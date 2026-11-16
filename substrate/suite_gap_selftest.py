#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_gap` — the reading that turns a vacuous pass into a bounded one.

⚑⚑⚑ THE MOTIVATING INCIDENT IS ONE ARM: `ratchet_render.py` has no suite, so a 58-file batch that
verified itself with "the suites still pass" said NOTHING about it — and its converted record broke
an unrelated gate through seven callers in three other files. The arm asserting that a real
uncovered module is found is the whole reason this exists.

⚑⚑ AND THE DENOMINATOR ARMS MATTER AS MUCH AS THE MEMBERSHIP ONES. A count of uncovered modules
with no total is a number a reader cannot weigh — the same defect this repo records about every
census that reports a numerator alone.

⚑ THE SUITES THEMSELVES ARE EXCLUDED FROM THE POPULATION, pinned because including them would
inflate the denominator with files the convention never applies to and make coverage read better
than it is — an error in the flattering direction, which is the one that goes unnoticed.

⚑⚑⚑ AND THE DEBT CATEGORY SPANNED SHAPES OWING OPPOSITE WORK (⟡inline-spans-two-shapes). A module
carrying cases in its own TAIL owes a SPLIT; one that merely DISPATCHES `--selftest` reaching
nothing owes a suite that has to be WRITTEN; one that DELEGATES to the suite of the reader it
wraps owes NOTHING at all. Merged, the census sent a reader to `module_trim` for a split there was
nothing to perform, and then flagged two delegating CLIs as owed suites that would have been
vacuous. Every shape is pinned here as a FIXTURE rather than a live module: the live inline list
was empty when these were written, and this file's live-tree witnesses have already expired twice
in two turns by naming victims that then got fixed.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import corpus, suite_gap

# What the fixtures write.
_MODULE = '"""A module."""\n'

# ⚑ THE THREE DISPATCH SHAPES, AS SOURCE, and each owes something different. `_TAIL` is a
# top-level `def selftest` — the object `module_trim` moves, so the cases EXIST and a split is
# owed. `_DISPATCH` answers the flag and reaches nothing, so a suite must be written. `_DELEGATES`
# answers it by calling ANOTHER module's suite, so nothing is owed — and its import sits inside
# the `__main__` guard, which is the shape that defeated the first implementation.
_TAIL = "def selftest() -> int:\n    return 0\n"
_DISPATCH = (
    'import sys\n\n\nif __name__ == "__main__":\n'
    '    sys.exit(0 if "--selftest" in sys.argv else 2)\n'
)
_DELEGATES = (
    'import sys\n\n\nif __name__ == "__main__":\n'
    '    if "--selftest" in sys.argv:\n'
    "        from substrate import reader_selftest\n"
    "        sys.exit(reader_selftest.selftest())\n"
    "    sys.exit(0)\n"
)

# A module known to have a suite — the discriminating half of the live-tree arm.
#
# ⚑⚑ THIS WITNESS HAS ALREADY BEEN REPOINTED ONCE, WHICH IS THE ARM WORKING. It named
# `ratchet_render.py` — the module whose missing suite let a conversion break the type gate — and
# went red the moment that suite landed, with a message saying to repoint rather than delete.
# **A case that goes green because the world improved has stopped measuring**, so the property
# replaced the instance and only the covered witness remains.
_COVERED = "tool_gap.py"


def _tree(directory: Path, *names: str) -> None:
    """Write each named file as a trivial module."""
    for name in names:
        (directory / name).write_text(_MODULE, encoding="utf-8")


def a_module_with_a_suite_is_covered(out: list[str]) -> int:
    """Check the `<module>_selftest.py` convention is recognised."""
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        _tree(base, "thing.py", "thing_selftest.py")
        if not suite_gap.has_suite(base / "thing.py"):
            out.append("selftest: a module with its suite beside it read as uncovered")
            return 1
    return 0


def a_module_without_a_suite_is_uncovered(out: list[str]) -> int:
    """Check a bare module is reported."""
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        _tree(base, "lonely.py")
        if suite_gap.has_suite(base / "lonely.py"):
            out.append("selftest: a module with no suite read as covered")
            return 1
    return 0


