#!/usr/bin/env python3
"""⟡query-topo — a topographic map of the query workload's column usage.

ELEVATION  = breadth: how many interned query builders touch a column (query_registry already ranks this).
CONTOURS   = co-usage clustering: which columns are used TOGETHER, within one table, in one query.

WHY CONTOURS AND NOT JUST ELEVATION
  Breadth alone tells you WHICH columns deserve an index; it cannot tell you what a COMPOSITE index should
  contain, because that depends on which columns co-occur in the same query. A composite index (a,b) only
  pays when a and b are used together — and a COVERING index additionally needs the query's projected
  columns from that table. So the contour (the co-usage group), not the peak, is the unit of index design.

  This is the workload-derived generalisation of the per-access-path index design done by hand for the
  ⟡demand-projection read-model (where ix_uri_u(u,r) / ix_uri_r(r,u) were chosen from 5 known access paths).

METHOD (reuse, not new machinery)
  query_registry.build_corpus() interns every builder as a query Unit over jea_pyalg.Intern; Column nodes
  carry `table.column`; Compare children are the predicate (index-relevant) columns. From one interned
  corpus we read: per-query column sets, predicate vs projection role, and same-table co-occurrence.

HONEST BOUNDARIES
  - Covers the INTERNED builder corpus (query_registry.BUILDERS), not every SQL ever run. Coverage is
    printed; an incomplete census is not a low count.
  - Co-occurrence is per-QUERY, not per-execution: it weights a rare query the same as a hot one. Frequency
    weighting needs execution counts the corpus does not carry.
  - "no composite index" is checked against catalog.db's live index list (first two columns), best-effort.
  - A contour is a CANDIDATE, still gated on selectivity and join direction (query_registry._roles).
"""
import os, sys, itertools, collections, sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "jea", "metalanguage"))
import query_registry as QR                                   # REUSE: corpus, ClauseLowerer, roles

CATALOG = os.path.join(os.path.dirname(HERE), "catalog", "catalog.db")


def column_sets(C):
    """[(query_name, all_cols, predicate_cols)] — one entry per interned builder."""
    preds = QR._predicate_columns(C)
    out = []
    for u in C.units:
        allc, prd = set(), set()
        for nid in u.support:
            n = C.I.nodes[nid]
            if n.kind == "Column" and n.op:
                allc.add(n.op)
                if nid in preds:
                    prd.add(n.op)
        if allc:
            out.append((u.name, allc, prd))
    return out


def live_composites():
    """({table: [(col1, col2, idxname)]}, {table.column PKs}) — existing multi-column prefixes, and PKs.

    MEASURED CORRECTION: a PK predicate on a rowid table is ALREADY served — projecting another column is a
    cheap rowid lookup, and SQLite will not switch to a hand-made (pk, other) covering index. Validated on a
    24,300-row path_text replica: adding (path_id, text) changed neither the plan nor the time (61 ms both),
    for 2.9 MB of index. So PK-predicate contours must NOT be nominated as gaps — they are the schema's
    id-resolution joins, and they are already optimal."""
    out = collections.defaultdict(list)
    pks = set()
    if not os.path.exists(CATALOG):
        return out, pks
    con = sqlite3.connect(f"file:{CATALOG}?mode=ro", uri=True)
    for (tbl,) in con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')"):
        try:
            for r in con.execute(f"PRAGMA table_info({tbl})"):
                if r[5]:
                    pks.add(f"{tbl}.{r[1]}")
            for idx in con.execute(f"PRAGMA index_list({tbl})"):
                info = [r[2] for r in con.execute(f"PRAGMA index_info({idx[1]})")]
                if len(info) >= 2:
                    out[tbl].append((info[0], info[1], idx[1]))
                elif len(info) == 1 and idx[2]:            # UNIQUE single-col == a key seek
                    pks.add(f"{tbl}.{info[0]}")
        except sqlite3.OperationalError:
            pass
    con.close()
    return out, pks


def main(argv):
    top = int(argv[argv.index("--top") + 1]) if "--top" in argv else 18
    C = QR.build_corpus()
    qs = column_sets(C)
    print(f"⟡query-topo — {len(qs)} interned query builders, {C.I.size()} interned nodes\n")

    # ── ELEVATION ────────────────────────────────────────────────────────────
    elev = collections.Counter()
    pelev = collections.Counter()
    for _, allc, prd in qs:
        for c in allc:
            elev[c] += 1
        for c in prd:
            pelev[c] += 1
    print("ELEVATION — columns by breadth (queries touching them); (P)=used as a predicate")
    print(f"  {'all':>4} {'pred':>5}  column")
    for c, n in elev.most_common(top):
        print(f"  {n:>4} {pelev.get(c,0):>5}  {c}{'  (P)' if pelev.get(c) else ''}")

    # ── CONTOURS ─────────────────────────────────────────────────────────────
    co = collections.Counter()          # same-table column pairs co-occurring in a query
    cover = collections.Counter()       # (pred, projected) same-table pairs -> covering-index candidates
    for _, allc, prd in qs:
        bytbl = collections.defaultdict(set)
        for c in allc:
            bytbl[c.split(".")[0]].add(c)
        for tbl, cols in bytbl.items():
            for a, b in itertools.combinations(sorted(cols), 2):
                co[(a, b)] += 1
            for p in (prd & cols):
                for q in cols - {p}:
                    cover[(p, q)] += 1

    live, pks = live_composites()
    def has_idx(a, b):
        t = a.split(".")[0]
        ac, bc = a.split(".")[-1], b.split(".")[-1]
        for c1, c2, _ in live.get(t, []):
            if {c1, c2} == {ac, bc}:
                return True
        return False

    print(f"\nCONTOURS — same-table column pairs co-occurring in a query (composite-index unit)")
    print(f"  {'n':>3}  {'idx?':<5} pair")
    shown = 0
    for (a, b), n in co.most_common():
        if shown >= top:
            break
        print(f"  {n:>3}  {'YES' if has_idx(a,b) else '--':<5} {a} + {b}")
        shown += 1

    gaps = [((a, b), n) for (a, b), n in cover.most_common()
            if not has_idx(a, b) and pelev.get(a) and a not in pks]   # PK predicates are already served
    served = [((a, b), n) for (a, b), n in cover.most_common() if a in pks]
    print(f"\n  ({len(served)} contours suppressed: predicate is a PK/UNIQUE key — already served, measured)")
    print(f"\nGAPS — co-occurring pairs, PREDICATE not a key, NO composite index (ranked candidates)")
    print(f"  {'n':>3}  predicate  +  co-used column")
    if not gaps:
        print("   (none — every predicate co-usage is already covered)")
    for (a, b), n in gaps[:top]:
        print(f"  {n:>3}  {a}  +  {b}")

    ntbl = len({c.split('.')[0] for c in elev})
    print(f"\ncoverage: {len(qs)} builders, {len(elev)} distinct columns, {ntbl} tables/views, "
          f"{len(co)} co-usage pairs, {len(gaps)} un-indexed predicate contours")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
