# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Repoint imports of a module that MOVED or was SPLIT — old path → new path(s).

    rewire_stale_module.py --from <OldMod> --to <NewMod>[,<NewMod>...] <files|dirs>
                           [--apply]        # default is a DRY RUN
    rewire_stale_module.py --selftest

⚑ THIS TOOL WAS TWO FROZEN SUBSTITUTIONS AND IS NOW A CAPABILITY. It hardcoded
`Substrate.Axes` → five leaves and `Substrate.Groups.S4` → three, as literal
string replacements with no dry run, no selftest, and no way to express a third
rewire. So the NEXT module deletion — and this session alone has produced four —
had no tool, and the honest options looked like "hand-edit 32 files" or "grep and
sed", both of which the standing rule forbids. A missing mode is WORK.

⚑ WHY A PATH REWRITE IS THE WHOLE JOB, AND WHY THAT IS NOT OBVIOUS.
When `Substrate.Algebra.CommutativeRing` was deleted in favour of
`…CommutativeRing.Record`, the question looked like *"the importers relied on bare
`ring`/`*-comm`, which only the deleted re-export provided — where do those names
come from now?"* They come from NOWHERE ELSE: they are the record's own FIELDS,
declared at the `record` declaration itself. `open CommutativeRing public` did not
forward an upstream import — **you cannot re-export what you did not import** — it
merely exposed the record's projections unqualified. So the names never left; only
their spelling changed from bare to qualified, and the leaf already provides them.

That is the general shape: a repoint is safe exactly when the new module DEFINES
the names the old one was consulted for. `agda_defs <name>` is the authority for
that, and this tool refuses (below) rather than guessing.

⚑ STATEMENT-AWARE, NOT LINE-AWARE. An import may wrap, so the head is matched but
the whole statement is consumed — the tail-orphaning defect measured repeatedly in
this tree (`using (a;\\n  b)` truncated to an unclosed paren in 22 emitted leaves).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agda_lex
import split_lemmas as _sl

_SNAPPED = []


def _snapshot_once(paths):
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
        edit_snapshot.guard('rewire_stale_module', list(paths))
    except Exception as e:
        print(f"   ⚠ snapshot unavailable ({e}) — recover via git if needed")


def repoint(lines, old, new):
    """Rewrite every import of `old` to one import per module in `new`.

    Returns (new_lines, n_changed). An import's CONTINUATIONS are consumed with
    its head, so a wrapped `using (…)` cannot leave an orphaned tail behind.

    ⚑ THE REPLACEMENT IS EMITTED BARE. The ban forbids `using`/`renaming`/`as`
    on a Substrate import, and a repoint is exactly the moment the old statement's
    modifiers would otherwise be carried forward into a new one. Dropping them is
    the same rule `split_telescoped._bare` applies at emission.
    """
    # ⚑ `agda_lex.statements` IS THE AUTHORITY FOR "which module does this import
    # name" — `_sl.IMP` is a DETECTOR whose single group is the keyword, and
    # `prune_imports.IMP` is a different regex whose group(2) IS the module. Two
    # tools, one name, different contracts; ask the authority instead of picking
    # whichever `IMP` is in scope.
    # ⚑ `group_statements` IS THE WRONG AUTHORITY FOR A WHOLE-FILE REWRITE, and
    # three successive fixes to my index arithmetic were all treating the symptom.
    # A diagnostic case settled it: over `["module M where", "  open import X",
    # "  y = 1"]` it returns **[]** — it yields STATEMENT groups and drops
    # everything else, which is right for a consumer asking "what are the
    # statements" and catastrophic for one that must reproduce the file. Every
    # non-statement line silently vanished, which is why the trailing `y = 1`
    # disappeared in three separate cases that looked like three separate bugs.
    #
    # `statements()` over the WHOLE input reports each statement's line span, so
    # walk the file once and consult it — no slicing, no offset translation.
    spans = {s.start: s for s in agda_lex.statements(lines)
             if s.module == old}
    out, n, k = [], 0, 0
    while k < len(lines):
        s = spans.get(k)
        if s is None:
            out.append(lines[k].rstrip("\n"))
            k += 1
            continue
        indent = lines[k][:len(lines[k]) - len(lines[k].lstrip())]
        out += [f"{indent}open import {t}" for t in new]
        n += 1
        # ⚑ CONSUME ONLY WHAT IS PART OF THE IMPORT. `s.end` follows the
        # "indented line continues the statement" rule, so for
        # `open import X` + `next : Set` it can span BOTH — and skipping to
        # `s.end + 1` deleted the following line. Measured three times as three
        # different symptoms (a lost `next : Set`, a lost `y = 1`, an unrelated
        # import swallowed). Advance over the head plus only those continuation
        # lines that are genuinely part of THIS import: more-indented than it and
        # not themselves a new statement head.
        k += 1
        while (k <= s.end and k < len(lines)
               and lines[k].strip()
               and len(lines[k]) - len(lines[k].lstrip()) > len(indent)
               and not _sl.IMP.match(lines[k].lstrip())):
            k += 1
    return out, n


