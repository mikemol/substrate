#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which modules have no suite — the population a green run says nothing about.

⚑⚑⚑ A GREEN SUITE RUN IS A FACT ABOUT THE MODULES THAT HAVE SUITES. Measured: a 58-file
conversion was verified two ways — a prospective ruff+mypy pass and spot-checked suites — and
`ratchet_render.py` broke a gate anyway, because it has NO SUITE and therefore passed the second
check VACUOUSLY. Its `Report._replace` had seven callers in three other files, and nothing
exercised the path until an unrelated gate ran.

⚑⚑ SO THE WEAKNESS OF *"the suites still pass"* IS EXACTLY PROPORTIONAL TO COVERAGE, AND NOTHING
REPORTED COVERAGE. That is `census-green-is-a-fact-about-the-census` in its sharpest local form:
the verification covered what has verification and said nothing about the rest BY CONSTRUCTION.
This module makes the rest READABLE, which is the only thing that turns a vacuous pass into a
bounded one.

⚑ IT REPORTS A POPULATION, NEVER A VERDICT. A module without a suite is not thereby defective —
a pure constant table needs none — but it IS a module whose changes nothing catches, and a reader
weighing a batch needs to know which of its files sit there. Naming them is the finding; deciding
which deserve suites is a judgement this cannot make.

⚑ AND THE PAIRING IS BY CONVENTION, NOT BY GUESS: `<module>.py` is covered by
`<module>_selftest.py` beside it, which is what `suite_discovery` finds and what the runner
executes. A module whose suite lives elsewhere reads as UNCOVERED here — a limit of the naming
convention, stated so the count is not mistaken for a defect list.

⚑⚑⚑ AN INLINE `def selftest()` IS A THIRD CATEGORY, AND CALLING IT COVERAGE WAS MY ERROR. Four
modules carry their cases in their own tails; the runner executes them, so I widened the
predicate to accept both and reported coverage jumping 121→128. Operator: *"n-split that crap.
No more in-line/tail testing."* It is the state a module is in BEFORE its cases are split out,
not a second convention — and `toolmodes.py`, with a 615-line `_selftest` inside 3,700 lines no
edit can touch, is where that shape ends. It is named separately so neither fact is lost: the
cases EXIST (do not write duplicates) and they are in the WRONG PLACE (a split is owed).

⚑⚑⚑ AND THAT THIRD CATEGORY SPANNED TWO SHAPES A READER COULD NOT TELL APART (⟡inline-spans-
two-shapes). `is_suite` matches a `--selftest` DISPATCH — correctly, because the dispatch is what
`run_selftests` keys on — so a module with a `__main__ --selftest` block and NO `selftest`
definition anywhere landed in the same bucket as a module carrying real cases in its tail. The
two owe OPPOSITE work: a tail owes a SPLIT (move existing cases out), a dispatch-only CLI owes a
NEW SUITE (there are no cases to move).

⚑⚑ MEASURED, AND IT MISDIRECTED A DISPATCH. `ratchet_suites.py` was briefed for a split on the
strength of its INLINE flag; it has no `selftest` def, so there was nothing to split, and
`module_trim --dry-run` refused with *"no top-level definition named: selftest"*. The refusal
worked — but a census whose category sends a reader to the wrong tool is reporting its own
predicate's reach as a fact about the module.

⚑⚑⚑ AND THE SPLIT CATEGORY IMMEDIATELY OVER-REPORTED, WHICH SPLIT IT AGAIN. Its first live run
flagged `kind_partition_show.py` and `md_spans_show.py` as owed a NEW SUITE. Mechanically true —
they answer `--selftest` and define no cases — and WRONG as an instruction: their dispatch
FORWARDS to `kind_partition_selftest` / `md_spans_selftest`, the suites of the readers they wrap,
which already cover every branch a case could pin. Writing suites for them would either duplicate
those or assert that a passthrough passes through, and a vacuous suite written to move a number
is worse than an honest gap.