def a_suite_is_not_itself_a_module(out: list[str]) -> int:
    """Check suites are excluded from the population — THE FLATTERING-ERROR ARM.

    ⚑⚑ INCLUDING THEM WOULD INFLATE THE DENOMINATOR with files the convention never applies to,
    making coverage read better than it is. An error in the flattering direction is the one that
    goes unnoticed.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        _tree(base, "thing.py", "thing_selftest.py")
        names = [path.name for path in suite_gap.modules(base)]
        if "thing_selftest.py" in names:
            out.append(f"selftest: a suite was counted as a module: {names!r}")
            return 1
        if names != ["thing.py"]:
            out.append(f"selftest: the population is {names!r}")
            return 1
    return 0


def a_dunder_file_is_not_a_module(out: list[str]) -> int:
    """Check `__init__.py` and friends are excluded."""
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        _tree(base, "thing.py", "__init__.py")
        names = [path.name for path in suite_gap.modules(base)]
        if "__init__.py" in names:
            out.append(f"selftest: a dunder file was counted: {names!r}")
            return 1
    return 0


def the_split_reports_both_sides(out: list[str]) -> int:
    """Check coverage names what is covered AND what is not."""
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        _tree(base, "has.py", "has_selftest.py", "lacks.py")
        found = suite_gap.coverage(base)
        if found.covered != ("has.py",):
            out.append(f"selftest: covered is {found.covered!r}")
            return 1
        if found.uncovered != ("lacks.py",):
            out.append(f"selftest: uncovered is {found.uncovered!r}")
            return 1
    return 0


def the_denominator_is_reported(out: list[str]) -> int:
    """Check the total is available — a numerator alone cannot be weighed."""
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        _tree(base, "has.py", "has_selftest.py", "lacks.py")
        found = suite_gap.coverage(base)
        expected = 2
        if found.total != expected:
            out.append(f"selftest: the total is {found.total}, expected {expected}")
            return 1
        if found.ratio != "1/2":
            out.append(f"selftest: the ratio is {found.ratio!r}")
            return 1
    return 0


def every_module_lands_in_exactly_one_category(out: list[str]) -> int:
    """Check the categories PARTITION the population — the arm each split makes newly necessary.

    ⚑⚑⚑ FOUR CATEGORIES CAN OVERLAP OR LEAK IN WAYS TWO CANNOT, and the denominator is computed
    by SUMMING them. A module counted twice inflates the total and deflates the ratio; one counted
    nowhere vanishes from a census whose entire purpose is that nothing vanishes from it. Neither
    shows up as an error — both just move a number.

    ⚑ SO IT IS ASSERTED OVER A DIRECTORY HOLDING ONE OF EVERY SHAPE AT ONCE. Checking each shape
    in isolation, which the other arms do, cannot see a leak that only appears when they coexist.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        (base / "reader_selftest.py").write_text(_MODULE + _TAIL, encoding="utf-8")
        (base / "reader.py").write_text(_MODULE, encoding="utf-8")
        (base / "tailed.py").write_text(_MODULE + _TAIL, encoding="utf-8")
        (base / "bare.py").write_text(_MODULE + _DISPATCH, encoding="utf-8")
        (base / "wrapper.py").write_text(_MODULE + _DELEGATES, encoding="utf-8")
        (base / "plain.py").write_text(_MODULE, encoding="utf-8")
        found = suite_gap.coverage(base)
        buckets = (
            found.covered,
            found.uncovered,
            found.tailed,
            found.dispatch_only,
            found.delegating,
        )
        placed = [name for bucket in buckets for name in bucket]
        population = sorted(path.name for path in suite_gap.modules(base))
        if sorted(placed) != population:
            out.append(
                f"selftest: the categories place {sorted(placed)!r}, population is "
                f"{population!r} — a module is double-counted or lost"
            )
            return 1
        if found.total != len(population):
            out.append(f"selftest: the total is {found.total}, population is {len(population)}")
            return 1
    return 0


