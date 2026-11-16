#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Pass the 14 adapter args to each Graded part QUALIFIED through a module alias.

⚑ The direct form `open …Defs.Over _+_ _*_ 𝟘 𝟙 …` NAMES the adapter's ops at the
use site, where they can collide with an unrenamed `Foundation.Nat._+_` — an
[AmbiguousName] the tip form never produced (it named nothing).  Binding

    module FCRq = …FromCommRing.Over <args>
    open …Defs.Over FCRq._+_ FCRq._*_ FCRq.𝟘 … FCRq.*-absorbʳ

resolves every arg unambiguously.  `module M = …` is a module definition, NOT an
import directive, so it mints ZERO ban-ratchet keys (the tree already uses it).
It also gives the `module MF = <part>.Over …` alias form a target again.

USAGE: fcr_qualify.py <file>... [--apply]
"""
import os, re, sys

_SNAPPED = []


def _snapshot_once(path):
    """Arm edit_snapshot on the FIRST write of a run; a no-op thereafter.

    ⚑ This tool rewrites files it read — the shape that made 33 files
    unrecoverable (Coxeter/Core.agda 76 lines -> 3).  The write is inside a loop,
    so a per-file `guard` would arm only the first file AND shell out to `git
    stash create` on every iteration; arming once per run is both correct and
    cheap.  Recovery is per-file and MANUAL by design — edit_snapshot never
    restores anything itself.
    """
    if _SNAPPED:
        return
    _SNAPPED.append(True)
    try:
        import edit_snapshot
        edit_snapshot.guard('fcr_qualify', [path])
    except Exception as e:
        print(f"   \u26a0 snapshot unavailable ({e}) \u2014 recover via git if needed")



FCR = "Substrate.Algebra.Polynomial.Graded.FromCommRing"
NAMES = ["_+_", "_*_", "𝟘", "𝟙", "+-assoc", "+-comm", "+-identityˡ", "+-identityʳ",
         "*-assoc", "*-comm", "*-identityˡ", "*-distribˡ", "*-absorbˡ", "*-absorbʳ"]
ARGS = " ".join(NAMES)
AD = re.compile(r"^(\s*)open\s+" + re.escape(FCR) + r"\.Over\s+(?P<args>\S+)(?P<tail>.*)$")
PART = re.compile(r"^(\s*)open\s+(Substrate\.Algebra\.Polynomial\.Graded\.(?:Defs|Laws\.\w+))"
                  r"\.Over\s+" + re.escape(ARGS) + r"(?P<tail>.*)$")

def go(path, apply):
    L = open(path, encoding="utf-8").read().split("\n")
    if not any(PART.match(l) for l in L):
        return None
    out, alias, n = [], None, 0
    for l in L:
        m = AD.match(l)
        if m:
            n += 1
            alias = "FCRq" if n == 1 else f"FCRq{n}"
            out.append(f"{m.group(1)}module {alias} = {FCR}.Over {m.group('args')}")
            out.append(l)
            continue
        m = PART.match(l)
        if m and alias:
            q = " ".join(f"{alias}.{x}" for x in NAMES)
            out.append(f"{m.group(1)}open {m.group(2)}.Over {q}{m.group('tail')}")
            continue
        out.append(l)
    txt = "\n".join(out)
    if f"import {FCR}\n" not in txt and f"import {FCR}" not in txt.split("\n"):
        li = max((i for i, l in enumerate(out)
                  if re.match(r"^\s*(?:open\s+)?import\s", l)), default=0)
        out[li + 1:li + 1] = [f"import {FCR}"]
        txt = "\n".join(out)
    if apply:
        _snapshot_once(path)
        open(path, "w", encoding="utf-8").write(txt)
    return n

if __name__ == "__main__":
    # ⚑ ONE ACT: state the intent AND take the snapshot, BEFORE `apply` is bound.
    # `_snapshot_once` below is correct wherever it runs, but it runs at the first
    # PENDING WRITE — a point a run that matches nothing never reaches, and it is
    # consulted AFTER the apply/dry decision rather than at it. `require_at_entry`
    # asks at the invocation; `paths=` is load-bearing because `snapshot()` reaches
    # TRACKED content whole-worktree while `_copy_untracked(paths)` is the only
    # mechanism that reaches an untracked Agda leaf.
    _es_paths = [a for a in sys.argv[1:] if not a.startswith("-")]
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit_snapshot as _es
    _es.require_at_entry("fcr_qualify", paths=_es_paths)
    apply = "--apply" in sys.argv
    c = 0
    for p in [a for a in sys.argv[1:] if a != "--apply"]:
        if go(p, apply) is not None:
            c += 1
    print(f"qualified: {c} files" + ("" if apply else "  (dry run)"))
