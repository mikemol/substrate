#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_census` — the fold, and the four zeros it must not bank.

⚑⚑⚑ THE VACUOUS ARM IS THE ONE A MEASURED DEFECT BOUGHT. `0/0` satisfies the record shape, and
`0 != 0` is False, so a suite that executed ZERO cases counted GREEN and moved neither total —
invisible in the summary. Eight real assertions never ran and the gate said green.

⚑ THE REACH ARM IS THE SAME ZERO ONE LAYER OVER. A suite that did not report must contribute NO
reach row: recording it as 0 banks the abort as its reading, and every later run then reads as
growth. Absent and zero are opposite, and only one of them is honest here.

⚑ THE KIND-BEFORE-THE-BRANCH ARM PINS A SHAPE, NOT A VALUE. The kind is a property of the RUN,
not of the reporting branch it happens to take — so a suite that reported nothing must still
carry a kind, which is what a reader needs to know where to look.

⚑ AND THE TWO PROSE ARMS ARE BOTH DIRECTIONS OF ONE CENSUS. A census that only ever checks its
positive case cannot distinguish "correctly empty" from "never populated", which is this repo's
recorded green-is-a-fact-about-the-census failure.
"""

from __future__ import annotations

import json
import sys

from substrate import suite_census, suite_record

# ⚑ THE PREFIX IS IMPORTED, NEVER RETYPED. A fixture spelling its own record prefix tests the
# author's retyping rather than the reader — the `census-keyed-on-one-spelling` shape, and the
# one this module's own subject records against itself.
_PREFIX = suite_record.RECORD_PREFIX

# How many distinct kinds two differently-broken suites must partition into.
_TWO_KINDS = 2

# The duration one fixture run reports, so the per-suite carry is checkable.
_ONE_DURATION = 1.5


def _record(passed: int, total: int, skipped: int = 0, reason: str = "") -> str:
    """Render a typed suite record the way a suite emits one."""
    body = {"passed": passed, "total": total, "skipped": skipped, "reason": reason}
    return _PREFIX + json.dumps(body)


def _run(label: str, output: str, returncode: int = 0, seconds: float = 0.0) -> suite_census.Run:
    """Build one captured run."""
    return suite_census.Run(label=label, output=output, returncode=returncode, seconds=seconds)


def a_green_suite_is_counted(out: list[str]) -> int:
    """Check a passing suite contributes its counts and refuses nothing."""
    bad = 0
    census = suite_census.fold([_run("a.py", _record(5, 5))])
    if (census.passed, census.declared, census.failed) != (5, 5, []):
        out.append(f"selftest: a green suite folded to {census.counts!r} / {census.failed!r}")
        bad += 1
    return bad


def a_vacuous_suite_is_refused(out: list[str]) -> int:
    """Check `0/0` refuses the run rather than reading green.

    ⚑ THE MEASURED DEFECT: `0 != 0` is False, so a zero-case suite moved neither total.
    """
    bad = 0
    census = suite_census.fold([_run("a.py", _record(0, 0))])
    if not census.failed:
        out.append("selftest: a vacuous 0/0 suite passed the fold")
        bad += 1
    return bad


def a_vacuous_suite_contributes_no_reach(out: list[str]) -> int:
    """Check a `0/0` suite contributes no reach row, so a zero cannot become a reading."""
    bad = 0
    census = suite_census.fold([_run("a.py", _record(0, 0))])
    if census.reach:
        out.append(f"selftest: a vacuous suite recorded reach {census.reach!r}")
        bad += 1
    return bad


def a_silent_suite_contributes_no_reach(out: list[str]) -> int:
    """Check a suite that reported nothing contributes no reach row — absent, not zero."""
    bad = 0
    census = suite_census.fold([_run("a.py", "")])
    if census.reach or not census.failed:
        out.append(
            f"selftest: a silent suite gave reach {census.reach!r}, failed {census.failed!r}"
        )
        bad += 1
    return bad


def a_silent_suite_still_carries_a_kind(out: list[str]) -> int:
    """Check the kind survives the no-record arm.

    ⚑ THE KIND IS A PROPERTY OF THE RUN, not of the branch it takes.
    """
    bad = 0
    census = suite_census.fold([_run("a.py", "")])
    if not census.kinds.get("a.py"):
        out.append(f"selftest: a silent suite carried no kind — {census.kinds!r}")
        bad += 1
    return bad


def a_failing_assertion_is_refused(out: list[str]) -> int:
    """Check a suite reporting fewer passes than it registered refuses the run."""
    bad = 0
    census = suite_census.fold([_run("a.py", _record(4, 5))])
    if not census.failed:
        out.append("selftest: a 4/5 suite passed the fold")
        bad += 1
    return bad


def a_nonzero_exit_is_refused(out: list[str]) -> int:
    """Check a green-looking record with a nonzero exit still refuses the run."""
    bad = 0
    census = suite_census.fold([_run("a.py", _record(5, 5), returncode=2)])
    if not census.failed:
        out.append("selftest: a green record with exit 2 passed the fold")
        bad += 1
    return bad


def a_prose_suite_is_named_as_debt(out: list[str]) -> int:
    """Check a suite reporting by prose lands in the legacy census."""
    bad = 0
    census = suite_census.fold([_run("a.py", "a selftest: 5/5")])
    if census.legacy != {"a.py"}:
        out.append(f"selftest: the prose census read {census.legacy!r}")
        bad += 1
    return bad


def a_typed_suite_is_not_named_as_debt(out: list[str]) -> int:
    """Check a suite emitting a typed record is NOT counted as prose debt."""
    bad = 0
    census = suite_census.fold([_run("a.py", _record(5, 5))])
    if census.legacy:
        out.append(f"selftest: a typed suite was named as prose debt — {census.legacy!r}")
        bad += 1
    return bad


def a_declared_skip_is_reported_not_swallowed(out: list[str]) -> int:
    """Check a declared skip is carried per suite, so it can be printed."""
    bad = 0
    census = suite_census.fold([_run("a.py", _record(4, 4, skipped=2, reason="no numpy"))])
    row = census.skipping.get("a.py")
    if row is None or (row.skipped, row.reason) != (2, "no numpy"):
        out.append(f"selftest: the skip census read {census.skipping!r}")
        bad += 1
    return bad


def the_partition_names_the_kinds(out: list[str]) -> int:
    """Check the refusal is reported as a partition over kinds, not one number.

    ⚑ ONE NUMBER REQUESTS ONE ACTION; a run with two kinds needs two.
    """
    bad = 0
    census = suite_census.fold([_run("a.py", _record(0, 0)), _run("b.py", "")])
    if len(census.by_kind()) < _TWO_KINDS:
        out.append(f"selftest: two differently-broken suites partitioned to {census.by_kind()!r}")
        bad += 1
    return bad


def the_totals_are_sums_of_the_split(out: list[str]) -> int:
    """Check the aggregate is derived from the per-suite rows, never carried beside them."""
    bad = 0
    census = suite_census.fold([_run("a.py", _record(3, 3)), _run("b.py", _record(2, 4))])
    if (census.passed, census.declared) != (5, 7):
        out.append(f"selftest: the totals read {census.passed}/{census.declared}, expected 5/7")
        bad += 1
    return bad


def durations_are_kept_per_suite(out: list[str]) -> int:
    """Check each suite's duration survives the fold — the parallel floor is per suite."""
    bad = 0
    census = suite_census.fold([_run("a.py", _record(1, 1), seconds=_ONE_DURATION)])
    if census.seconds.get("a.py") != _ONE_DURATION:
        out.append(f"selftest: durations folded to {census.seconds!r}")
        bad += 1
    return bad


_ARMS = (
    a_green_suite_is_counted,
    a_vacuous_suite_is_refused,
    a_vacuous_suite_contributes_no_reach,
    a_silent_suite_contributes_no_reach,
    a_silent_suite_still_carries_a_kind,
    a_failing_assertion_is_refused,
    a_nonzero_exit_is_refused,
    a_prose_suite_is_named_as_debt,
    a_typed_suite_is_not_named_as_debt,
    a_declared_skip_is_reported_not_swallowed,
    the_partition_names_the_kinds,
    the_totals_are_sums_of_the_split,
    durations_are_kept_per_suite,
)

_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-census selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-census selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO DISCOVERY SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