def a_batch_is_asked_about_rather_than_a_directory(out: list[str]) -> int:
    """Check `uncovered_among` answers about the CHANGED files, not the tree.

    ⚑ AFTER A CHANGE TOUCHING N FILES, the question is which of THOSE N nothing catches. The
    tree's overall coverage is a different and less actionable number.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        _tree(base, "a.py", "a_selftest.py", "b.py", "c.py", "c_selftest.py")
        got = suite_gap.uncovered_among(["a.py", "b.py"], directory=base)
        if got != ("b.py",):
            out.append(f"selftest: the uncovered batch members are {got!r}")
            return 1
    return 0


def a_name_not_present_is_not_reported(out: list[str]) -> int:
    """Check a name with no file is omitted rather than counted as uncovered.

    ⚑ ABSENT AND UNCOVERED ARE DIFFERENT FACTS. Reporting a nonexistent module as lacking a suite
    would send a reader to write one for a file that is not there.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        _tree(base, "a.py", "a_selftest.py")
        if suite_gap.uncovered_among(["nonesuch.py"], directory=base):
            out.append("selftest: an absent module was reported as uncovered")
            return 1
    return 0


def the_census_reads_the_live_tree(out: list[str]) -> int:
    """Check the census answers about the real package — THE LIVE-TREE ARM.

    ⚑⚑⚑ THIS ARM NAMED A VICTIM AND EXPIRED TWICE IN TWO TURNS. It pinned `ratchet_render.py` as
    uncovered — the module whose missing suite let a conversion break the type gate — went red
    when that suite landed, was repointed to `gate_main.py`, and went red again when THAT suite
    landed. **A witness that must be repointed every time the work succeeds is friction the work
    itself creates**, and the third repointing would have been mechanical, which is where a reader
    starts editing the case to make it pass.

    ⚑⚑ SO IT ASSERTS THE PROPERTY, NOT AN INSTANCE. What must hold is that the census READS the
    live tree rather than reporting a constant: some modules covered, some not, and a known
    covered one never reported as uncovered. All three survive the population improving, which is
    what a witness has to do.

    ⚑ AND THE `_COVERED` HALF IS THE DISCRIMINATOR. Without it, a census reporting EVERY module as
    uncovered would satisfy the other halves — the constant-predicate failure a positive-only
    assertion cannot see.
    """
    base = corpus.ROOT / "substrate"
    found = suite_gap.coverage(base)
    if not found.covered:
        out.append("selftest: the live census reports NOTHING covered — a constant, not a read")
        return 1
    if not found.uncovered:
        out.append(
            "selftest: the live census reports nothing uncovered — a fully covered tree, "
            "or a constant"
        )
        return 1
    got = suite_gap.uncovered_among([_COVERED], directory=base)
    if got:
        out.append(f"selftest: {_COVERED} has a suite and read as uncovered: {got!r}")
        return 1
    return 0


# ⚑ THE OLD NAME STAYS REGISTERED so the rename and its registration land together — the
# atomicity rule this session measured at six wasted refusals. The alias is deleted when the
# `_ARMS` tuple is next edited for another reason.
the_motivating_module_is_found = the_census_reads_the_live_tree


