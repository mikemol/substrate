#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Where does a name live? — from a NAME, or from an agda build log.

⟡no-qualifiers: reports modules to plain-`open import`; never a `using`
list, a `renaming`, or a qualified alias.

    resolve_notinscope.py <name> ...       # ask about names directly
    resolve_notinscope.py <build.log>      # every [NotInScope] in a log
    resolve_notinscope.py … --all          # LIFT THE HOME LIMIT — report every home, not the
                                           # first 12. ⚑ This is the switch for the truncation
                                           # defect the block below describes: without it a
                                           # many-homed name shows a SUBSET, and the reader
                                           # cannot tell "these are the homes" from "these are
                                           # twelve of them". Applies to both input shapes.
    resolve_notinscope.py --selftest

⚑ IT USED TO TAKE ONLY A LOG, WHICH IS THE WRONG SHAPE FOR THE COMMON QUESTION.
"Where does `divmod-unique` live" needs no build at all — the name→home index
answers it statically — but the only entry point demanded a log file, so the
question got answered by a `python3 -c` over `def_index` or a grep. A tool whose
input is a BUILD ARTIFACT cannot answer a question about the TREE, and the tree
question is the one asked more often (memory `feedback_fix_infra_not_route_around`:
fix the library, don't route around it per-consumer).

⚑ AND IT TRUNCATED HOMES AT `[:6]` WITH NO NARROWING (worklist R5). 64 names have
more than six homes, so for those the tool silently showed a SUBSET and gave no
sign it had done so — the reader cannot tell "these are the homes" from "these are
six of the homes". A truncated list presented as a complete one is the same defect
class as a census that hides its own false positives behind a count: report the
population, or say plainly that you are not.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agda_defs import def_index


def homes_of(name, idx=None):
    """[module] defining `name`, trying the bare and both operator spellings.

    An operator is written `_≟_` where it is declared and bare `≟` at an infix
    use site, so a lookup keyed on only one spelling misses the other — the
    two-spelling rule `rename_at_source.spellings` records.
    """
    idx = def_index() if idx is None else idx
    leaf = name.split(".")[-1]
    return idx.get(leaf) or idx.get("_" + leaf + "_") or idx.get(leaf + "_") \
        or idx.get("_" + leaf) or []


def report(name, idx, limit=None):
    hs = homes_of(name, idx)
    print(f"{name}")
    if not hs:
        # ⚑ ABSENCE IS A FACT ABOUT THE INDEX, NOT ABOUT THE TREE.  `def_index`
        # covers `agda/Substrate/` only, so `Level`, `[]`, `_⊔_` — owned by
        # Agda.Primitive or the stdlib — correctly resolve to nothing here.  Say
        # which of the two it is rather than implying the name does not exist.
        print("      (no definer in agda/Substrate — may be Agda.Primitive/stdlib)")
        return
    shown = hs if limit is None else hs[:limit]
    for h in shown:
        print(f"      -> open import {h}")
    if len(shown) < len(hs):
        print(f"      … and {len(hs)-len(shown)} more of {len(hs)} homes "
              f"(pass --all to see them)")


def _selftest():
    """Counted from len(cases)."""
    cases = []

    def check(n, got, want):
        cases.append((n, got == want, got, want))

    idx = {"foo": ["A.B"], "_≟_": ["Foundation.Eq"], "many": [f"M{i}" for i in range(9)]}
    check("a plain name resolves", homes_of("foo", idx), ["A.B"])
    # ⚑ the two-spelling rule: a bare infix `≟` must find the declared `_≟_`
    check("a BARE operator finds its underscore form",
          homes_of("≟", idx), ["Foundation.Eq"])
    # ⚑ R5: the old code sliced [:6] and said nothing about the remainder
    check("more than six homes are ALL returned", len(homes_of("many", idx)), 9)
    check("a qualified reference keys on its LAST segment",
          homes_of("M.Over.foo", idx), ["A.B"])
    check("an unknown name is empty, not an error", homes_of("nope", idx), [])

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got, want in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {want!r}")
    print(f"resolve_notinscope selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    limit = None if "--all" in sys.argv else 12
    if not args:
        print(__doc__)
        sys.exit(2)
    idx = def_index()
    if len(args) == 1 and os.path.exists(args[0]) and not args[0].endswith(".agda"):
        log = open(args[0], encoding="utf-8", errors="replace").read()
        errs = re.findall(
            r"^(/\S+\.agda):(\d+)\.[\d-]+: error: \[NotInScope\]\n"
            r"Not in scope:\n\s+(\S+)", log, re.M)
        for f, ln, name in errs:
            print(f"{f.split('/agda/')[-1]}:{ln}", end="  ")
            report(name, idx, limit)
        print(f"{len(errs)} [NotInScope] site(s) in the log")
        sys.exit(0)
    for a in args:
        report(a, idx, limit)
