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
    args = ap.parse_args()
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