def an_inline_selftest_is_not_coverage(out: list[str]) -> int:
    """Check a module with cases in its own tail lands in `inline`, not `covered` — THE ARM.

    ⚑⚑⚑ THIS CENSUS BRIEFLY COUNTED INLINE SUITES AS COVERED and reported the population
    improving from 121/145 to 128/145 with nothing written. The runner does execute them, which
    is why it looked like a convention; it is the UNSPLIT state, and a census that calls it
    coverage hides every split that is owed.

    ⚑ AND IT MUST NOT LAND IN `uncovered` EITHER — that would send a reader to write a duplicate
    suite for a module that already has cases, which is what nearly happened to `baseline_io`.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        (base / "tailed.py").write_text(_MODULE + _TAIL, encoding="utf-8")
        found = suite_gap.coverage(base)
        if "tailed.py" in found.covered:
            out.append("selftest: an inline selftest was counted as COVERAGE")
            return 1
        if "tailed.py" in found.uncovered:
            out.append(
                "selftest: an inline selftest was counted as UNCOVERED — a reader would "
                "write a duplicate"
            )
            return 1
        if found.inline != ("tailed.py",):
            out.append(f"selftest: the inline population is {found.inline!r}")
            return 1
    return 0


def the_two_inline_shapes_are_distinguished(out: list[str]) -> int:
    """Check a TAIL and a bare DISPATCH land in different buckets — ⟡inline-spans-two-shapes.

    ⚑⚑⚑ THE MERGED CATEGORY SENT A DISPATCH TO THE WRONG TOOL. `ratchet_suites.py` was briefed
    for a SPLIT on the strength of its INLINE flag; it defines no `selftest` at all, so there was
    nothing to move, and `module_trim --dry-run` refused with *"no top-level definition named:
    selftest"*. The two shapes owe OPPOSITE work — a tail owes a split, a bare dispatch owes a
    suite that does not exist yet — and one bucket cannot say which.

    ⚑⚑ BOTH SHAPES ARE FIXTURES, NOT LIVE MODULES, AND THAT IS DELIBERATE. The live inline list
    was EMPTY when this was written — every tail had just been split — so a case naming a real
    module would have had nothing to name. And this file's live-tree witnesses expired TWICE IN
    TWO TURNS by naming victims that then got fixed. A fixture pins the property against a tree
    that keeps improving.

    ⚑ AND EACH HALF DISCRIMINATES THE OTHER. A predicate that always answered "tail" satisfies
    the tail half; one that always answered "dispatch" satisfies the dispatch half. Asserting
    both, over one directory, in one call, is what neither constant survives.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        (base / "tailed.py").write_text(_MODULE + _TAIL, encoding="utf-8")
        (base / "cli.py").write_text(_MODULE + _DISPATCH, encoding="utf-8")
        found = suite_gap.coverage(base)
        if found.tailed != ("tailed.py",):
            out.append(
                f"selftest: the TAIL population is {found.tailed!r} — a split is owed "
                "only where cases exist"
            )
            return 1
        if found.dispatch_only != ("cli.py",):
            out.append(
                f"selftest: the DISPATCH-ONLY population is {found.dispatch_only!r} — a "
                "module with no cases was read as having some"
            )
            return 1
        if found.inline != ("cli.py", "tailed.py"):
            out.append(f"selftest: inline is no longer the union of the two: {found.inline!r}")
            return 1
    return 0


def a_delegating_dispatch_owes_nothing(out: list[str]) -> int:
    """Check a dispatch FORWARDING to a real suite is separated from one reaching nothing.

    ⚑⚑⚑ THE SPLIT CATEGORY OVER-REPORTED ON ITS FIRST LIVE RUN, WHICH IS HOW THIS ARM EXISTS.
    `kind_partition_show.py` and `md_spans_show.py` were flagged as owed a NEW SUITE. Mechanically
    true — they answer `--selftest` and define nothing — and wrong as an instruction: each guard
    imports the suite of the reader it wraps and calls it, so every branch a case could pin is
    already covered at the far end. A suite written for either would duplicate that one or assert
    that a passthrough passes through, and a vacuous suite written to move a number is worse than
    an honest gap.

    ⚑⚑ THE DISCRIMINATING HALF IS THE BARE DISPATCH IN THE SAME DIRECTORY. A predicate that called
    every dispatch a delegation would satisfy the first assertion and empty the category that owes
    real work — the flattering direction. Both are asserted from one `coverage` call, which is
    what neither constant survives.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        (base / "wrapper.py").write_text(_MODULE + _DELEGATES, encoding="utf-8")
        (base / "reader_selftest.py").write_text(_MODULE + _TAIL, encoding="utf-8")
        (base / "bare.py").write_text(_MODULE + _DISPATCH, encoding="utf-8")
        found = suite_gap.coverage(base)
        if found.delegating != ("wrapper.py",):
            out.append(f"selftest: the DELEGATING population is {found.delegating!r}")
            return 1
        if found.dispatch_only != ("bare.py",):
            out.append(
                f"selftest: a bare dispatch was absorbed into delegation: {found.dispatch_only!r}"
            )
            return 1
        if "wrapper.py" in found.inline:
            out.append("selftest: a delegator was counted as DEBT — it owes no work")
            return 1
    return 0


def a_dispatch_forwarding_nowhere_is_not_delegation(out: list[str]) -> int:
    """Check the forwarded-to suite must EXIST — the flattering-error arm for delegation.

    ⚑⚑ A GUARD IMPORTING A DELETED SUITE FORWARDS TO NOTHING, and reading it as covered would make
    the census flatter than the tree. The name is in the AST either way, so an AST-only test
    cannot tell a live delegation from a dangling one; the filesystem check is what can.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        # The same guard, with no `reader_selftest.py` beside it.
        (base / "wrapper.py").write_text(_MODULE + _DELEGATES, encoding="utf-8")
        found = suite_gap.coverage(base)
        if found.delegating:
            out.append(
                f"selftest: a dispatch forwarding to an ABSENT suite read as delegating: "
                f"{found.delegating!r}"
            )
            return 1
        if found.dispatch_only != ("wrapper.py",):
            out.append(
                f"selftest: a dangling forward is {found.dispatch_only!r}, expected a "
                "bare dispatch owed a suite"
            )
            return 1
    return 0


