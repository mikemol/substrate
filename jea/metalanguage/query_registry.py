#!/usr/bin/env python3
"""query_registry.py — ⟡query-sppf-intern (first milestone): intern the project's SQLAlchemy-Core query
workload into the SPPF via the SAME interner that interns .py / .agdai (jea_pyalg.Intern, children-as-ids),
then read a join/filter predicate's sharing-BREADTH (node_units / fanin) as its INDEX PRIORITY.

NOT new machinery: the interner + its breadth readouts already exist (jea_pyalg.Intern.fanin,
jea_pysim.Corpus.node_units / extract_candidates). The only additions here are a ClauseLowerer — a THIRD
front-end beside jea_pyalg's Lowerer (Python AST) and CstLowerer (libcst) — that walks a SQLAlchemy
Select/ClauseElement into IR, and a ~6-line unit-register helper mirroring jea_pysim.add_file:121-128.

Reshaping discovery: the `path_text.path_id` breadth signal lives in the node/unit VIEW DEFINITIONS, not the
ad-hoc queries, so this first milestone points the lowerer at the view-def SELECTs + the existing Core sites
(where the join predicates are). GROUND TRUTH: `path_text.path_id` — the join key of the GROUP_CONCAT
`path_text` view, hand-fixed to a PK-indexed table on 2026-07-13 — is the validated indexed key
(i.e. the tool would have surfaced exactly that index). The broad ad-hoc raw→Core migration for fuller
coverage is the separate follow-on ⟡query-rawtocore-migration.

⟡index-weight-by-cost: breadth alone OVER-nominates. A join key is weighted by DIRECTION — an unindexed
column whose join-counterpart is ALREADY indexed is a PROBE-source: the planner SCANs its table and seeks
the indexed counterpart, so an index on the probe column is IGNORED (measured empirically on _unit.name_pid
/ event.ctor_id / _node.op_path_id — ⟡investigate-surfaced-candidates). `_roles` demotes those out of the
recommendation list; genuine candidates are unindexed columns on the SEEK side (value filter, or joined to
an unindexed column), still gated on selectivity / join-target cost. Direction needs the live index set
(catalog.db); render-table keys are accurate only against a db built with the reuse-catalog tables.
"""
import sys, os, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from jea_pyalg import IR
from jea_pysim import Corpus, Unit
from sqlalchemy import MetaData, Table, Column, String, select

# ── lightweight (reflection-free) Tables: we intern query STRUCTURE, never execute — no DB needed ──
_MD = MetaData()
def _T(name, *cols): return Table(name, _MD, *[Column(c, String) for c in cols])
path_text  = _T("path_text", "path_id", "text")
_unit      = _T("_unit", "unit_id", "name_pid", "root_id", "file_id", "kind_id", "module_pid", "root_lid", "copy")
_node      = _T("_node", "node_id", "sym", "kind_id", "role_id", "op_term_id", "op_path_id", "lit_id")
terms      = _T("terms", "term_id", "text")
unit_node  = _T("unit_node", "unit_id", "node_id")
node_child = _T("node_child", "node_id", "ord", "child_id")
obs        = _T("obs", "core_id", "local_id", "ekey")
event      = _T("event", "ekey", "ctor_id", "qname_pid", "idx")
edge       = _T("edge", "core_id", "plid", "ord", "clid")

# ── the query workload as named build-only Core select()s ──────────────────────────────────────────
# The node/unit VIEW-definition SELECTs (where path_text.path_id is joined) + the existing Core sites
# (graded_orbit.preload_cores / unit_index, autocorr_synth). Each is the STRUCTURE only.
def q_node_view():          # sppf_db `node` view: joins path_text on op_path_id
    return (select(_node.c.node_id, terms.c.text, path_text.c.text)
            .select_from(_node.join(terms, terms.c.term_id == _node.c.kind_id)
                              .outerjoin(path_text, path_text.c.path_id == _node.c.op_path_id)))
def q_unit_view():          # sppf_db `unit` view: joins path_text on name_pid
    return (select(_unit.c.unit_id, path_text.c.text, terms.c.text)
            .select_from(_unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)
                              .join(terms, terms.c.term_id == _unit.c.file_id)))
def q_unit_index():         # graded_orbit.unit_index
    return (select(path_text.c.text, _unit.c.file_id, _unit.c.root_lid)
            .select_from(_unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)))
