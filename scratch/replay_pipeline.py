#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Replay the ban-decompose pipeline over the whole tree in TOPOLOGICAL order.

WHY THIS EXISTS.  Running the pipeline module-by-module leaves the tree in a
half-rewired state, and the state is order-dependent: reverting one file
un-rewires it against decompositions that other files still reference, so a
"fix the missing module" loop chases its own tail and can fail to converge
(measured: `Substrate.Algebra.Quotient` never cleared, because each pass
re-created the reference it had just removed).

Replaying from a clean baseline in dependency order makes the result a FUNCTION
of (baseline, pipeline) instead of a function of the order the operator happened
to run things.  That is what makes it reproducible — and reproducible is the
property the whole arc has been missing: a day's work was lost because the
result lived only in a working tree, not in a script that could rebuild it.

ORDER.  A module must be decomposed BEFORE its consumers are rewired onto its
leaves, so targets are processed in reverse-dependency (upstream-first) order.
The import DAG is read from the sources themselves — the same parse
`gen_build_makefiles` uses — not from a hand-maintained list.

PER TARGET, the pipeline is:
    1. split_lemmas <mod>              one definition per leaf; tip DELETED
    2. collapse_carrier_nesting <mod>  X/X.agda -> X.agda, when the split left a
                                       redundant nesting
    3. decompose_rewrite <mod>         every consumer rewired onto the leaves,
                                       reading each one's declared demand
All three are snapshot-guarded and all three refuse rather than guess.

⚑ STEP 2 IS NOT OPTIONAL, AND ITS ORDER IS LOAD-BEARING.  Splitting `Foundation/
Bool.agda` moves `data Bool` into `Foundation/Bool/Bool.agda`, which renames the
carrier's module AND relocates its home directory to `Foundation/Bool/Bool/` — a
directory that does not exist.  Every operator over the carrier (`_∧_`, `_∨_`,
`_xor_`) becomes a SIBLING of the carrier instead of living under it, and
carrier-locality fails on all of them.  `collapse_carrier_nesting` exists for
exactly this case (its docstring opens with the Bool example).

Read naively, the result also LOOKS like an import cycle: `Foundation.Bool.
Properties.AndAssoc` imports `Foundation.Bool` while sitting beneath it.  It is
not a cycle — it is a nesting waiting to be collapsed, and reporting it as a
cycle sends you hunting a structural problem that does not exist.  (Measured: an
earlier version of this driver reported 18 such "cycles", all Bool leaves.)

The collapse REFUSES while the parent slot is occupied, so it must run AFTER the
split has deleted the tip and BEFORE consumers are rewired — rewiring first would
point them at `X.X` and the collapse would then invalidate every one.

SAFETY.  Dry-run by default.  `--apply` snapshots first.  Every target is
checked for "did this actually converge" (no dangling module references) before
moving to the next, so a failure stops at the target that caused it rather than
cascading into the next fifty.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
AGDA = os.path.join(ROOT, "agda")
sys.path.insert(0, HERE)
import edit_snapshot

IMP = re.compile(r"^\s*(?:open\s+)?import\s+(Substrate[\w.']*)", re.M)


def module_of(path):
    rel = os.path.relpath(path, AGDA)
    return rel[:-5].replace(os.sep, ".")


def all_modules():
    out = {}
    for dp, _, fs in os.walk(os.path.join(AGDA, "Substrate")):
        for f in fs:
            if f.endswith(".agda"):
                p = os.path.join(dp, f)
                out[module_of(p)] = p
    return out


def deps(path, known):
    try:
        src = open(path, encoding="utf-8").read()
    except OSError:
        return set()
    return {m for m in IMP.findall(src) if m in known}


