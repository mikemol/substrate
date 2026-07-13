#!/usr/bin/env python3
"""autocorr_synth.py — ⟡autocorr-synth: MECHANICAL consolidation synthesis via anti-unification.

The reuse tooling RANKS parameterization targets (reuse_tui's κ/σ/V₄ frame); this DISCHARGES one — it
synthesizes the abstraction + the per-instance substitutions with NO LLM in the loop, by reusing the
existing anti-unifier `jea_extrude_ir.templatize`:

  a cluster of ≥2 units sharing one SKELETON (structure + ops + referential names) is a template;
  the residue positions that VARY across instances are the HOLES (parameters, Free⊣Forgetful
  substitution), those constant are baked in. templatize returns the template source + each instance's
  hole-fillings. That IS the consolidation: extract the template, apply each filling.

The AUTOCORRELATION is the signal that a cluster is worth it: a genuine target is N near-identical
copies that autocorrelate at zero lag (same skeleton) with a thin varying residue. We score each cluster
  score = instances × (1 − hole_density)      hole_density = holes / (holes + baked residue slots)
so many-instances / few-holes (high self-correlation) leads — the mechanically-extractable wins.

Two corpora. PYTHON (templatize, ast-based) closes fully: same-skeleton clusters → template + hole
fillings, compiling Python. AGDA (--agda) is SQL-NATIVE over catalog.db via SQLAlchemy Core — we do NOT
walk the SPPF in Python (that reinvents a query engine; it timed out). Profiling showed load is ~2.7s
(SQLite is not the bottleneck), and the projection ALREADY enumerated each unit's node-membership into
`unit_node`, so exact-body identity is a GROUP BY over the unit_node SET-signature (declarative, ~4s), and
near-dups-with-holes are a unit_node self-join + set-difference — JOINs and constraints, never a recursive
walk. (⟡autocorr-synth-agda-holes = the holes rung.)

  autocorr_synth.py [--min-instances 2] [--top 12] [PATHS...]   # Python corpus: template + fillings
  autocorr_synth.py --emit <cluster-id>                          # its full template + all substitutions
  autocorr_synth.py --agda [FILTER] [--emit <#>]                 # Agda SPPF: exact-body (CSE) clusters
"""
import sys, os, ast, argparse, glob

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import jea_extrude_ir as E
import graded_orbit                                   # ⟡cosets-into-autocorr: the coset/residue reader


def functions(paths):
    """(label, source) for every top-level def/async-def in the corpus — the units to anti-unify."""
    out = []
    for p in paths:
        try:
            src = open(p, encoding="utf-8").read(); tree = ast.parse(src)
        except (OSError, SyntaxError):
            continue
        lines = src.splitlines()
        rel = os.path.relpath(p, REPO)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                seg = ast.get_source_segment(src, node)
                if seg and seg.count("\n") >= 1:                 # skip one-liners (no residue to align)
                    out.append((f"{rel}::{node.name}", seg + "\n"))
    return out


# ─────────────────────────────── the AGDA path: SQL-native over the SPPF (SQLAlchemy Core) ──────────
# The projection is CONTENT-ADDRESSED (node_id = hash of head+children), so we do NOT walk the graph in
# Python (that reinvents a query engine — it timed out). We push the work into SQL over catalog.db via
# SQLAlchemy Core. The projection ALREADY enumerated each unit's node-membership into `unit_node`, so we
# think in JOINs + declarative constraints over that materialized enumeration — NOT recursive-imperative
# walks. Size = GROUP BY over unit_node (count the done enumeration). Exact-body dup = GROUP BY the
# unit_node SET-signature (root_id is only a depth-1 packing — it false-clusters). Near-dup = a SELF-JOIN
# on unit_node (shared node-count); holes = the set-difference.
CATALOG_DB = os.path.join(REPO, "catalog", "catalog.db")

def _engine():
    from sqlalchemy import create_engine
    if not os.path.exists(CATALOG_DB):
        sys.exit(f"\u27e1autocorr-synth-agda: no catalog.db at {CATALOG_DB} (python3 scripts/sppf_db.py \"\").")
    return create_engine(f"sqlite:///{os.path.abspath(CATALOG_DB)}")