def q_preload_nodes():      # graded_orbit.preload_cores node scan
    return (select(obs.c.core_id, obs.c.local_id, terms.c.text, path_text.c.text, event.c.idx)
            .select_from(obs.join(event, event.c.ekey == obs.c.ekey)
                            .join(terms, terms.c.term_id == event.c.ctor_id)
                            .outerjoin(path_text, path_text.c.path_id == event.c.qname_pid)))
def q_argperm_uid():        # sppf_db.project_argperm's uid map
    return (select(_unit.c.unit_id, path_text.c.text)
            .select_from(_unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)))
def q_orbit_def_join():     # graded_orbit.orbit_cosets / cosets_view: _orbit_def → _unit → path_text
    return (select(path_text.c.text, _unit.c.unit_id)
            .select_from(_unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)))
def q_reuse_unit_name():    # reuse_tui / reuse_catalog compat: unit name via path_text
    return (select(_unit.c.unit_id, path_text.c.text)
            .select_from(_unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)))
def q_autocorr_dupsig():    # autocorr_synth dup-signature: unit_node self-join (NO path_text — a control)
    a = unit_node.alias("a"); b = unit_node.alias("b")
    return (select(a.c.unit_id, b.c.unit_id)
            .select_from(a.join(b, a.c.node_id == b.c.node_id)))
def q_reuse_nodechild():    # a reuse query over node_child (NO path_text — a control)
    return (select(unit_node.c.unit_id, node_child.c.child_id)
            .select_from(unit_node.join(node_child, node_child.c.node_id == unit_node.c.node_id)))

BUILDERS = {
    "node_view": q_node_view, "unit_view": q_unit_view, "unit_index": q_unit_index,
    "preload_nodes": q_preload_nodes, "argperm_uid": q_argperm_uid, "orbit_def_join": q_orbit_def_join,
    "reuse_unit_name": q_reuse_unit_name, "autocorr_dupsig": q_autocorr_dupsig, "reuse_nodechild": q_reuse_nodechild,
}
# ⟡query-rawtocore-migration: the migrated ad-hoc queries (single source in query_builders) are interned
# here too — one builder is BOTH executed (via query_builders.run at the call site) AND interned for breadth.
from query_defs import INTERN_BUILDERS as _QB_BUILDERS   # the builder OBJECTS (⟡qinfra: compiler, not runtime)
BUILDERS.update({f"qb.{k}": v for k, v in _QB_BUILDERS.items()})

# ── ClauseLowerer: SQLAlchemy Select/ClauseElement → IR, bottom-up, interned into Corpus.I ─────────
class ClauseLowerer:
    """A third front-end beside jea_pyalg.Lowerer/CstLowerer. Head ‖ children, children-as-interned-ids —
    a Column's referential identity ('table.col') sits in `op` exactly like a free Name/Attribute; a Join /
    Compare wraps its parts as children. The interner content-addresses the shared structure; a predicate
    node (Compare over two Columns) shared across queries gets fanin/node_units breadth for free."""
    def __init__(self, I): self.I = I

    @staticmethod
    def _base_table(tbl):
        """resolve an Alias to its underlying Table name — an index recommendation must target the REAL
        table (unit_node), not a query-local alias (a/b), so aliased columns aggregate breadth correctly."""
        return getattr(getattr(tbl, "element", tbl), "name", getattr(tbl, "name", "?"))

    def lower(self, el):
        cn = el.__class__.__name__
        # Column (has a table + name) → the referential identity in op
        tbl = getattr(el, "table", None)
        if tbl is not None and hasattr(el, "name") and cn in ("Column",):
            return self.I.intern(IR(kind="Column", op=f"{self._base_table(tbl)}.{el.name}"))
        if cn == "Table":
            return self.I.intern(IR(kind="Table", op=el.name))
        if cn == "Join":
            op = "outer" if getattr(el, "isouter", False) else "inner"
            kids = (self.lower(el.left), self.lower(el.right), self.lower(el.onclause))
            return self.I.intern(IR(kind="Join", op=op, children=kids))
        if cn in ("BinaryExpression",):
            opn = getattr(getattr(el, "operator", None), "__name__", str(getattr(el, "operator", "")))
            return self.I.intern(IR(kind="Compare", op=opn,
                                    children=(self.lower(el.left), self.lower(el.right))))
        if cn in ("BooleanClauseList", "ClauseList"):          # AND/OR of predicates
            opn = getattr(getattr(el, "operator", None), "__name__", "and_")
            return self.I.intern(IR(kind="Bool", op=opn, children=tuple(self.lower(c) for c in el.clauses)))
        if hasattr(el, "get_final_froms"):                     # a Select
            kids = [self.lower(c) for c in el.selected_columns]
            kids += [self.lower(f) for f in el.get_final_froms()]
            if el.whereclause is not None:
                kids.append(self.lower(el.whereclause))
            return self.I.intern(IR(kind="Select", children=tuple(kids)))
        # leaf fallback (alias-wrapped column, bindparam, literal, …): keep a stable op where possible
        if tbl is not None and hasattr(el, "name"):
            return self.I.intern(IR(kind="Column", op=f"{self._base_table(tbl)}.{el.name}"))
        return self.I.intern(IR(kind=cn, op=str(getattr(el, "key", "") or getattr(el, "value", "") or "")))