⚑⚑ SO `delegating` IS THE FOURTH SHAPE, AND THE DISCRIMINATOR IS STATIC: where the dispatch GOES.
A delegating guard imports another module's suite and calls it, so the edge is in the AST and
`import_edges.deferred_dotted` reads it; a bare guard's flag branch reaches nothing. The
obligation differs accordingly — a delegator owes NOTHING (it is covered at the far end), a bare
dispatch owes a suite that does not exist. Three passes over this one category, each finer than
the last, and each found by a LIVE RUN rather than by review: a category is a READING, and a
reading that names two obligations can only be acted on by guessing which.

⚑ THE FORWARDED-TO SUITE MUST EXIST FOR THE DELEGATION TO COUNT. A guard importing a suite that
was deleted forwards to nothing, and calling that covered would be the flattering error — the
direction that goes unnoticed.

⚑ `inline` REMAINS THE DEBT UNION AND `delegating` IS NOT IN IT. The union names what a reader
OWES WORK ON; a delegator owes none, so folding it in would re-merge exactly the distinction the
last two passes bought.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from mikemol.corpus import import_edges, suite_discovery

from substrate import corpus


def _dispatch_reaches_local(text: str) -> bool:
    """Report whether a `--selftest` guard calls a top-level def defined in this same file.

    ⚑⚑⚑ THE FACT IS STRUCTURAL, AND KEYING ON A NAME COST TWO FINDINGS IN TWO TICKS. The text
    pattern matched `def selftest` only, so nine modules spelling it `_selftest` read as owed a
    NEW SUITE (gate-G318); widening to `_?selftest` then left `type_scope`, which names its arms
    `_cases` and answers `--selftest` with 14 passing. A third regex would fix that member and
    leave the class — the next module to spell it `_run_cases` reopens the finding.

    ⚑⚑ SO THE QUESTION IS *DOES THE DISPATCH REACH A BODY HERE*, which is what `module_trim` needs
    to move and what makes the cases exist, and it is readable without knowing any name in
    advance. `delegates_to` already reads the dispatch's FAR end from the AST; this reads its NEAR
    end, so the two halves of one question are answered the same way.

    ⚑ A DISPATCH REACHING NOTHING MUST STILL READ FALSE. That is the category which sent a reader
    to `module_trim` with nothing to split (`ratchet_suites`), and collapsing it back would undo
    the pass that separated them.
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return False
    top = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    for guard in ast.walk(tree):
        if not isinstance(guard, ast.If) or "--selftest" not in ast.dump(guard.test):
            continue
        for node in ast.walk(guard):
            called = node.func if isinstance(node, ast.Call) else None
            if isinstance(called, ast.Name) and called.id in top:
                return True
    return False


if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

# What a module's suite is called — the ONE accepted shape.
SUITE_SUFFIX = "_selftest.py"

# ⚑ AND THE SHAPE THAT IS DEBT: cases in the module's own tail. Detected so it can be REPORTED,
# never so it can count as coverage.
#
# ⚑⚑ ANCHORED AT COLUMN ZERO, WHICH IS THE DIFFERENCE BETWEEN THE TWO DEBT SHAPES. A substring
# test would also match `suite.selftest()` in a call, `def selftest` nested inside a class, and
# the word inside a docstring — and it is precisely the TOP-LEVEL definition that `module_trim`
# needs in order to move the cases out. The tool that performs the split and the census that
# reports one is owed must agree on what a tail IS, or the census points at work no tool can do.
#
# ⚑⚑⚑ AND THE PRIVATE SPELLING IS THE SAME OBJECT — MISSING IT REPORTED NINE PASSING SUITES AS
# ABSENT. `iface_cost` and eight siblings define `_selftest` at top level and call it from their
# dispatch; measured, they answer `--selftest` with real arms (`iface_cost` 5/5, `iface_readers`
# 8/8). The unwidened pattern could not match the leading underscore, so every one fell through to
# *"DISPATCH --selftest reaching nothing — owed a NEW SUITE"* — a census proposing nine suites that
# already exist, which is the direction that MANUFACTURES WORK.
#
# ⚑⚑ IT IS THIS FILE'S OWN RECORDED ERROR, ONE SPELLING OVER. The note above says the top-level
# DEFINITION is the fact rather than the word — and then keyed on one spelling of the name, which
# is `census-keyed-on-one-spelling` committed inside the comment warning against its sibling.
# `module_trim` moves a top-level def whether or not it leads with an underscore, so admitting the
# private form keeps the split tool and this census agreeing about what a tail IS.
TAIL_SUITE = re.compile(r"^def _?selftest\s*\(", re.MULTILINE)

# The package whose suites a delegating dispatch can forward to.
PACKAGE = "substrate"

# Files that are suites themselves, or are not modules a suite would cover.
DUNDER = "__"


@dataclass(frozen=True, slots=True)
class Coverage:
    """One directory's modules, split by WHAT EACH OWES — which is what a category is for.

    ⚑⚑ `inline` IS NEITHER COVERED NOR UNCOVERED. Its cases EXIST, so calling it uncovered would
    send someone to write duplicates; they are in the wrong PLACE, so calling it covered would
    hide the split that is owed. Two categories cannot carry that.

    ⚑⚑⚑ AND THAT THIRD ONE SPLIT TWICE MORE, EACH TIME BECAUSE A LIVE RUN NAMED THE WRONG WORK.
    `tailed` has a top-level `def selftest`: the cases are there and owe a SPLIT. `dispatch_only`
    answers `--selftest` and reaches nothing: a suite must be WRITTEN. `delegating` answers it by
    calling ANOTHER module's suite, which already covers the reader it wraps: nothing is owed.
    Merged, a reader picks the wrong tool — measured twice, on a split with nothing to split and
    on two CLIs that would have got vacuous suites.

    ⚑ `inline` STAYS, AS THE DEBT UNION — `tailed` plus `dispatch_only`, the two that owe work.
    `delegating` is deliberately outside it: it is a reading, not a debt. The name is kept because
    the render and the older readers consume it, and silently changing what a name MEANS is worse
    than adding ones that are precise.
    """

    covered: tuple[str, ...]
    uncovered: tuple[str, ...]
    tailed: tuple[str, ...] = ()
    dispatch_only: tuple[str, ...] = ()
    delegating: tuple[str, ...] = ()

    @property
    def inline(self) -> tuple[str, ...]:
        """Return the modules carrying selftest debt in their own body — tail or bare dispatch."""
        return tuple(sorted(self.tailed + self.dispatch_only))

    @property
    def total(self) -> int:
        """Return how many modules were considered — the denominator a count needs."""
        return len(self.covered) + len(self.uncovered) + len(self.inline) + len(self.delegating)

    @property
    def ratio(self) -> str:
        """Return the coverage as a readable fraction."""
        return f"{len(self.covered)}/{self.total}"


def modules(directory: Path) -> tuple[Path, ...]:
    """Return every module in `directory` that a suite could cover.

    ⚑ A SUITE IS NOT ITSELF COVERED, and a dunder file is not a module in this sense. Counting
    either would inflate the denominator with files the convention never applies to.
    """
    return tuple(
        sorted(
            path
            for path in directory.glob("*.py")
            if not path.name.endswith(SUITE_SUFFIX) and not path.name.startswith(DUNDER)
        )
    )


def has_suite(module: Path) -> bool:
    """Report whether a SIBLING `<module>_selftest.py` exists — the only accepted shape."""
    return module.with_name(module.stem + SUITE_SUFFIX).exists()


def has_tail_suite(module: Path) -> bool:
    """Report whether this module defines `selftest` in its OWN body — cases owed a SPLIT.

    ⚑⚑⚑ AN INLINE SUITE IS THE UNSPLIT SHAPE, AND COUNTING IT AS COVERAGE WAS MY ERROR. I found
    four modules (`baseline_io` 10/10, `baseline_state`, `ratchet_flags`, `ratchet_log`) carrying
    cases in their own tails, widened the predicate to accept them, and reported coverage jumping
    121→128. Operator: *"n-split that crap. No more in-line/tail testing."*

    ⚑⚑ THE RUNNER EXECUTING BOTH IS WHY IT LOOKED LIKE A CONVENTION. It is not one — it is the
    state a module is in BEFORE its cases are split out, and every property that makes a suite
    useful is weaker inline: the cases cannot be run without importing the module they test, they
    inflate the file the per-file gate measures, and a module too dirty to edit takes its own
    suite hostage. `toolmodes.py` carried a 615-line `_selftest` inside 3,700 lines that no edit
    can touch, which is the end state of this shape.

    ⚑ IT IS THE **TOP-LEVEL DEFINITION** THAT IS THE FACT, not the word appearing somewhere. That
    is the object `module_trim` moves, so a census keyed on anything looser reports a split that
    the tool performing splits would refuse — which is exactly what happened.
    """
    text = module.read_text(encoding="utf-8", errors="replace")
    # ⚑⚑ THE UNION IS DELIBERATE AND NEITHER HALF IS REDUNDANT. The pattern catches a tail that
    # nothing dispatches — cases sitting in a file with no `--selftest` guard at all, which still
    # owe a split. The structural read catches a dispatched tail under ANY name, which is the half
    # two regexes could not reach. Either alone drops a real population.
    return bool(TAIL_SUITE.search(text)) or _dispatch_reaches_local(text)


def delegates_to(module: Path) -> str | None:
    """Return the sibling suite this module's dispatch FORWARDS to, or None.

    ⚑⚑⚑ THE DISCRIMINATOR IS WHERE THE DISPATCH GOES, AND IT IS STATICALLY READABLE. A CLI over a
    covered reader keeps a `--selftest` guard that imports that reader's suite and calls it —
    `md_spans_show` → `md_spans_selftest`, `kind_partition_show` → `kind_partition_selftest`. The
    forwarded-to name is right there in the AST.

    ⚑⚑ BOTH READINGS ARE UNIONED HERE, AND THE FIRST CUT GOT THAT WRONG. I reached for
    `deferred_dotted` alone, reasoning that an import inside a `__main__` guard is "not module
    level" — and the census kept reporting both delegators as bare dispatches. It is
    `import_edges._eager_bodies` that settles it: an `ast.If` body DESCENDS EAGERLY, because the
    question that function answers is *what executes when this file is run*, and a guard body
    does. A function body does not, which is why `deferred_dotted` exists. `--selftest` guards are
    written both ways in this tree, so the union is the honest reading and either alone drops
    half the population — the `correlated-instruments` shape, where one instrument's blind spot
    is read as an absence.

    ⚑⚑ AND IT MUST RESOLVE TO A SUITE THAT EXISTS. A guard importing a deleted suite forwards to
    nothing; calling that covered would read better than the tree is, which is the error direction
    that survives review. So the name is checked against the filesystem, not just the AST.

    ⚑ THE FORWARDED-TO MODULE IS RETURNED, NOT A BOOLEAN. A reader asking why a module owes
    nothing needs the far end — that is where the cases it is relying on actually live.
    """
    prefix = f"{PACKAGE}."
    stem = SUITE_SUFFIX[: -len(".py")]
    reachable = import_edges.module_level_dotted(str(module)) | import_edges.deferred_dotted(
        str(module)
    )
    for dotted in sorted(reachable):
        if not dotted.startswith(prefix):
            continue
        name = dotted[len(prefix) :]
        if "." in name or not name.endswith(stem):
            continue
        if module.with_name(f"{name}.py").exists():
            return name
    return None


def is_dispatch_only(module: Path) -> bool:
    """Report whether the module answers `--selftest` at all — the shape, before its direction.

    ⚑⚑⚑ THIS IS THE OTHER HALF OF WHAT `inline` USED TO MEAN. `suite_discovery.is_suite` admits a
    `__main__` block naming `--selftest` whether or not a `selftest` body exists anywhere —
    deliberately, because a split module keeps the dispatch and exports the body to a sibling, and
    requiring both in one file once erased three real suites. That reach is RIGHT for discovery
    and WRONG to read as a description of the module.

    ⚑⚑ IT DOES NOT DISTINGUISH THE DIRECTION, AND `coverage` MUST. A dispatch that forwards to
    another module's suite owes nothing; a dispatch that reaches nothing owes a suite. This
    predicate answers only *does it dispatch*, and `delegates_to` answers *where to* — kept apart
    so neither question is settled by the other's answer.

    ⚑ `suite_discovery` IS NOT CHANGED TO FIX ANY OF THIS, and that is the ruling. It keys on what
    the runner keys on; narrowing it to require a body would re-break the split modules it was
    widened for. The distinction belongs in the CENSUS, which is the layer that has both facts.
    """
    return suite_discovery.is_suite(module.read_text(encoding="utf-8", errors="replace"))


def coverage(directory: Path) -> Coverage:
    """Return which modules have a suite, hold cases inline, delegate, dispatch, or have none.

    ⚑ THE ORDER OF THE TESTS IS THE POLICY. A module with a sibling suite is COVERED even if a
    vestigial inline `selftest()` remains, because the sibling is what the split was for. A tail
    beats a dispatch for the same reason in reverse: a module with both HAS cases, so the work it
    owes is the split, and the dispatch is how those cases are already reached. And a dispatch
    that FORWARDS is separated from one that does not, because only the second owes anything.
    """
    covered: list[str] = []
    tailed: list[str] = []
    dispatch: list[str] = []
    delegating: list[str] = []
    uncovered: list[str] = []
    for path in modules(directory):
        if has_suite(path):
            covered.append(path.name)
        elif has_tail_suite(path):
            tailed.append(path.name)
        elif not is_dispatch_only(path):
            uncovered.append(path.name)
        elif delegates_to(path) is not None:
            delegating.append(path.name)
        else:
            dispatch.append(path.name)
    return Coverage(
        covered=tuple(covered),
        uncovered=tuple(uncovered),
        tailed=tuple(tailed),
        dispatch_only=tuple(dispatch),
        delegating=tuple(delegating),
    )


def uncovered_among(names: Iterable[str], directory: Path | None = None) -> tuple[str, ...]:
    """Return which of `names` have no suite — the population a batch change cannot verify.

    ⚑ THE ARGUMENT IS THE BATCH, NOT THE DIRECTORY. After a change touching N files, the question
    is which of THOSE N nothing catches — not the tree's overall coverage, which is a different
    and less actionable number.
    """
    base = directory if directory is not None else corpus.ROOT / "substrate"
    # ⚑ A MODULE WITH AN INLINE SUITE IS STILL REPORTED HERE, because the question this mode
    # answers is what a batch change cannot verify — and an inline suite does not verify a batch
    # any better than none: it cannot run without importing the module under test. `coverage`
    # separates the shapes so the DEBT is legible; this mode is about REACH, and inline has none.
    return tuple(
        sorted(name for name in names if (base / name).exists() and not has_suite(base / name))
    )


def bounds() -> tuple[str, ...]:
    """Return the caveats every coverage answer carries, whichever mode asked.

    ⚑⚑⚑ THE SECOND RENDERING PATH INHERITED NEITHER, WHICH IS WHY THIS IS A FUNCTION. `render`
    appended both footers as literals, and `suite_gap_report`'s NAMED-BATCH branch builds its own
    ratio line and returns — so asking about a specific batch emitted no bound at all (gate-G343).
    That is the branch a reader uses when weighing a change they just made, which is exactly when
    the caveat matters most. A shared reader is what makes the two answers carry the same warning.

    ⚑⚑ THE RENDER IS NOT SHARED, AND THAT IS DELIBERATE RATHER THAN A GAP. `uncovered_among`
    answers a DIFFERENT question — reach over a batch — and reports a module with an inline suite
    as uncovered, because an inline suite cannot run without importing the module under test.
    `coverage` separates those shapes so the debt is legible. Building a `Coverage` from a name
    list to unify the renders would flatten a distinction this module states; the FOOTER is the
    part both answers genuinely share.

    ⚑ A CAVEAT KEPT IN PROSE GETS SUMMARISED AWAY (⟡bounds-in-band), and a caveat that reaches one
    of two call paths is the same failure with a smaller blast radius.
    """
    return (
        (
            "   ⚑ NOT A DEFECT LIST. A module without a suite is one whose changes nothing "
            "catches —\n     which is a fact a reader weighing a batch needs, not a verdict "
            "on the module."
        ),
        (
            "   ⚑ AND HAVING A SUITE IS NOT PASSING ONE. This counts a sibling that EXISTS, "
            "so a\n     failing suite is coverage here — ask `run_selftests` for outcome."
        ),
    )


def render(found: Coverage, limit: int = 40) -> str:
    """Return the coverage as a reader sees it.

    ⚑ EACH SHAPE IS RENDERED SEPARATELY AND SAYS WHAT IT OWES, INCLUDING WHEN THAT IS NOTHING. A
    merged list is a line a reader acts on with the wrong tool — measured twice, once on a split
    that had nothing to split and once on two CLIs that would have received vacuous suites.

    ⚑⚑⚑ AND THE COVERED SIDE CARRIES ITS OWN BOUND, WHICH IT DID NOT UNTIL A RED SUITE WAS
    COUNTED. The footer bounded the UNCOVERED list — *not a verdict on the module* — and nothing
    bounded the other half, which is where the false reading lives: a reader sees the ratio and
    takes it for verification. Measured: `module_replace_selftest.py` was written failing two arms
    and left untracked, and this census moved by one with it counted (gate-G341).

    ⚑⚑ THE PREDICATE IS EXISTENCE AND THAT IS CORRECT RATHER THAN A DEFECT. This module exists
    because *a green suite run is a fact about the modules that have suites* — its job is to make
    the rest READABLE so a vacuous pass becomes a bounded one. Joining it to outcome would collapse
    the distinction it was built to preserve: a suite that fails is still coverage, and a module
    with no suite is still the population a green run says nothing about. So the bound is STATED,
    not repaired — and `run_selftests` is named, because a reader who wants outcome needs the
    reader that has it.

    ⚑ THE CAVEATS COME FROM `bounds`, NOT FROM LITERALS HERE, so the named-batch path carries the
    same ones rather than silently omitting both (gate-G343).
    """
    lines = [f"{found.ratio} module(s) have a suite; {len(found.uncovered)} do not"]
    lines.extend(f"   {name}" for name in found.uncovered[:limit])
    if len(found.uncovered) > limit:
        lines.append(f"   … and {len(found.uncovered) - limit} more")
    if found.tailed:
        lines.append(
            f"   {len(found.tailed)} carry cases in their own TAIL — owed a SPLIT (module_trim):"
        )
        lines.extend(f"   ~ {name}" for name in found.tailed[:limit])
    if found.dispatch_only:
        lines.append(
            f"   {len(found.dispatch_only)} DISPATCH --selftest reaching nothing "
            "— owed a NEW SUITE:"
        )
        lines.extend(f"   ? {name}" for name in found.dispatch_only[:limit])
    if found.delegating:
        lines.append(
            f"   {len(found.delegating)} DELEGATE --selftest to the suite of the reader "
            "they wrap — owed NOTHING:"
        )
        lines.extend(f"   → {name}" for name in found.delegating[:limit])
    lines.extend(bounds())
    return "\n".join(lines)