def synth_agda(filt, min_instances):
    """SQL-NATIVE, declarative — keyed on the MATERIALIZED enumeration itself. Two units have an identical
    body ⟺ identical unit_node SET (root_id is only a depth-1 packing — it FALSE-clusters). So the exact
    key is a per-unit set-signature: group_concat(node_id ORDER BY node_id) over unit_node, then GROUP BY
    that signature — no walk, the projection already enumerated the membership. copy=0 keeps INDEPENDENT
    units (module-instantiation families are copy=1, already consolidated). size = |set|. Near-dup WITH
    holes is the same shape one step out — a unit_node SELF-JOIN for shared-node-count + a set-difference
    for the holes (\u27e1autocorr-synth-agda-holes)."""
    from sqlalchemy import MetaData, Table, select, func, and_
    from collections import defaultdict
    eng = _engine(); md = MetaData()
    unit = Table("_unit", md, autoload_with=eng)
    ptv = Table("path_text", md, autoload_with=eng)
    un = Table("unit_node", md, autoload_with=eng)
    with eng.connect() as conn:
        # per-unit set-signature over the ordered membership (order-independent body identity) + its size.
        ordered = select(un.c.unit_id, un.c.node_id).order_by(un.c.unit_id, un.c.node_id).subquery()
        sig = (select(ordered.c.unit_id.label("uid"),
                      func.group_concat(ordered.c.node_id).label("s"), func.count().label("sz"))
               .group_by(ordered.c.unit_id)).subquery()
        base = (sig.join(unit, unit.c.unit_id == sig.c.uid)
                   .join(ptv, ptv.c.path_id == unit.c.name_pid))
        dupsig = (select(sig.c.s).select_from(sig.join(unit, unit.c.unit_id == sig.c.uid))
                  .where(unit.c.copy == 0).group_by(sig.c.s).having(func.count() >= min_instances)).subquery()
        q = (select(sig.c.s, ptv.c.text, sig.c.sz).select_from(base)
             .where(and_(unit.c.copy == 0, sig.c.s.in_(select(dupsig.c.s)))))
        by_sig, sz = defaultdict(list), {}
        for s, name, size in conn.execute(q):
            if not filt or filt in (name or ""):
                by_sig[s].append(name); sz[s] = size
        clusters = sorted(((s, sorted(ns)) for s, ns in by_sig.items() if len(ns) >= min_instances),
                          key=lambda sn: -(len(sn[1]) * (sz.get(sn[0]) or 1)))   # rank by instances × body size
        return [{"n": len(ns), "size": sz.get(s), "labels": ns} for s, ns in clusters]