def the_delegation_edge_is_read_in_a_guard(out: list[str]) -> int:
    """Check a `__main__`-guarded import is seen — THE BLIND-INSTRUMENT ARM.

    ⚑⚑⚑ THE FIRST CUT OF `delegates_to` READ `deferred_dotted` ALONE AND SAW NEITHER DELEGATOR.
    The reasoning was that an import inside a `__main__` guard is "not module level"; the code
    says otherwise — `import_edges._eager_bodies` descends an `ast.If` body, because it answers
    *what executes when this file runs*, and a guard body does. The census reported both live
    delegators as bare dispatches and looked entirely plausible doing it.

    ⚑ SO THE UNION OF BOTH READINGS IS PINNED, AND FROM BOTH SIDES. A guard import and a
    function-body import each name a real forward; an implementation consulting only one reading
    reports the other's population as absent, which is a fact about the instrument reported as a
    fact about the tree.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        (base / "reader_selftest.py").write_text(_MODULE + _TAIL, encoding="utf-8")
        (base / "guarded.py").write_text(_MODULE + _DELEGATES, encoding="utf-8")
        if suite_gap.delegates_to(base / "guarded.py") != "reader_selftest":
            out.append(
                "selftest: a __main__-GUARDED forward was not seen — the eager reading is missing"
            )
            return 1
        (base / "deep.py").write_text(
            _MODULE + "def run() -> int:\n    from substrate import reader_selftest\n"
            "    return reader_selftest.selftest()\n",
            encoding="utf-8",
        )
        if suite_gap.delegates_to(base / "deep.py") != "reader_selftest":
            out.append(
                "selftest: a FUNCTION-BODY forward was not seen — the deferred reading is missing"
            )
            return 1
    return 0


def an_ordinary_import_is_not_a_delegation(out: list[str]) -> int:
    """Check only a SUITE counts as a forward target — not any package import.

    ⚑ EVERY CLI IN THIS PACKAGE IMPORTS THE READER IT WRAPS. If any `substrate.*` import counted,
    every dispatching module would read as delegating and the category that owes real work would
    empty itself — the same over-admitting failure `suite_discovery` has recorded twice.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        (base / "reader.py").write_text(_MODULE, encoding="utf-8")
        (base / "cli.py").write_text(
            "from substrate import reader\n" + _MODULE + _DISPATCH, encoding="utf-8"
        )
        if suite_gap.delegates_to(base / "cli.py") is not None:
            out.append("selftest: importing a plain module read as forwarding to its suite")
            return 1
        found = suite_gap.coverage(base)
        if "cli.py" not in found.dispatch_only:
            out.append(f"selftest: a bare dispatch over a reader is {found.dispatch_only!r}")
            return 1
    return 0


