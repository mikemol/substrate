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

HONEST SCOPE. templatize lowers PYTHON source (jea_pyalg / ast), so this runs over the substrate's own
.py tooling corpus (where it fully closes: template + fillings are compiling Python). The AGDA path is
the same algorithm over the interned SPPF (skeleton + ordered lit/op residue per unit from catalog.db);
its residue-alignment over the shared DAG is the next rung (⟡autocorr-synth-agda) — the design is here,
the Python corpus is the working proof.

  autocorr_synth.py [--min-instances 2] [--top 12] [PATHS...]   # default: jea/metalanguage + scripts
  autocorr_synth.py --emit <cluster-id>                          # print the full template + all fillings
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
    args = ap.parse_args()
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