def toposort(targets, mods):
    """Upstream-first order over `targets`, using the full import DAG.

    A target's position depends on ALL its transitive deps, not only the ones
    that are themselves targets — a module is only safe to split once every
    module it imports has settled.
    """
    graph = {m: deps(p, mods) for m, p in mods.items()}
    seen, order, stack = set(), [], []

    def visit(m, path):
        if m in seen:
            return
        if m in path:                     # cycle: break it, report, keep going
            stack.append(m)
            return
        path = path | {m}
        for d in sorted(graph.get(m, ())):
            visit(d, path)
        seen.add(m)
        order.append(m)

    for m in sorted(mods):
        visit(m, frozenset())
    if stack:
        # ⚑ MOST "cycles" here are UNCOLLAPSED X/X NESTINGS, not real cycles: a leaf
        # under `Foundation/Bool/` importing `Foundation.Bool` looks circular only
        # because the carrier still sits one level too deep.  Say so, or the reader
        # goes hunting a structural problem that a collapse dissolves.
        cyc = sorted(set(stack))
        nest = [m for m in cyc
                if any(m.startswith(o + ".") for o in cyc) or "." in m]
        print(f"  ⚑ {len(cyc)} module(s) reported circular; most are usually an "
              f"UNCOLLAPSED X/X nesting (see collapse_carrier_nesting), not a real "
              f"cycle — they resolve once step 2 runs. e.g. {cyc[:3]}")
    rank = {m: i for i, m in enumerate(order)}
    return sorted(targets, key=lambda t: rank.get(t, len(rank)))


def dangling():
    """Module references with no source file — the convergence test."""
    mods = all_modules()
    out = set()
    for p in mods.values():
        for m in deps(p, None) if False else IMP.findall(
                open(p, encoding="utf-8").read()):
            if m not in mods:
                out.add(m)
    return out


def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def replay(targets, apply=False):
    mods = all_modules()
    missing = [t for t in targets if t not in mods]
    for t in missing:
        print(f"  skip (no source): {t}")
    targets = [t for t in targets if t in mods]
    ordered = toposort(targets, mods)
    print(f"=== {len(ordered)} target(s), upstream-first:")
    for i, t in enumerate(ordered, 1):
        print(f"  {i:3d}. {t}")
    if not apply:
        print("\n(dry run — pass --apply)")
        return 0
    edit_snapshot.guard(f"replay_pipeline ({len(ordered)} target(s))", [])
    before = dangling()
    for i, t in enumerate(ordered, 1):
        print(f"\n=== [{i}/{len(ordered)}] {t}")
        rc, out = run(["python3", "scratch/split_lemmas.py",
                       os.path.relpath(mods[t], ROOT), "--apply"])
        print("   split:", out.strip().split("\n")[-1] if out.strip() else f"rc={rc}")
        if rc != 0:
            print(f"   ⚠ split failed — stopping at this target, tree is consistent "
                  f"through {i-1}")
            return 1
        # ── 2. collapse a redundant X/X nesting, if the split created one ──
        leaf = t + "." + t.rsplit(".", 1)[-1]
        if os.path.exists(os.path.join(AGDA, leaf.replace(".", os.sep) + ".agda")):
            rc2, out2 = run(["python3", "scratch/collapse_carrier_nesting.py",
                             leaf, "--apply"])
            last = [l for l in out2.strip().split("\n") if l.strip()]
            print(f"   collapse: {last[-1] if last else f'rc={rc2}'}")
            if rc2 != 0:
                print(f"   ⚠ collapse REFUSED — the carrier's parent slot is still "
                      f"occupied; stopping (a rewire now would point consumers at "
                      f"{leaf} and the collapse would invalidate every one)")
                return 1
        rc, out = run(["python3", "scratch/decompose_rewrite.py", t, "--prefer", t,
                       "--apply"])
        n = sum(1 for l in out.split("\n") if l.startswith("rewrote"))
        unres = [l for l in out.split("\n") if "unresolved" in l]
        print(f"   rewire: {n} consumer(s)"
              + (f"   {unres[0].strip()}" if unres else ""))
        now = dangling() - before
        if now:
            print(f"   ⚠ introduced dangling reference(s): {sorted(now)[:5]}")
            return 1
    print("\n=== converged: no new dangling module references")
    return 0


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        print("usage: replay_pipeline.py <Module>... [--apply]")
        print("       replay_pipeline.py --file <list.txt> [--apply]")
        sys.exit(2)
    if args[0] == "--file" or "--file" in sys.argv:
        k = sys.argv.index("--file")
        args = [l.strip() for l in open(sys.argv[k + 1]) if l.strip()
                and not l.startswith("#")]
    sys.exit(replay(args, apply))