def a_dispatch_with_a_sibling_is_simply_covered(out: list[str]) -> int:
    """Check a SPLIT module is not re-reported as debt — the shape the split produces.

    ⚑⚑ THIS IS WHY `suite_discovery` IS NOT NARROWED TO FIX THE MERGED CATEGORY. A split module
    KEEPS its `--selftest` dispatch and exports the body to a sibling; that is the end state the
    whole exercise drives at. Requiring a local body in `is_suite` once erased three real suites,
    so the fix lives here, in the census — and this arm pins that a correctly split module reads
    as COVERED rather than as the debt it just stopped being.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        (base / "split.py").write_text(_MODULE + _DISPATCH, encoding="utf-8")
        (base / "split_selftest.py").write_text(_MODULE + _TAIL, encoding="utf-8")
        found = suite_gap.coverage(base)
        if found.covered != ("split.py",):
            out.append(f"selftest: a split module reads as {found.covered!r}, not covered")
            return 1
        if found.inline:
            out.append(f"selftest: a split module still read as inline debt: {found.inline!r}")
            return 1
    return 0


def a_nested_or_quoted_selftest_is_not_a_tail(out: list[str]) -> int:
    """Check the tail test finds a TOP-LEVEL definition, not the word — THE TOOL-AGREEMENT ARM.

    ⚑⚑⚑ THE CENSUS AND THE SPLITTING TOOL MUST MEAN THE SAME THING BY "a tail". `module_trim`
    moves a TOP-LEVEL `def selftest`, and refuses anything else with *"no top-level definition
    named: selftest"*. The substring test this module used also matches a call `runner.selftest()`,
    a method inside a class, and the word inside a docstring — so it would report a split that the
    only tool able to perform one would refuse.

    ⚑ AND THIS IS THE OVER-ADMITTING DIRECTION, which is the one that produced the measured
    misdirection. A module wrongly called `tailed` sends a reader to move cases that are not
    there; the census must be at least as narrow as the tool it points at.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        (base / "caller.py").write_text(
            _MODULE + "class Runner:\n    def selftest(self) -> int:\n        return 0\n",
            encoding="utf-8",
        )
        if suite_gap.has_tail_suite(base / "caller.py"):
            out.append("selftest: a METHOD named selftest was read as a splittable tail")
            return 1
        (base / "mentions.py").write_text(
            '"""Run selftest() to check — def selftest() is not defined here."""\n',
            encoding="utf-8",
        )
        if suite_gap.has_tail_suite(base / "mentions.py"):
            out.append("selftest: a DOCSTRING mention was read as a splittable tail")
            return 1
    return 0


def a_private_tail_is_still_a_tail(out: list[str]) -> int:
    """Check a top-level `_selftest` reads as a tail — THE UNDER-ADMITTING DIRECTION.

    ⚑⚑⚑ THIS IS THE ARM THE SUITE DID NOT HAVE, AND ITS ABSENCE COST NINE FALSE ROWS. The pattern
    was anchored on `def selftest`, so the PRIVATE spelling could not match — and nine modules
    (`iface_cost`, `iface_readers`, `sandbox_connect`, …) that define `_selftest` at top level and
    call it from their dispatch fell through to *"DISPATCH --selftest reaching nothing — owed a NEW
    SUITE"*. Measured against the modules themselves: `iface_cost --selftest` answers 5/5 and
    `iface_readers` 8/8. The census proposed nine suites that already existed.

    ⚑⚑ AND THE TWO ARMS ABOVE BOTH GUARD THE OTHER DIRECTION, which is why the gap survived. A
    method, a call and a docstring mention are each asserted NOT to be a tail; nothing asserted
    that a real tail IS one, so a pattern matching too little passed the suite unchanged. That is
    `a passing arm says a check works, never that it is load-bearing` — the change that fixed this
    left 44/44 untouched in both directions until this case existed.

    ⚑ `module_trim` MOVES EITHER SPELLING, so admitting the private form keeps the census and the
    splitting tool agreeing about what a tail is — the invariant the sibling arms exist to protect.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        (base / "private.py").write_text(
            _MODULE + "def _selftest() -> int:\n    return 0\n", encoding="utf-8"
        )
        if not suite_gap.has_tail_suite(base / "private.py"):
            out.append("selftest: a top-level _selftest was NOT read as a splittable tail")
            return 1
        (base / "public.py").write_text(
            _MODULE + "def selftest() -> int:\n    return 0\n", encoding="utf-8"
        )
        if not suite_gap.has_tail_suite(base / "public.py"):
            out.append("selftest: a top-level selftest was NOT read as a splittable tail")
            return 1
    return 0


def a_tail_under_any_name_is_a_tail(out: list[str]) -> int:
    """Check a dispatch calling a LOCAL def is a tail whatever that def is named.

    ⚑⚑⚑ THE THIRD SPELLING, AND THE REASON THIS IS NOT A FOURTH REGEX. `type_scope` names its
    arms `_cases` and answers `--selftest` with 14 passing cases, and a predicate keyed on the
    NAME reported it as owed a NEW SUITE — the same error as the private-tail row, one name over.
    Widening the pattern again would fix this member and leave the class: the next module to spell
    it `_run_cases` reopens the finding.

    ⚑⚑ SO THE FACT IS STRUCTURAL — a `--selftest` guard that calls a top-level def IN THIS FILE.
    That is what `module_trim` moves and what makes the cases exist, and it is readable from the
    AST without knowing any name in advance. The sibling predicate `delegates_to` already reads
    the dispatch's FAR END this way; this reads its NEAR end.

    ⚑ BOTH DIRECTIONS. A dispatch that calls nothing local must still read as owing a NEW SUITE,
    or the category that sent a reader to `module_trim` with nothing to split comes back.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        (base / "named.py").write_text(
            _MODULE + "def _cases() -> tuple[int, int]:\n    return (1, 1)\n\n\n"
            "def main(argv: list[str]) -> int:\n"
            '    if "--selftest" in argv:\n'
            "        return _cases()[0]\n"
            "    return 0\n",
            encoding="utf-8",
        )
        if not suite_gap.has_tail_suite(base / "named.py"):
            out.append("selftest: a dispatch calling a local def was not read as a tail")
            return 1
        (base / "empty.py").write_text(
            _MODULE + "def main(argv: list[str]) -> int:\n"
            '    if "--selftest" in argv:\n'
            "        return 0\n"
            "    return 0\n",
            encoding="utf-8",
        )
        if suite_gap.has_tail_suite(base / "empty.py"):
            out.append("selftest: a dispatch reaching NOTHING was read as a tail")
            return 1
    return 0