def synth_agda_holes(filt, min_instances, sim=0.6, bucket_cap=60):
    """Near-dup (WITH-holes) targets, declaratively. A parameterization target is N units sharing a large
    common subtree (the abstraction) and differing at a few nodes (the holes = the per-instance
    substitution). Candidate pairs are bounded to the same (root_id, size) BUCKET first (near-dups have
    equal size — a hole swaps a subtree, it doesn't add nodes to only one side of the bucket), skipping
    giant buckets LOUDLY (no silent truncation); within-bucket the overlap is a unit_node SELF-JOIN and the
    holes are the set-difference (NOT EXISTS) — JOINs + constraints, no walk."""
    from sqlalchemy import MetaData, Table, select, func, and_
    from collections import defaultdict
    eng = _engine(); md = MetaData()
    unit = Table("_unit", md, autoload_with=eng)
    un = Table("unit_node", md, autoload_with=eng)
    with eng.connect() as conn:
        sz = select(un.c.unit_id, func.count().label("n")).group_by(un.c.unit_id).subquery()
        # buckets = (root_id, size) among independent units; keep 2..bucket_cap (skip the giant ones LOUD)
        bexpr = (select(unit.c.root_id, sz.c.n, func.count().label("k"))
                 .select_from(unit.join(sz, sz.c.unit_id == unit.c.unit_id)).where(unit.c.copy == 0)
                 .group_by(unit.c.root_id, sz.c.n))
        buckets = conn.execute(bexpr.having(func.count() >= min_instances)).all()
        keep = [(r, n) for r, n, k in buckets if k <= bucket_cap]
        skipped = [(r, n, k) for r, n, k in buckets if k > bucket_cap]
        if skipped:
            tot = sum(k for _, _, k in skipped)
            print(f"  \u26a0 skipped {len(skipped)} bucket(s) with > {bucket_cap} units ({tot} units) — "
                  f"too big to pairwise self-join; raise --bucket-cap to include (biggest {max(k for *_ ,k in skipped)}).",
                  file=sys.stderr)
        if not keep: return []
        # eligible units = those in a kept bucket
        elig = (select(unit.c.unit_id, unit.c.root_id, sz.c.n)
                .select_from(unit.join(sz, sz.c.unit_id == unit.c.unit_id)).where(unit.c.copy == 0)).subquery()
        keepset = set(keep)
        rows = [r for r in conn.execute(select(elig.c.unit_id, elig.c.root_id, elig.c.n))
                if (r[1], r[2]) in keepset]
        by_bucket = defaultdict(list)
        for uid, root, n in rows:
            by_bucket[(root, n)].append(uid)
        # within each small bucket, cluster by pairwise overlap ≥ sim·n (connected components)
        out = []
        uid2name = {}
        for (root, n), uids in by_bucket.items():
            if len(uids) < min_instances: continue
            a = un.alias("a"); b = un.alias("b")
            pair = (select(a.c.unit_id, b.c.unit_id, func.count().label("sh"))
                    .select_from(a.join(b, and_(a.c.node_id == b.c.node_id, a.c.unit_id < b.c.unit_id)))
                    .where(and_(a.c.unit_id.in_(uids), b.c.unit_id.in_(uids)))
                    .group_by(a.c.unit_id, b.c.unit_id)
                    .having(and_(func.count() >= sim * n, func.count() < n)))
            adj = defaultdict(set)
            for x, y, sh in conn.execute(pair):
                adj[x].add(y); adj[y].add(x)
            seen = set()
            for u0 in list(adj):
                if u0 in seen: continue
                comp, stack = set(), [u0]
                while stack:
                    v = stack.pop()
                    if v in seen: continue
                    seen.add(v); comp.add(v); stack.extend(adj[v] - seen)
                if len(comp) >= min_instances:
                    out.append({"units": comp, "n": len(comp), "size": n, "root": root})
        # names + rank
        allu = set().union(*[c["units"] for c in out]) if out else set()
        if allu:
            ptv = Table("path_text", md, autoload_with=eng)
            nq = (select(unit.c.unit_id, ptv.c.text).select_from(
                    unit.join(ptv, ptv.c.path_id == unit.c.name_pid)).where(unit.c.unit_id.in_(allu)))
            uid2name = {u: nm for u, nm in conn.execute(nq)}
        res = []
        for c in out:
            names = sorted(uid2name.get(u, u) for u in c["units"])
            if filt and not any(filt in nm for nm in names): continue
            res.append({"n": c["n"], "size": c["size"], "labels": names, "uids": sorted(c["units"])})
        res.sort(key=lambda c: -(c["n"] * c["size"]))
        return res