def build_corpus(builders=BUILDERS):
    """Intern every builder as a query Unit (mirrors jea_pysim.add_file:121-128 register shape)."""
    C = Corpus(); lw = ClauseLowerer(C.I)
    for name, fn in builders.items():
        root = lw.lower(fn())
        sup = C._support(root)
        C.units.append(Unit(name=name, path="query", lineno=-1, root=root, support=sup,
                            depth=C._depth_map(root)))
        uidx = len(C.units) - 1
        for nid in sup:
            C.node_units.setdefault(nid, set()).add(uidx)
    return C


def _predicate_columns(C):
    """column node-ids that appear as a child of a Compare (join onclause / filter) — the index candidates
    (a projected-only column is not one). Returns {col_nid}."""
    preds = set()
    for nid in range(C.I.size()):
        n = C.I.nodes[nid]
        if n.kind == "Compare":
            for c in n.children:
                if C.I.nodes[c].kind == "Column":
                    preds.add(c)
    return preds


def _live_indexed(colops):
    """best-effort: which 'table.column' predicate keys are ALREADY covered by an index in catalog.db
    (PK or any index's first column). Annotation only; absent DB → empty."""
    import sqlite3
    db = os.path.join(os.path.dirname(os.path.dirname(HERE)), "catalog", "catalog.db")
    covered = set()
    if not os.path.exists(db): return covered
    con = sqlite3.connect(db)
    for tbl in {op.split(".")[0] for op in colops}:
        try:
            for r in con.execute(f"PRAGMA table_info({tbl})"):
                if r[5]:                                        # pk flag
                    covered.add(f"{tbl}.{r[1]}")
            for idx in con.execute(f"PRAGMA index_list({tbl})"):
                info = list(con.execute(f"PRAGMA index_info({idx[1]})"))
                if info: covered.add(f"{tbl}.{info[0][2]}")     # first indexed column
        except sqlite3.OperationalError:
            pass
    con.close(); return covered


def _join_pairs(C):
    """From each Compare node, the columns it relates: (colA_nid, colB_nid) for a join equality between two
    columns, or (col_nid, None) for a filter equality (column vs bindparam/literal). Direction is read off
    these pairs (⟡investigate-surfaced-candidates: an unindexed column whose join-counterpart is ALREADY
    indexed is a PROBE-source — the planner drives on it via a full SCAN and seeks the counterpart, so an
    index here is IGNORED; measured empirically on _unit.name_pid / event.ctor_id / _node.op_path_id)."""
    _NULLCHECK = {"is_", "is_not", "isnot", "isnull", "is_null", "notnull"}  # IS [NOT] NULL — no plain-index seek
    pairs = []
    for nid in range(C.I.size()):
        n = C.I.nodes[nid]
        if n.kind != "Compare": continue
        cols = [c for c in n.children if C.I.nodes[c].kind == "Column"]
        if len(cols) == 2:                                     # a join equality (col == col)
            pairs.append((cols[0], cols[1]))
        elif len(cols) == 1 and n.op not in _NULLCHECK:        # a VALUE filter (eq/range/in/like) — index-servable;
            pairs.append((cols[0], None))                      # a null-check is NOT (a probe column's incidental filter)
    return pairs


