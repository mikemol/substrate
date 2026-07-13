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

def sweep(files, min_size, min_fanin):
    sys.path.insert(0, os.path.join(REPO, "jea", "metalanguage"))
    import jea_pysim as J
    changed_mods = {module_of(f) for f in files}
    cores = glob.glob(os.path.join(AGDA, "_build", "**", "agda", "Substrate", "**", "*.agdai"), recursive=True)
    print(f"interning the full forest: {len(cores)} cores …", flush=True)
    C = J.Corpus()
    for c in sorted(cores):
        try: C.add_agdai(c)
        except Exception: pass
    print(f"  {len(C.units)} units interned.\n")

    def mod(u): return getattr(u, "name", "").rsplit(".", 1)[0]
    node_units = defaultdict(set)                                  # canonical node -> owning units (= its fanin)
    for ui, u in enumerate(C.units):
        for nid in getattr(u, "support", ()): node_units[nid].add(ui)

    # a canonical node with fanin ≥ 2 IS shared structure = a consolidation opportunity. Report every
    # shared subtree that touches CHANGED code, ranked by IMPACT (fanin × size) — Sequitur digram value.
    findings = []
    for nid, fanin, size, head in C.extract_candidates(min_fanin=min_fanin, min_size=min_size):
        owners = node_units.get(nid, ())
        chg = sorted({C.units[i].name for i in owners if mod(C.units[i]) in changed_mods})
        exi = sorted({C.units[i].name for i in owners if mod(C.units[i]) not in changed_mods})
        if chg and exi:
            findings.append((fanin * size, fanin, size, head, chg, exi))
    findings.sort(reverse=True)
    return findings

def sweep_recursive(files, min_size, min_fanin):
    """the Sequitur FIXPOINT: build the containment TOWER (rung = consolidation depth) over the whole
    forest via typeholer_path; report the rungs the CHANGED code participates in, each showing what it
    CONTAINS (the recursive stack: a rung-k abstraction is built from rung-(k-1) ones)."""
    sys.path.insert(0, os.path.join(REPO, "jea", "metalanguage"))
    import typeholer_path as tp
    changed_mods = {module_of(f) for f in files}
    cores = glob.glob(os.path.join(AGDA, "_build", "**", "agda", "Substrate", "**", "*.agdai"), recursive=True)
    print(f"interning + building the containment tower: {len(cores)} cores …", flush=True)
    C = tp.build_corpus(sorted(cores))
    cands = tp.extract_cands(C, min_fanin=min_fanin, min_size=min_size)
    direct, rung, _ = tp.containment_dag(cands)
    by_nid = {c.nid: c for c in cands}
    def mod(ui): return getattr(C.units[ui], "name", "").rsplit(".", 1)[0]
    touching = []
    for c in cands:
        chg = sorted({C.units[i].name for i in c.unit_ids if mod(i) in changed_mods})
        if chg:
            contains = sorted({tp._head_str(by_nid[b].head) for b in direct.get(c.nid, [])})
            touching.append((rung[c.nid], c.units, c.size, tp._head_str(c.head), chg, contains))
    touching.sort(key=lambda t: (-t[0], -(t[1] * t[2])))
    return touching, max((rung[c.nid] for c in cands), default=0), len(cands)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--min-size", type=int, default=6, help="min shared-subtree size to report")
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
    print(f"  (parameterize the pattern; the instances — old and new — consolidate onto it. Ranked by fanin×size.)\n")
    for impact, fanin, size, head, chg, exi in findings[:args.top]:
        h = head[1] if isinstance(head, (list, tuple)) and len(head) > 1 else head
        print(f"    [{fanin} instances × size {size}]  {h or '(anonymous pattern → parameterize)'}")
        print(f"        changed:  " + ", ".join(chg))
        print(f"        also in:  " + ", ".join(exi[:4]) + (f"  … (+{len(exi)-4})" if len(exi) > 4 else ""))
    if args.gate:
        sys.exit(1)

if __name__ == "__main__":
    main()