def agda_holes_detail(uids):
    """The set-difference that IS the synthesis: the shared CORE (nodes in ALL units = the abstraction) vs
    each unit's HOLES (its nodes not in the core = its substitution), with the hole node HEADS. Declarative:
    core = GROUP BY node_id HAVING COUNT(DISTINCT unit)=|cluster|; holes = the complement per unit."""
    from sqlalchemy import MetaData, Table, select, func, and_, literal_column
    from collections import defaultdict
    eng = _engine(); md = MetaData()
    un = Table("unit_node", md, autoload_with=eng); node = Table("_node", md, autoload_with=eng)
    trm = Table("terms", md, autoload_with=eng); ptv = Table("path_text", md, autoload_with=eng)
    unit = Table("_unit", md, autoload_with=eng)
    with eng.connect() as conn:
        core = (select(un.c.node_id).where(un.c.unit_id.in_(uids))
                .group_by(un.c.node_id).having(func.count(func.distinct(un.c.unit_id)) == len(uids))).subquery()
        core_n = conn.execute(select(func.count()).select_from(core)).scalar()
        # per-unit hole node heads (nodes NOT in the shared core)
        t_op = trm.alias("o"); t_role = trm.alias("r"); pt2 = ptv.alias("pt"); ptn = ptv.alias("ptn")
        head = func.coalesce(func.nullif(pt2.c.text, ""), t_op.c.text, t_role.c.text, literal_column("'·'"))
        q = (select(ptn.c.text, head.label("h"))
             .select_from(un.join(node, node.c.node_id == un.c.node_id)
                          .join(unit, unit.c.unit_id == un.c.unit_id)
                          .join(ptn, ptn.c.path_id == unit.c.name_pid)
                          .outerjoin(pt2, pt2.c.path_id == node.c.op_path_id)
                          .outerjoin(t_op, t_op.c.term_id == node.c.op_term_id)
                          .outerjoin(t_role, t_role.c.term_id == node.c.role_id))
             .where(and_(un.c.unit_id.in_(uids), un.c.node_id.notin_(select(core.c.node_id)))))
        holes = defaultdict(list)
        for name, h in conn.execute(q):
            holes[name].append(h)
    return core_n, holes


def _density(cluster):
    """hole_density = holes / (holes + baked residue slots). Needs the template's baked count; approximate
    baked by the template body size in tokens minus holes (a proxy that ranks stably)."""
    holes = cluster["holes"]
    baked = max(1, cluster["template"].count("\n") + len(cluster["template"].split()) - holes)
    return holes / (holes + baked)


