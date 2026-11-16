#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_report` — the kind reaches the operator, and the hints do too.

⚑⚑ THE LOAD-BEARING ARM IS THAT THE KIND REACHES THE PRINTED ROW. This projection is the one an
operator actually reads, and it kept saying "BROKEN … failed" for a whole session after the
ledger and the staleness reader had both been taught the kind. A reader seeing a bare mark went
hunting a defect in a suite that passes 67/67 and had been killed by its memory lease.

⚑ THE HINT ARMS ARE THE OTHER HALF, AND THEY ARE PLURAL ON PURPOSE. Three kinds are NOT test
failures, and a run can carry two of them at once; printing only the first is the same collapse
one layer down.

⚑ AND THE SKIP ARM CHECKS AN ABSENCE IS SPOKEN. A declared skip is not in the denominator, so
this renderer is the ONLY place it can be seen — an unrun case nobody is told about is exactly
the defect the runner exists to surface.
"""

from __future__ import annotations

import sys

from substrate import suite_census, suite_report

# The wall time one fixture suite reports.
_SLOW = 9.5
_FAST = 0.5


def _census(kinds: dict[str, str]) -> suite_census.Census:
    """Build a census whose suites all failed with the given kinds."""
    census = suite_census.Census()
    for label, kind in kinds.items():
        census.kinds[label] = kind
        census.failed.append((label, ["tail line"]))
    return census


def the_kind_leads_the_row(out: list[str]) -> int:
    """Check each failing row is led by its kind, which is what decides where to look."""
    bad = 0
    lines = suite_report.failure_lines(_census({"a.py": "unfit"}), 1)
    if not any("UNFIT" in line and "a.py" in line for line in lines):
        out.append(f"selftest: the failing row did not lead with its kind — {lines!r}")
        bad += 1
    return bad


def the_verdict_names_the_partition(out: list[str]) -> int:
    """Check the head line names each kind and its count, not one number."""
    bad = 0
    lines = suite_report.failure_lines(_census({"a.py": "unfit", "b.py": "cases"}), 2)
    if "1 cases" not in lines[0] or "1 unfit" not in lines[0]:
        out.append(f"selftest: the verdict head read {lines[0]!r}")
        bad += 1
    return bad


def a_lease_kill_is_named_as_not_a_failure(out: list[str]) -> int:
    """Check `unfit` earns the hint saying it is a LEASE finding, not a test failure."""
    bad = 0
    lines = suite_report.failure_lines(_census({"a.py": "unfit"}), 1)
    if suite_report.HINTS["unfit"] not in lines:
        out.append("selftest: an unfit run printed no lease hint")
        bad += 1
    return bad


def two_hint_kinds_both_print(out: list[str]) -> int:
    """Check a run carrying two not-a-failure kinds prints BOTH hints.

    ⚑ PRINTING ONLY THE FIRST is the same collapse this module exists to undo.
    """
    bad = 0
    lines = suite_report.failure_lines(_census({"a.py": "unfit", "b.py": "refused"}), 2)
    printed = sum(1 for kind in ("unfit", "refused") if suite_report.HINTS[kind] in lines)
    if printed != len(("unfit", "refused")):
        out.append(f"selftest: only {printed} of 2 hints printed")
        bad += 1
    return bad


def a_plain_failure_earns_no_hint(out: list[str]) -> int:
    """Check `cases` — an ordinary assertion failure — prints no not-a-failure hint."""
    bad = 0
    lines = suite_report.failure_lines(_census({"a.py": "cases"}), 1)
    if any(hint in lines for hint in suite_report.HINTS.values()):
        out.append("selftest: a plain assertion failure printed a not-a-failure hint")
        bad += 1
    return bad


def every_hint_kind_has_a_reason(out: list[str]) -> int:
    """Check each hinted kind also has a `WHY` line — the two tables must not drift apart."""
    bad = 0
    missing = sorted(set(suite_report.HINTS) - set(suite_report.WHY))
    if missing:
        out.append(f"selftest: hinted kinds with no reason line: {missing}")
        bad += 1
    return bad


def a_declared_skip_is_spoken(out: list[str]) -> int:
    """Check a passing suite's declared skip appears in its line, rather than vanishing."""
    bad = 0
    row = suite_census.Counts(passed=4, declared=4, skipped=2, reason="no numpy")
    line = suite_report.passing_line("a.py", row)
    if "2 skipped" not in line or "no numpy" not in line:
        out.append(f"selftest: the passing line read {line!r}")
        bad += 1
    return bad


def a_suite_with_no_skip_says_nothing_extra(out: list[str]) -> int:
    """Check a suite with no skip prints no empty parenthetical."""
    bad = 0
    line = suite_report.passing_line("a.py", suite_census.Counts(passed=4, declared=4))
    if "skipped" in line:
        out.append(f"selftest: a suite with no skip read {line!r}")
        bad += 1
    return bad


def the_summary_names_the_skips(out: list[str]) -> int:
    """Check the passing verdict reports declared skips rather than folding them away."""
    bad = 0
    census = suite_census.Census()
    census.counts["a.py"] = suite_census.Counts(passed=4, declared=4, skipped=2, reason="no numpy")
    line = suite_report.summary_line(census, 1)
    if "2 declared skip(s)" not in line:
        out.append(f"selftest: the summary read {line!r}")
        bad += 1
    return bad


def the_slowest_suite_is_named(out: list[str]) -> int:
    """Check the timing report NAMES the parallel floor rather than only totalling it."""
    bad = 0
    lines = suite_report.slowest_lines({"slow.py": _SLOW, "fast.py": _FAST}, jobs=4)
    if "slow.py" not in lines[1]:
        out.append(f"selftest: the slowest suite was not named first — {lines!r}")
        bad += 1
    return bad


def the_serial_cost_is_reported(out: list[str]) -> int:
    """Check the serial total is reported beside the population, not instead of it."""
    bad = 0
    lines = suite_report.slowest_lines({"slow.py": _SLOW, "fast.py": _FAST}, jobs=4)
    if "serial cost" not in lines[-1] or "4 worker(s)" not in lines[-1]:
        out.append(f"selftest: the serial-cost line read {lines[-1]!r}")
        bad += 1
    return bad


_ARMS = (
    the_kind_leads_the_row,
    the_verdict_names_the_partition,
    a_lease_kill_is_named_as_not_a_failure,
    two_hint_kinds_both_print,
    a_plain_failure_earns_no_hint,
    every_hint_kind_has_a_reason,
    a_declared_skip_is_spoken,
    a_suite_with_no_skip_says_nothing_extra,
    the_summary_names_the_skips,
    the_slowest_suite_is_named,
    the_serial_cost_is_reported,
)

_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-report selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-report selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO DISCOVERY SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