def _roles(C, covered):
    """Classify each predicate-column op → 'indexed' | 'probe' | 'candidate' by join DIRECTION (not breadth):
    - indexed  : already covered by a PK/index (a validated key, e.g. the hand-done path_text.path_id).
    - probe    : unindexed, but in EVERY join it participates in the counterpart is already indexed — the
                 planner SCANs this column's table and seeks the counterpart, so an index here is ignored.
    - candidate: unindexed AND (a filter target, OR joined to an UNINDEXED column) — a genuine seek an index
                 could serve; still gated on selectivity / join-target cost before adding."""
    op = lambda nid: C.I.nodes[nid].op
    cps = {}                                                   # colop -> list of counterpart ops (None=filter)
    for a, b in _join_pairs(C):
        cps.setdefault(op(a), []).append(op(b) if b is not None else None)
        if b is not None: cps.setdefault(op(b), []).append(op(a))
    roles = {}
    for colop, cc in cps.items():
        if colop in covered: roles[colop] = "indexed"; continue
        has_filter = any(c is None for c in cc)
        joins = [c for c in cc if c is not None]
        roles[colop] = "candidate" if (has_filter or any(c not in covered for c in joins)) else "probe"
    return roles


def _filter_cols(C):
    """predicate-column ops that appear as a VALUE filter (col op value) — the selectivity-relevant ones
    (a join column's index utility is about direction, not cardinality)."""
    op = lambda nid: C.I.nodes[nid].op
    return {op(a) for a, b in _join_pairs(C) if b is None}