def a_sibling_suite_beats_a_vestigial_tail(out: list[str]) -> int:
    """Check a module with BOTH reads as covered — the sibling is what the split was for."""
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        _tree(base, "both_selftest.py")
        (base / "both.py").write_text(_MODULE + _TAIL, encoding="utf-8")
        found = suite_gap.coverage(base)
        if found.covered != ("both.py",):
            out.append(f"selftest: covered is {found.covered!r}, expected the split module")
            return 1
        if found.inline:
            out.append(f"selftest: a split module still read as inline debt: {found.inline!r}")
            return 1
    return 0


def the_bounds_are_one_reader_both_paths_use(out: list[str]) -> int:
    """Check the caveats come from `bounds` so a second render path cannot omit them.

    ⚑⚑⚑ `suite_gap_report` HAS TWO BRANCHES AND ONE OF THEM BUILT ITS OWN SUMMARY, so asking
    about a named batch emitted no caveat at all (gate-G343) — the branch a reader uses when
    weighing a change they just made. A literal appended inside `render` reaches one call path by
    construction, and nothing said so.

    ⚑⚑ THE RENDER ITSELF IS NOT SHARED, DELIBERATELY. `uncovered_among` answers reach over a
    BATCH and counts an inline-suite module as uncovered, which `coverage` separates — unifying
    the renders would flatten that. The footer is the part both answers genuinely share, and this
    arm pins that it is ONE READER rather than two copies that drift.
    """
    text = "\n".join(suite_gap.bounds())
    if "NOT A DEFECT LIST" not in text:
        return _bound_fail(out, "bounds omits the not-a-defect-list caveat")
    if "NOT PASSING ONE" not in text:
        return _bound_fail(out, "bounds omits the coverage-is-not-passing caveat")
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        _tree(base, "lacks.py")
        rendered = suite_gap.render(suite_gap.coverage(base))
    for line in suite_gap.bounds():
        if line not in rendered:
            return _bound_fail(out, f"render does not use bounds: {line!r}")
    return 0


def _bound_fail(out: list[str], why: str) -> int:
    """Record one bound failure and return its contribution to the exit code."""
    out.append(f"selftest: {why}")
    return 1