def synth(paths, min_instances):
    units = functions(paths)
    res = E.templatize(units)
    rows = []
    for c in res["clusters"]:
        n = len(c["labels"])
        if n < min_instances:
            continue
        dens = _density(c)
        rows.append({"n": n, "holes": c["holes"], "density": dens,
                     "score": n * (1 - dens), **c})
    rows.sort(key=lambda r: -r["score"])
    return rows, res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--min-instances", type=int, default=2)
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--emit", type=int, metavar="RANK", help="print the full template + fillings for a rank")
    ap.add_argument("--agda", nargs="?", const="", metavar="FILTER",
                    help="synth over the AGDA SPPF (catalog.db) instead of Python; optional qname filter")
    ap.add_argument("--holes", action="store_true", help="(with --agda) near-dup WITH-holes targets, not exact CSE")
    ap.add_argument("--bucket-cap", type=int, default=60, help="(--holes) max units per (root,size) bucket to self-join")
    args = ap.parse_args()
    if args.agda is not None and args.holes:
        rows = synth_agda_holes(args.agda, args.min_instances, bucket_cap=args.bucket_cap)
        print(f"⟡autocorr-synth-agda-holes: {len(rows)} near-dup (WITH-holes) parameterization targets"
              f"{f' (filter {args.agda!r})' if args.agda else ''} (≥{args.min_instances} units)\n")
        if args.emit is not None:
            c = rows[args.emit]
            core_n, holes = agda_holes_detail(c["uids"])
            print(f"# cluster #{args.emit}: {c['n']} near-identical units (~{c['size']}-node bodies).")
            print(f"## ABSTRACTION = the shared core: {core_n} nodes common to ALL {c['n']} units (extract this,")
            print(f"   with a hole per differing position). Each unit's HOLES (its substitution):")
            # ⟡cosets-into-autocorr: if the cluster's units carry graded-orbit cosets (_orbit_def), render
            # the holes as the WEDGE FORM `orbit-rep ∘ residue` — the residue a PROVEN adjacent-transposition
            # (sadj) word (coxeter-complete, 9dcdbb7) — instead of opaque token diffs.
            import sqlite3 as _sql
            _gc = _sql.connect(CATALOG_DB)
            cos = graded_orbit.orbit_cosets(_gc, unit_ids=c["uids"]); _gc.close()
            by_qn = {v["qname"]: v for v in cos.values()}
            if cos:
                keys = {v["graded_key"] for v in cos.values()}
                print(f"## GRADED-ORBIT: these units span {len(keys)} orbit-key(s); a permutation-cluster is "
                      f"ONE key whose members differ only by the residue coset (braiding word). Holes shown "
                      f"as `orbit-rep ∘ sadj-word` (|Stab| = symmetric-binder count).")
            for name in sorted(holes)[:20]:
                hs = holes[name]
                from collections import Counter
                top = ", ".join(f"{h}×{k}" if k > 1 else h for h, k in Counter(hs).most_common(6))
                cz = by_qn.get(name)
                coset = f"   ⊘ residue={cz['coxeter']} |Stab|={cz['stab']}" if cz else ""
                print(f"  - {name.split('.')[-1]:28s} {len(hs):>2} hole-nodes: {top}{coset}")
            if len(holes) > 20: print(f"  … (+{len(holes)-20})")
            return
        for i, c in enumerate(rows[:args.top]):
            print(f"  #{i:<2} ×{c['n']:<4} ~{c['size']:>4}-node bodies  eg {c['labels'][0]}")
        print(f"\n  → autocorr_synth.py --agda --holes --emit <#> for the cluster.")
        return
    if args.agda is not None:
        rows = synth_agda(args.agda, args.min_instances)
        print(f"⟡autocorr-synth-agda (SQL-native): {len(rows)} exact-body (0-hole/CSE) clusters over the SPPF"
              f"{f' (filter {args.agda!r})' if args.agda else ''} (≥{args.min_instances} instances)\n")
        if args.emit is not None:
            c = rows[args.emit]
            print(f"# cluster #{args.emit}: {c['n']} independent units, IDENTICAL body "
                  f"({c['size']} distinct nodes) — 0 holes = pure CSE.")
            print(f"## consolidation: extract ONE def with this body, reference it from the other {c['n']-1}.")
            print("## units:")
            for name in c["labels"][:40]:
                print(f"  - {name}")
            if c["n"] > 40: print(f"  … (+{c['n']-40})")
            return
        for i, c in enumerate(rows[:args.top]):
            print(f"  #{i:<2} ×{c['n']:<4} {c['size']:>4}-node identical body  eg {c['labels'][0]}")
        print(f"\n  → autocorr_synth.py --agda --emit <#> for the full cluster + the consolidation.")
        print(f"  (near-dups WITH holes = a unit_node self-join + set-difference — ⟡autocorr-synth-agda-holes)")
        return
    paths = args.paths or (glob.glob(os.path.join(HERE, "*.py")) +
                           glob.glob(os.path.join(REPO, "scripts", "*.py")))
    paths = [p for p in paths if not p.endswith("autocorr_synth.py")]
    rows, res = synth(paths, args.min_instances)
    print(f"⟡autocorr-synth: {res['compression']} over {len(paths)} files; "
          f"{len(rows)} consolidatable clusters (≥{args.min_instances} instances)\n")
    if args.emit is not None:
        c = rows[args.emit]
        print(f"# cluster #{args.emit}: {c['n']} instances, {c['holes']} holes, score {c['score']:.1f}")
        print("## instances:", ", ".join(c["labels"]))
        print("\n## MECHANICAL TEMPLATE (holes = __pN__):\n" + c["template"])
        print("## per-instance substitutions:")
        for lab, fill in zip(c["labels"], c["fillings"]):
            print(f"  {lab}:  " + ", ".join(f"{k}={v}" for k, v in sorted(fill.items())))
        return
    for i, c in enumerate(rows[:args.top]):
        head = c["template"].strip().splitlines()[0][:52]
        print(f"  #{i:<2} score {c['score']:5.1f}  ×{c['n']:<3} {c['holes']:>2} holes  autocorr {1-c['density']:.0%}"
              f"  {head}")
    print(f"\n  → autocorr_synth.py --emit <#> for the template + substitutions (the consolidation).")


if __name__ == "__main__":
    main()