def _selectivity(cols, cap=2_000_000):
    """⟡index-selectivity-weight: for each BASE-table 'table.col', (n_distinct, n_rows) via a guarded
    COUNT(DISTINCT)/COUNT(*). Skips VIEWs (can't be indexed; probing one may materialize it — that's the
    separate ⟡resolve-view-columns) and tables above `cap` rows (n_distinct=None = 'too big to probe cheaply,
    left as a candidate'). Absent DB → {}. Only the columns already role='candidate' & filter-driven are passed
    in, so this runs a handful of cheap COUNTs, never a scan of event/obs/edge."""
    import sqlite3
    db = os.path.join(os.path.dirname(os.path.dirname(HERE)), "catalog", "catalog.db")
    out = {}
    if not os.path.exists(db): return out
    con = sqlite3.connect(db)
    kinds = {r[0]: r[1] for r in con.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view')")}
    for colop in cols:
        tbl, _, col = colop.partition(".")
        if kinds.get(tbl) != "table": continue                 # view / absent → not a base-table index target
        try:
            nrows = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            if nrows > cap: out[colop] = (None, nrows); continue
            out[colop] = (con.execute(f"SELECT COUNT(DISTINCT {col}) FROM {tbl}").fetchone()[0], nrows)
        except sqlite3.OperationalError:
            pass
    con.close(); return out


_MIN_ROWS     = 1000    # a table below this is scanned instantly — an index is moot
_MIN_DISTINCT = 25      # a typical equality match ≈ 1/n_distinct of rows (uniform est.); <25 → >4%/value, a
                        # b-tree seek isn't worth it (⟡investigate-surfaced-candidates: _unit.copy = 2 distinct)
def index_report(C):
    preds = _predicate_columns(C)
    colops = {C.I.nodes[nid].op for nid in preds}
    covered = _live_indexed(colops)
    roles = _roles(C, covered)
    fcols = _filter_cols(C)
    sel = _selectivity({op for op in colops if roles.get(op) == "candidate" and op in fcols})
    rows = []
    for nid in preds:
        op = C.I.nodes[nid].op; role = roles.get(op, "candidate"); note = ""
        if role == "candidate" and op in sel:                  # base-table VALUE filter → weigh cardinality
            nd, nr = sel[op]
            if nd is None:           note = f"{nr} rows — too big to probe"
            elif nr < _MIN_ROWS:     role, note = "low-selectivity", f"{nr}-row table (index moot)"
            elif nd < _MIN_DISTINCT: role, note = "low-selectivity", f"{nd} distinct / {nr} rows (~{nr // max(nd, 1)}/value)"
            else:                    note = f"{nd} distinct / {nr} rows (selective)"
        rows.append((len(C.node_units.get(nid, ())), op, role, note))   # (breadth, colop, role, note)
    _rank = {"candidate": 0, "indexed": 1, "low-selectivity": 2, "probe": 3}   # actionable → validated → demoted
    rows.sort(key=lambda r: (_rank[r[2]], -r[0], r[1]))
    return rows


_ROLE_LABEL = {"indexed": "indexed (validated)",
               "probe":   "probe-source — index IGNORED (counterpart indexed)",
               "low-selectivity": "low-selectivity — index won't help (demoted)",
               "candidate": "CANDIDATE (seek)"}
def _print_report(C):
    rows = index_report(C)
    print(f"⟡index-weight-by-cost — breadth × join-DIRECTION × selectivity over {len(C.units)} interned "
          f"query builders, {C.I.size()} interned nodes\n")
    print("  breadth  join/filter-predicate key         role / note")
    print("  -------  --------------------------------  -----------")
    for breadth, op, role, note in rows:
        lab = _ROLE_LABEL[role] + (f"  [{note}]" if note else "")
        print(f"  {breadth:>5}    {op:<32}  {lab}")
    cands  = [(b, op, note) for b, op, role, note in rows if role == "candidate"]
    idxd   = [op for _, op, role, _ in rows if role == "indexed"]
    probes = [op for _, op, role, _ in rows if role == "probe"]
    lowsel = [op for _, op, role, _ in rows if role == "low-selectivity"]
    print(f"\n  → {len(cands)} genuine NOT-INDEXED candidate(s) after DIRECTION × SELECTIVITY weighting; "
          f"{len(probes)} probe-source(s) + {len(lowsel)} low-selectivity DEMOTED "
          f"(⟡investigate-surfaced-candidates: neither a full-scan probe column nor a low-cardinality filter "
          f"gets used by the planner — measured).")
    print(f"     validated indexes: {', '.join(idxd) or '(none)'}")
    if probes: print(f"     demoted probe-sources: {', '.join(probes)}")
    if lowsel: print(f"     demoted low-selectivity filters: {', '.join(lowsel)}")
    if cands:
        print("     candidates (rank by breadth; base-table filters carry measured selectivity):")
        for b, op, note in cands: print(f"       breadth {b:>2}  {op:<28}{('  '+note) if note else '  (view / absent-in-this-db — resolve to base: ⟡resolve-view-columns)'}")
    print(f"  COVERAGE: view-def + Core builders (the signal-carrying set); ⟡query-rawtocore-migration widened it.")


def selftest():
    C = build_corpus()
    rows = index_report(C)
    assert rows, "index report must have predicate columns"
    role = {op: r for _, op, r, _ in rows}
    breadth = {op: b for b, op, _, _ in rows}
    # ground truth 1: path_text.path_id is the validated indexed key, shared across many builders.
    assert role.get("path_text.path_id") == "indexed", \
        f"path_text.path_id must be 'indexed' (validated), got {role.get('path_text.path_id')}"
    assert breadth["path_text.path_id"] >= 2, "path_text.path_id must be shared across ≥2 builders"
    # ground truth 2 (⟡investigate-surfaced-candidates): the high-breadth NOT-INDEXED probe-sources and the
    # low-cardinality filter are DEMOTED — an index on them is ignored (measured). DIRECTION classifies the
    # probe-sources 'probe'; SELECTIVITY classifies _unit.copy (2 distinct / 18269) 'low-selectivity'. Both
    # must be EXCLUDED from recommendations. (Skipped if catalog.db absent — needs the live index set + rows.)
    if role.get("path_text.path_id") == "indexed":
        cands = {op for _, op, r, _ in rows if r == "candidate"}
        for spurious in ("_unit.name_pid", "event.ctor_id", "_node.op_path_id"):
            assert role.get(spurious) == "probe", \
                f"{spurious} must be demoted to 'probe' (counterpart indexed), got {role.get(spurious)}"
            assert spurious not in cands, f"{spurious} (probe-source) must not appear as a candidate"
        assert role.get("_unit.copy") == "low-selectivity", \
            f"_unit.copy (2 distinct / 18269 rows) must be demoted to 'low-selectivity', got {role.get('_unit.copy')}"
        assert "_unit.copy" not in cands, "_unit.copy (low-selectivity) must not appear as a candidate"
    print("PASS ⟡index-weight-by-cost selftest:")
    print(f"  path_text.path_id = validated indexed key (breadth {breadth['path_text.path_id']}); the "
          f"high-breadth probe-sources (_unit.name_pid, event.ctor_id, _node.op_path_id) are DEMOTED by "
          f"DIRECTION and _unit.copy by SELECTIVITY (2 distinct) — all excluded from recommendations, "
          f"reproducing the ⟡investigate-surfaced-candidates measurement by construction.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index-report", action="store_true",
                    help="rank join/filter predicate keys by breadth × join-DIRECTION (probe-sources demoted)")
    ap.add_argument("--selftest", action="store_true",
                    help="ground-truth: path_text.path_id validated-indexed; measured probe-sources demoted")
    a = ap.parse_args()
    if a.selftest: selftest(); return
    _print_report(build_corpus())


if __name__ == "__main__":
    main()