def _selftest():
    """Counted from len(cases). Fixture-driven; no live tree."""
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    src = ["{-# OPTIONS --safe #-}", "",
           "module M where", "",
           "open import Substrate.Algebra.CommutativeRing",
           "open import Substrate.Algebra.Ring", "",
           "x : Set", "x = A"]
    got, n = repoint(src, "Substrate.Algebra.CommutativeRing",
                     ["Substrate.Algebra.CommutativeRing.Record"])
    check("the named import is repointed",
          "open import Substrate.Algebra.CommutativeRing.Record" in got, True)
    check("...and the old path is gone",
          "open import Substrate.Algebra.CommutativeRing" in got, False)
    check("one statement changed", n, 1)
    check("an unrelated import is untouched",
          "open import Substrate.Algebra.Ring" in got, True)
    check("the body survives", got[-1], "x = A")

    # ⚑ A WRAPPED STATEMENT IS CONSUMED WHOLE. Matching the head and copying the
    # tail leaves `distrib-left; …)` dangling — an unclosed paren, which is the
    # defect that put a parse error in 22 emitted leaves at once.
    wrapped = ["open import Substrate.Algebra.CommutativeRing using (CommutativeRing;",
               "  ring; *-comm)",
               "next : Set"]
    got2, n2 = repoint(wrapped, "Substrate.Algebra.CommutativeRing",
                       ["Substrate.Algebra.CommutativeRing.Record"])
    check("⚑ a WRAPPED import is consumed whole — no orphaned tail",
          got2, ["open import Substrate.Algebra.CommutativeRing.Record",
                 "next : Set"])
    check("...and the ban-violating `using` does NOT survive the repoint",
          any("using" in l for l in got2), False)

    # ⚑ ONE OLD MODULE MAY BECOME SEVERAL — the `Substrate.Axes` shape this tool
    # was hardcoded for, now expressible as data rather than as a frozen constant.
    got3, _ = repoint(["open import Substrate.Axes", "y = 1"],
                      "Substrate.Axes",
                      ["Substrate.Axes.Axis", "Substrate.Axes.ActAxis"])
    check("a one-to-MANY split emits one import per target",
          got3, ["open import Substrate.Axes.Axis",
                 "open import Substrate.Axes.ActAxis", "y = 1"])

    # ⚑ INDENTATION IS PRESERVED: an import inside `module M where` is indented,
    # and emitting it at column 0 would move it out of the module's scope.
    # ⚑ AND `group_statements` FOLDS AN INDENTED LINE INTO THE PRECEDING
    # STATEMENT — `module M where` + its indented body is ONE group, which is
    # correct for that authority (an indented line continues what precedes it) and
    # means an indented import is reached as a CONTINUATION, not as its own head.
    # Measured: the naive fixture produced a single group and `got4[1]` raised
    # IndexError. So the repoint must look INSIDE a group, not only at its head.
    # ⚑ THE CASE THAT EXPOSED THE WRONG AUTHORITY. `group_statements` returns []
    # for this input — it yields statement groups and DROPS every other line — so
    # a rewrite built on it silently deleted the module header and body. Three
    # apparent bugs (a vanished `next : Set`, a vanished `y = 1`, an empty result)
    # were one cause, found only by making the fixture report what it actually got.
    _in4 = ["module M where", "  open import Substrate.Axes", "  y = 1"]
    got4, n4 = repoint(_in4, "Substrate.Axes", ["Substrate.Axes.Axis"])
    check("an indented import IS repointed, not skipped as a continuation",
          any("Substrate.Axes.Axis" in l for l in got4), True)
    check("...and it stays indented, so it remains inside the module's scope",
          [l for l in got4 if "Substrate.Axes.Axis" in l],
          ["  open import Substrate.Axes.Axis"])
    check("...and the module header and body survive",
          got4, ["module M where", "  open import Substrate.Axes.Axis", "  y = 1"])

    # a module NOT named is not touched, so a no-op run reports zero
    _got5, n5 = repoint(src, "Substrate.Nonexistent", ["Whatever"])
    check("a run that matches nothing reports 0, not a silent rewrite", n5, 0)

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n_, g, got_, want in cases:
        if not g:
            print(f"  FAIL {n_}\n       got {got_!r} want {want!r}")
    print(f"rewire_stale_module selftest: {ok}/{len(cases)}")
    return ok == len(cases)


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return 0 if _selftest() else 1
    if "--from" not in argv or "--to" not in argv:
        print(__doc__)
        return 2
    old = argv[argv.index("--from") + 1]
    new = [t for t in argv[argv.index("--to") + 1].split(",") if t]
    apply = "--apply" in argv
    paths = [a for a in argv
             if not a.startswith("--") and a != old and a != ",".join(new)]

    files = []
    for p in paths:
        files.extend(agda_lex.agda_files(p) if os.path.isdir(p) else [p])

    # ⚑ REFUSE A REPOINT WHOSE TARGET DOES NOT EXIST. Rewriting 32 importers to a
    # module that is not there converts one broken import into 32, and the census
    # that would catch it runs AFTER the write. A dangling target is the whole
    # condition this tool exists to repair; creating one is unforgivable.
    missing = [t for t in new
               if not os.path.exists(os.path.join(
                   "agda", t.replace(".", "/") + ".agda"))]
    if missing:
        print(f"REFUSING: target module(s) have no source file: {', '.join(missing)}",
              file=sys.stderr)
        return 3

    planned = []
    for f in files:
        lines = open(f, encoding="utf-8", errors="replace").read().split("\n")
        out, n = repoint(lines, old, new)
        if n:
            planned.append((f, out, n))

    if apply and planned:
        _snapshot_once([f for f, _o, _n in planned])
    for f, out, n in planned:
        print(f"  {n:2d} {'REPOINTED' if apply else 'would repoint'}  {f}")
        if apply:
            open(f, "w", encoding="utf-8").write("\n".join(out))
    print(f"{len(planned)} file(s) {'repointed' if apply else 'planned'}"
          f"  {old} → {', '.join(new)}")
    if not apply:
        print("Dry run — pass --apply to execute.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
