#!/usr/bin/env python3
"""reuse_sweep.py — ⟡reuse-sweep: query the FULL agglomerated SPPF (every core in the tree, interned
into one shared structural space by the full-build discipline) and surface, for the CHANGED code, the
SHARED SUBTREES it participates in — the CONSOLIDATION opportunities.

Think Sequitur, recursively: a subtree shared across N units is a repeated "digram" — the move is to
PARAMETERIZE it into one abstraction, of which the N units become INSTANCES (X is an instance of Y, and
that is the POINT — consolidation is the research program, not a warning). FANIN *is* duplication:
higher fanin = MORE instances = a BIGGER consolidation win, not noise. So this does NOT filter by fanin;
it ranks by impact (fanin × size) and reports the shared subtree, its head, and every instance.

For changed code the reading is: your new unit is an INSTANCE of this shared structure — reuse the
existing abstraction if it is already named, or PARAMETERIZE it (extract the abstraction; the instances,
old and new, consolidate onto it). This is ⟡tree-resolve / the on-iso extraction, generalized.

Usage:
  scripts/reuse_sweep.py [FILES...]         # git-changed .agda; interns the full forest, ranks consolidations
  scripts/reuse_sweep.py --min-size 6       # min shared-subtree size to report
  scripts/reuse_sweep.py --gate             # exit nonzero if any consolidation opportunity touches changed code
"""
import sys, os, subprocess, argparse, glob
from collections import defaultdict

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGDA = os.path.join(REPO, "agda")

def module_of(path):
    return os.path.relpath(os.path.abspath(path), AGDA)[:-5].replace("/", ".")

def git_changed():
    for a in (["diff", "--cached", "--name-only", "--diff-filter=AM"], ["diff", "--name-only"]):
        r = subprocess.run(["git", "-C", REPO] + a, capture_output=True, text=True)
        fs = [os.path.join(REPO, f) for f in r.stdout.split() if f.endswith(".agda")]
        if fs:
            return fs
    return []

def _mod(qname): return qname.rsplit(".", 1)[0]

def _db_rows_and_verdict(min_size, min_fanin):
    """DB-derived consolidation rows + the defCopy resolver — the SAME projection reuse_tui reads (no
    re-intern). Returns (rows, verdict_of) where verdict_of(instances) → 'CONSOLIDATED'|'DUP'|'MIXED'."""
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import reuse_tui as T
    rows, copy_units, _, ncand = T.db_rows(min_size, min_fanin)
    defidx = T.load_def_index()
    cu = set(copy_units)
    def verdict_of(insts):
        return T.resolve_orbit(list(insts), defidx, cu)[0]
    return rows, verdict_of, ncand

def sweep(files, min_size, min_fanin):
    changed_mods = {module_of(f) for f in files}
    rows, verdict_of, _ = _db_rows_and_verdict(min_size, min_fanin)
    # a shared subtree touching CHANGED code is a consolidation opportunity; rank by impact (fanin×size)
    # — Sequitur digram value — and carry the defCopy verdict (DUP = genuine target; CONSOLIDATED = already
    # instances of one abstraction).
    findings = []
    for r in rows:
        chg = sorted(n for n in r["instances"] if _mod(n) in changed_mods)
        exi = sorted(n for n in r["instances"] if _mod(n) not in changed_mods)
        if chg and exi:
            findings.append((r["fanin"] * r["size"], r["fanin"], r["size"],
                             (r["head"], verdict_of(r["instances"])), chg, exi))
    findings.sort(reverse=True, key=lambda t: t[0])
    return findings

def sweep_recursive(files, min_size, min_fanin):
    """the Sequitur FIXPOINT: the containment TOWER (rung = consolidation depth), DERIVED from the
    projection (db_rows carries rung + contains); report the rungs the CHANGED code participates in."""
    changed_mods = {module_of(f) for f in files}
    rows, _, ncand = _db_rows_and_verdict(min_size, min_fanin)
    touching = []
    for r in rows:
        chg = sorted(n for n in r["instances"] if _mod(n) in changed_mods)
        if chg:
            touching.append((r["rung"], r["fanin"], r["size"], r["head"], chg, r["contains"]))
    touching.sort(key=lambda t: (-t[0], -(t[1] * t[2])))
    return touching, max((r["rung"] for r in rows), default=0), ncand

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--min-size", type=int, default=2, help="min shared-subtree size (default 2 = ENUMERATE all)")
    ap.add_argument("--min-fanin", type=int, default=2, help="min units sharing the subtree (2 = any dup)")
    ap.add_argument("--top", type=int, default=20, help="how many consolidation opportunities to show")
    ap.add_argument("--recursive", action="store_true", help="the Sequitur fixpoint: the containment tower (rungs)")
    ap.add_argument("--gate", action="store_true")
    args = ap.parse_args()

    files = [os.path.join(REPO, f) if not os.path.isabs(f) else f for f in args.files] or git_changed()
    files = [f for f in files if os.path.exists(f)]
    if not files:
        print("reuse-sweep: no changed .agda files."); return
    print(f"reuse-sweep: {len(files)} changed .agda file(s); shared subtree size ≥ {args.min_size}\n")

    if args.recursive:
        tower, max_rung, ncands = sweep_recursive(files, args.min_size, args.min_fanin)
        print(f"  containment tower height = {max_rung}; {ncands} shared-subtree candidates in the forest\n")
        if not tower:
            print("✓ changed code participates in no shared-subtree tower."); return
        rungs = sorted({r for r, *_ in tower})
        print(f"◆ changed code participates in {len(tower)} shared subtree(s), spanning rungs {rungs}")
        print(f"  (rung k = a composite built from rung-(k−1) shared subtrees; ⊃ = what it contains):\n")
        for r, units, size, head, chg, contains in tower[:args.top]:
            low = ("  ⊃ " + ", ".join(contains[:5])) if contains else ""
            print(f"    rung {r}  [{units} instances × size {size}]  {head}{low}")
            print(f"        changed: " + ", ".join(chg))
        if args.gate and tower:
            sys.exit(1)
        return

    findings = sweep(files, args.min_size, args.min_fanin)
    if not findings:
        print("✓ changed code shares no consolidatable subtree with the tree."); return
    print(f"◆ {len(findings)} CONSOLIDATION opportunit(ies) — changed code instantiates shared structure.")
    print(f"  (parameterize the pattern; the instances — old and new — consolidate onto it. Ranked by fanin×size.")
    print(f"   verdict via defCopy: ✗DUP = genuine target (independent originals); ✓CONSOLIDATED = already instances.)\n")
    for impact, fanin, size, head, chg, exi in findings[:args.top]:
        h, verdict = head if isinstance(head, (list, tuple)) else (head, "?")
        mark = {"CONSOLIDATED": "✓", "DUP": "✗", "MIXED": "·"}.get(verdict, "?")
        print(f"    {mark} {verdict:12s} [{fanin} instances × size {size}]  {h or '(anonymous pattern → parameterize)'}")
        print(f"        changed:  " + ", ".join(chg))
        print(f"        also in:  " + ", ".join(exi[:4]) + (f"  … (+{len(exi)-4})" if len(exi) > 4 else ""))
    if args.gate:
        sys.exit(1)

if __name__ == "__main__":
    main()
