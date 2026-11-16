#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_sample` — the round trip, and the absences it must keep.

⚑⚑ THE LOAD-BEARING ARMS ARE THE ABSENCES. A sample buffered before durations existed and one
buffered before skips were typed are the producer's OWN history, and the failure they cause is
not a crash: it is a confident zero. A suite emitted at `0.0s` reads as instantaneous rather
than as unmeasured, and that reading is indistinguishable from a real measurement downstream.

⚑ THE ROUND TRIP IS THE OTHER HALF. The live path and the replay project from the SAME object,
so if `as_dict` and `of` disagree the two paths silently diverge — which is exactly how a whole
`seconds` field went missing from the replay once already.
"""

from __future__ import annotations

import sys

from substrate import suite_sample

# A run with two suites, one of them broken and one carrying a declared skip.
_ROWS = {
    "a.py": suite_sample.Row(passed=3, declared=3),
    "b.py": suite_sample.Row(passed=1, declared=2, skipped=1),
}
_SECONDS = {"a.py": 1.5, "b.py": 0.25}
_AT = 1753300000.0


def _sample() -> suite_sample.Sample:
    """Return the fixture run."""
    return suite_sample.Sample(
        suites=2,
        cases=4,
        declared=5,
        at=_AT,
        per_suite=dict(_ROWS),
        seconds=dict(_SECONDS),
        broken=("b.py",),
    )


def the_round_trip_preserves_the_sample(out: list[str]) -> int:
    """Check a sample survives persistence and narrowing unchanged."""
    bad = 0
    got = suite_sample.Sample.of(_sample().as_dict())
    if got != _sample():
        out.append(f"selftest: the round trip returned {got!r}, not the sample it was given")
        bad += 1
    return bad


def failed_counts_the_broken_suites(out: list[str]) -> int:
    """Check the failure count is derived from the names, never carried separately."""
    bad = 0
    if _sample().failed != 1:
        out.append(f"selftest: failed read {_sample().failed}, expected 1")
        bad += 1
    return bad


def absent_durations_emit_no_series(out: list[str]) -> int:
    """Check a sample with no durations emits NOTHING, not a row of zeros.

    ⚑ THE SILENT-ZERO ARM. `0.0s` reads as instantaneous, not as unmeasured.
    """
    bad = 0
    bare = suite_sample.Sample(
        suites=1, cases=1, declared=1, at=_AT, per_suite={"a.py": suite_sample.Row(1, 1)}
    )
    if suite_sample.series_of(bare)["seconds"]:
        out.append("selftest: a sample with no durations emitted a seconds series")
        bad += 1
    return bad


def a_pre_skip_row_narrows_without_raising(out: list[str]) -> int:
    """Check a two-element row — the producer's own history — reads a zero skip, not an error."""
    bad = 0
    got = suite_sample.Sample.of(
        {"suites": 1, "cases": 2, "declared": 2, "at": _AT, "per_suite": {"a.py": [2, 2]}}
    )
    row = got.per_suite.get("a.py")
    if row is None or row.skipped != 0:
        out.append(f"selftest: a pre-skip row narrowed to {row!r}, expected 0 skipped")
        bad += 1
    return bad


def a_pre_duration_sample_narrows_to_empty(out: list[str]) -> int:
    """Check a sample with no `seconds` key narrows to an EMPTY map, never to zeros."""
    bad = 0
    got = suite_sample.Sample.of(
        {"suites": 1, "cases": 1, "declared": 1, "at": _AT, "per_suite": {"a.py": [1, 1, 0]}}
    )
    if got.seconds:
        out.append(f"selftest: a sample with no seconds narrowed to {got.seconds!r}")
        bad += 1
    return bad


def a_malformed_row_is_dropped_not_guessed(out: list[str]) -> int:
    """Check a row too short to be a pair of counts is dropped rather than padded."""
    bad = 0
    got = suite_sample.Sample.of({"per_suite": {"a.py": [7], "b.py": [1, 1]}})
    if "a.py" in got.per_suite or "b.py" not in got.per_suite:
        out.append(f"selftest: malformed-row handling gave {got.per_suite!r}")
        bad += 1
    return bad


def a_missing_field_narrows_to_zero(out: list[str]) -> int:
    """Check an entirely empty mapping narrows rather than raising."""
    bad = 0
    got = suite_sample.Sample.of({})
    if (got.suites, got.cases, got.declared, got.at, got.broken) != (0, 0, 0, 0.0, ()):
        out.append(f"selftest: an empty sample narrowed to {got!r}")
        bad += 1
    return bad


def every_gauge_declares_a_unit(out: list[str]) -> int:
    """Check the projection emits exactly the gauges the unit table names.

    ⚑ A GAUGE WITH NO UNIT IS A SERIES NOBODY CAN READ BACK, and a unit naming a gauge that
    is no longer emitted is the stale half of the same drift. Both directions, one arm.
    """
    bad = 0
    emitted = set(suite_sample.series_of(_sample()))
    declared = set(suite_sample.UNITS)
    if emitted != declared:
        out.append(
            f"selftest: gauges {sorted(emitted ^ declared)} are emitted or declared but not both"
        )
        bad += 1
    return bad


def the_broken_gauge_flags_only_the_broken(out: list[str]) -> int:
    """Check the broken gauge carries a point per suite, set only for the named ones."""
    bad = 0
    got = suite_sample.series_of(_sample())["broken"]
    if got != {(("suite", "a.py"),): 0, (("suite", "b.py"),): 1}:
        out.append(f"selftest: the broken gauge read {got!r}")
        bad += 1
    return bad


_ARMS = (
    the_round_trip_preserves_the_sample,
    failed_counts_the_broken_suites,
    absent_durations_emit_no_series,
    a_pre_skip_row_narrows_without_raising,
    a_pre_duration_sample_narrows_to_empty,
    a_malformed_row_is_dropped_not_guessed,
    a_missing_field_narrows_to_zero,
    every_gauge_declares_a_unit,
    the_broken_gauge_flags_only_the_broken,
)

_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-sample selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-sample selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO DISCOVERY SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