def the_render_bounds_the_covered_side(out: list[str]) -> int:
    """Check the ratio says that HAVING a suite is not PASSING one.

    ⚑⚑⚑ THE FOOTER BOUNDED THE UNCOVERED LIST AND NOTHING BOUNDED THE OTHER HALF, which is where
    the false reading lives: a reader sees the ratio and takes it for verification. Measured —
    `module_replace_selftest.py` was written failing two arms and left untracked, and this census
    counted it and moved by one (gate-G341).

    ⚑⚑ THE PREDICATE IS NOT THE DEFECT. This module's whole purpose is that *a green run is a
    fact about the modules that have suites*, so a failing suite IS coverage and joining this to
    outcome would collapse the distinction it exists to preserve. The repair is a stated bound,
    and the bound must name `run_selftests` — a caveat that does not say where to get the other
    answer sends a reader nowhere.

    ⚑ IT IS ASSERTED ON THE RENDER rather than kept in a docstring, because a caveat in prose gets
    summarised away (⟡bounds-in-band) and this arm is what makes its removal visible.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        _tree(base, "lacks.py")
        text = suite_gap.render(suite_gap.coverage(base))
        # ⚑ THE ASSERTION IS THE EMITTED SPELLING, NOT A PARAPHRASE OF IT. A first cut tested
        # `"not PASSING"` against a line that reads `NOT PASSING ONE` in the emphasis block's
        # capitals — case-sensitive, absent, and four probes went into reasoning about where the
        # text had gone before one `--literal` call over the module settled it.
        if "NOT PASSING ONE" not in text:
            out.append("selftest: the render does not bound the covered side")
            return 1
        if "run_selftests" not in text:
            out.append("selftest: the bound does not name the reader that knows outcome")
            return 1
    return 0


def the_render_refuses_to_be_a_defect_list(out: list[str]) -> int:
    """Check the report says a missing suite is not itself a defect."""
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        _tree(base, "lacks.py")
        text = suite_gap.render(suite_gap.coverage(base))
        if "NOT A DEFECT LIST" not in text:
            out.append("selftest: the render presents the population as a defect list")
            return 1
        if "lacks.py" not in text:
            out.append("selftest: the render omits the uncovered module")
            return 1
    return 0


def the_render_names_the_work_each_shape_owes(out: list[str]) -> int:
    """Check the report tells a tail from a dispatch from a delegation — the reader-facing half.

    ⚑ SPLITTING THE CATEGORY IS NOT THE FIX IF THE RENDER MERGES IT AGAIN. What went wrong both
    times was a READER acting on a printed line, so the printed line is where the distinctions
    have to survive: SPLIT for one, NEW SUITE for the second, NOTHING for the third.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        (base / "reader_selftest.py").write_text(_MODULE + _TAIL, encoding="utf-8")
        (base / "tailed.py").write_text(_MODULE + _TAIL, encoding="utf-8")
        (base / "cli.py").write_text(_MODULE + _DISPATCH, encoding="utf-8")
        (base / "wrapper.py").write_text(_MODULE + _DELEGATES, encoding="utf-8")
        text = suite_gap.render(suite_gap.coverage(base))
        for owed in ("SPLIT", "NEW SUITE", "NOTHING"):
            if owed not in text:
                out.append(f"selftest: the render never says a shape owes {owed}")
                return 1
        for name in ("tailed.py", "cli.py", "wrapper.py"):
            if name not in text:
                out.append(f"selftest: the render omits {name}")
                return 1
    return 0


_ARMS = (
    a_module_with_a_suite_is_covered,
    a_module_without_a_suite_is_uncovered,
    a_suite_is_not_itself_a_module,
    a_dunder_file_is_not_a_module,
    the_split_reports_both_sides,
    the_denominator_is_reported,
    every_module_lands_in_exactly_one_category,
    a_batch_is_asked_about_rather_than_a_directory,
    a_name_not_present_is_not_reported,
    the_motivating_module_is_found,
    an_inline_selftest_is_not_coverage,
    the_two_inline_shapes_are_distinguished,
    a_delegating_dispatch_owes_nothing,
    a_dispatch_forwarding_nowhere_is_not_delegation,
    the_delegation_edge_is_read_in_a_guard,
    an_ordinary_import_is_not_a_delegation,
    a_dispatch_with_a_sibling_is_simply_covered,
    a_nested_or_quoted_selftest_is_not_a_tail,
    a_private_tail_is_still_a_tail,
    a_tail_under_any_name_is_a_tail,
    a_sibling_suite_beats_a_vestigial_tail,
    the_bounds_are_one_reader_both_paths_use,
    the_render_bounds_the_covered_side,
    the_render_refuses_to_be_a_defect_list,
    the_render_names_the_work_each_shape_owes,
)

_CASE_COUNT = (
    1
    + 1
    + 2
    + 1
    + 2
    + 2
    + 2
    + 1
    + 1
    + 2
    + 3
    + 3
    + 3
    + 2
    + 2
    + 2
    + 2
    + 2
    + 2
    + 2
    + 2
    + 2
    + 2
    + 4
    + 6
)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-gap selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-gap selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
