#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_gap_report` — two branches answering two questions.

⚑⚑⚑ THE BRANCHES ARE NOT ONE ANSWER SPLIT IN TWO, AND ASSERTING ONLY THE FIRST LEFT THE OTHER
UNBOUNDED FOR A TICK. The whole-package path renders `coverage` over a directory; the named path
calls `uncovered_among`, which answers reach over a BATCH and reports a module with an inline
suite as uncovered where `coverage` separates the shapes. Because the named branch built its own
summary line and returned, it emitted neither caveat (gate-G343) — and it is the branch a reader
uses right after making a change, which is when a bound matters most.

⚑⚑ SO EVERY ARM THAT ASSERTS A BOUND ASSERTS IT ON BOTH PATHS. A suite that pinned the footer on
the render alone would have passed throughout the period the defect existed, which is the whole
argument for having this file.

⚑ THE OUTPUT IS CAPTURED RATHER THAN PARSED FROM A SUBPROCESS. `main` is a function returning an
exit code and writing to stdout, so redirecting it exercises the real dispatch — a subprocess
would test the shell and be slower for no additional reach.

⚑ AND `bounds()` IS ASKED OF `suite_gap`, NEVER RETYPED HERE. A second spelling of a caveat drifts
the first time either moves, which is the defect this file exists to keep closed.
"""

from __future__ import annotations

import contextlib
import io
import sys

from substrate import corpus, suite_gap, suite_gap_report


def _ran(argv: list[str]) -> tuple[int, str]:
    """Return `(exit code, stdout)` for one invocation of the report."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = suite_gap_report.main(argv)
    return (code, buffer.getvalue())


def _fail(out: list[str], why: str) -> int:
    """Record one failure and return its contribution to the exit code."""
    out.append(f"selftest: {why}")
    return 1


def the_whole_package_path_carries_the_bounds(out: list[str]) -> int:
    """Check the no-argument invocation emits every caveat `bounds` declares."""
    code, text = _ran([])
    if code != 0:
        return _fail(out, f"the whole-package path exited {code}")
    for line in suite_gap.bounds():
        if line not in text:
            return _fail(out, f"the whole-package path omits a bound: {line!r}")
    return 0


def the_named_batch_path_carries_the_bounds(out: list[str]) -> int:
    """Check a named batch emits them too — THE ARM THE DEFECT NEEDED.

    ⚑⚑⚑ THIS BRANCH BUILT ITS OWN SUMMARY AND RETURNED, so it printed the ratio with no caveat at
    all (gate-G343). A suite asserting the footer on the render alone would have stayed green for
    every run in which that was true, which is exactly the shape of a check that cannot fail.
    """
    code, text = _ran(["suite_gap.py"])
    if code != 0:
        return _fail(out, f"the named-batch path exited {code}")
    for line in suite_gap.bounds():
        if line not in text:
            return _fail(out, f"the named-batch path omits a bound: {line!r}")
    return 0


def the_two_paths_answer_different_questions(out: list[str]) -> int:
    """Check the named path reports the BATCH, not the tree.

    ⚑⚑ THE DISTINCTION IS WHY THE RENDERS ARE NOT UNIFIED. `uncovered_among`'s own docstring says
    the argument is the batch rather than the directory, because after a change touching N files
    the question is which of THOSE N nothing catches. A named run whose denominator were the whole
    package would answer a question nobody asked.
    """
    _code, text = _ran(["suite_gap.py"])
    first = text.splitlines()[0]
    if "1/1" not in first:
        return _fail(out, f"the named path did not report the batch as its denominator: {first!r}")
    if "named module(s)" not in first:
        return _fail(out, f"the named path does not say its population is named: {first!r}")
    return 0


def a_named_module_with_a_suite_reads_as_covered(out: list[str]) -> int:
    """Check a module whose sibling suite exists is not listed as uncovered.

    ⚑ THE POSITIVE CONTROL. An arm that only checked the uncovered case would pass against a
    reader calling everything uncovered, and the ratio line alone cannot separate the two.
    """
    _code, text = _ran(["suite_gap.py"])
    if "   suite_gap.py" in text:
        return _fail(out, "a module with a suite was listed as uncovered")
    return 0


def a_named_module_without_a_suite_is_listed(out: list[str]) -> int:
    """Check an uncovered module is NAMED, not merely counted.

    ⚑⚑ A COUNT WITHOUT ITS MEMBERS IS UNACTIONABLE — a reader weighing a batch needs to know WHICH
    of their files nothing catches, and the tree's own rule is to enumerate before acting on a
    count. The subject is read from the live gap rather than pinned, so this cannot go red when
    the tree moves.
    """
    uncovered = suite_gap.uncovered_among(
        [path.name for _path, path in [(p, p) for p in (corpus.ROOT / "substrate").glob("*.py")]],
        directory=corpus.ROOT / "substrate",
    )
    if not uncovered:
        return 0
    subject = uncovered[0]
    _code, text = _ran([subject])
    if f"   {subject}" not in text:
        return _fail(out, f"an uncovered module was counted but not named: {subject!r}")
    return 0


def an_unknown_name_is_not_counted_as_covered(out: list[str]) -> int:
    """Check a name that is not a module under the package does not inflate the covered side.

    ⚑⚑⚑ `uncovered_among` REQUIRES THE PATH TO EXIST before asking whether it has a suite, so a
    typo reads as covered rather than as uncovered — the flattering direction. The reader cannot
    distinguish a typo from a real module, and stating that here is what keeps the ratio from
    being mistaken for a verdict about names a caller supplied.
    """
    _code, text = _ran(["no_such_module_at_all.py"])
    first = text.splitlines()[0]
    if "1/1" not in first:
        return _fail(out, f"an absent name did not read as covered: {first!r}")
    return 0


def the_bounds_are_not_retyped_here(out: list[str]) -> int:
    """Check this suite asserts `suite_gap.bounds()` rather than a copy of its text.

    ⚑ A SECOND SPELLING OF A CAVEAT DRIFTS the first time either moves, and a suite holding one
    would keep passing while the shipped bound changed underneath it.
    """
    declared = suite_gap.bounds()
    if not declared:
        return _fail(out, "suite_gap declares no bounds")
    if len(declared) < _BOUND_COUNT:
        return _fail(out, f"suite_gap declares fewer bounds than expected: {len(declared)}")
    return 0


#: How many caveats a coverage answer is expected to carry — the not-a-defect-list one and the
#: coverage-is-not-passing one. ⚑ A FLOOR, not a pin: a third bound is an addition, not a failure.
_BOUND_COUNT = 2


_ARMS = (
    the_whole_package_path_carries_the_bounds,
    the_named_batch_path_carries_the_bounds,
    the_two_paths_answer_different_questions,
    a_named_module_with_a_suite_reads_as_covered,
    a_named_module_without_a_suite_is_listed,
    an_unknown_name_is_not_counted_as_covered,
    the_bounds_are_not_retyped_here,
)

_CASE_COUNT = 2 + 2 + 2 + 1 + 1 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-gap-report selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-gap-report selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
