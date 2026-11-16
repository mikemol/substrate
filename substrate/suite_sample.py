#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""One selftest run's counts, and the single projection into the producer's gauge shape.

⚑ ONE PROJECTION, SHARED BY THE LIVE PATH AND THE REPLAY. The live emit and the spool replay
previously built the same gauges from two different in-memory shapes, which is how the live
path gained a `seconds` series while the replay silently did not — a whole field lost with
nothing forcing the two to agree. Both now project through `series_of` FROM THE SAMPLE, so a
field added here reaches the replay by construction rather than by remembering to edit twice.

⚑ THE LIVE PATH EMITS THE SAMPLE IT WOULD HAVE BUFFERED. That is what makes the spool a
DELAY rather than a second encoding: "what got emitted" and "what got spooled" cannot
disagree if they are the same object.

⚑ PER-SUITE IS THE GRAIN, NEVER THE TOTAL. An aggregate cannot separate "one suite grew a
case" from "one grew and another lost one" — identical at the sum, and the second is the one
worth waking up for. The aggregate is derivable from the split by `sum`; the split is not
recoverable from the aggregate, so it is the split that is carried. The same argument holds
for durations: under a thread pool the slowest suite is the parallel floor, and a wall-clock
total hides which one it is.

⚑⚑ AN ABSENT FIELD PROJECTS TO NOTHING, NEVER TO A ZERO — and this is the module's whole
contract. A run that measured no durations emits no duration series; a suite reported at
`0.0s` would read as instantaneous rather than as unmeasured, which is the silent-zero this
repo banks at four layers. The same applies backwards in time: a sample buffered before
durations existed carries no seconds, and one buffered before skips were typed carries a
two-element row, so the projection tolerates its own history rather than raising on it.

⚑ A REPLAY IS NOT A RE-MEASUREMENT. A deferred sample carries its OWN moment in `at`;
emitting today's numbers under a week-old timestamp — or the reverse — makes the backfilled
series a fiction, worse than the gap it fills.

⚑ THE ROW IS TYPED, NOT A BAG. A buffered sample arrives from disk as untyped JSON, and
`Sample.of` is the ONE place that narrowing happens — so a shape the spool wrote before a
field existed is reconciled once, at the boundary, rather than guarded at each of six
projections.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡retire-the-runner). Deliberately pure: it
imports no producer and opens no socket, so its cases run without a store.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# The service and metric names this producer owns, and the spool queue it buffers into.
SERVICE = "substrate.selftest"
PREFIX = "substrate_selftest"
METER = "selftest"
SPOOL_KEY = "selftest"

# The heartbeat whose VALUE this run controls, for read-your-write verification.
HEARTBEAT = f"{PREFIX}_emit_unixtime"

# Each gauge's unit, keyed by the suffix `PREFIX` is joined to.
UNITS = {
    "cases": "1",
    "cases_declared": "1",
    "cases_skipped": "1",
    "broken": "1",
    "seconds": "s",
    "suites": "1",
}

# How many fields a per-suite row had before skips were typed.
_PRE_SKIP_ROW = 2

# One gauge's points: label tuples to values.
Points = dict[tuple[tuple[str, str], ...], float]


@dataclass(frozen=True, slots=True)
class Row:
    """One suite's counts: how many passed, how many registered, how many were skipped."""

    passed: int
    declared: int
    skipped: int = 0

    @classmethod
    def of(cls, values: list[int]) -> Row:
        """Narrow a persisted row, tolerating one written before skips were typed."""
        skipped = values[_PRE_SKIP_ROW] if len(values) > _PRE_SKIP_ROW else 0
        return cls(passed=values[0], declared=values[1], skipped=skipped)

    def as_list(self) -> list[int]:
        """Render the row as the plain list the spool persists."""
        return [self.passed, self.declared, self.skipped]


def _rows_of(value: object) -> dict[str, Row]:
    """Narrow the persisted per-suite map, dropping any row that is not a pair of counts."""
    if not isinstance(value, dict):
        return {}
    out: dict[str, Row] = {}
    for key, row in value.items():
        if isinstance(row, list) and len(row) >= _PRE_SKIP_ROW:
            out[str(key)] = Row.of([int(n) for n in row])
    return out


def _seconds_of(value: object) -> dict[str, float]:
    """Narrow the persisted duration map. An absent map stays EMPTY, never zeroed."""
    if not isinstance(value, dict):
        return {}
    return {str(key): float(secs) for key, secs in value.items()}


def _names_of(value: object) -> tuple[str, ...]:
    """Narrow a persisted list of suite labels."""
    if not isinstance(value, list):
        return ()
    return tuple(str(name) for name in value)


def _int_of(value: object) -> int:
    """Narrow a persisted number to an int, defaulting to 0 when it is not one."""
    return value if isinstance(value, int) else 0


def _float_of(value: object) -> float:
    """Narrow a persisted number to a float, defaulting to 0.0 when it is not one."""
    return float(value) if isinstance(value, (int, float)) else 0.0


@dataclass(frozen=True, slots=True)
class Sample:
    """One run's counts, in the shape that is BOTH emitted and buffered."""

    suites: int
    cases: int
    declared: int
    at: float
    per_suite: dict[str, Row] = field(default_factory=dict)
    seconds: dict[str, float] = field(default_factory=dict)
    broken: tuple[str, ...] = ()

    @property
    def failed(self) -> int:
        """How many suites this run reported broken."""
        return len(self.broken)

    def as_dict(self) -> dict[str, object]:
        """Render the sample as the plain mapping the spool persists."""
        return {
            "suites": self.suites,
            "cases": self.cases,
            "declared": self.declared,
            "failed": self.failed,
            "at": self.at,
            "per_suite": {k: v.as_list() for k, v in self.per_suite.items()},
            "seconds": dict(self.seconds),
            "broken": sorted(self.broken),
        }

    @classmethod
    def of(cls, values: dict[str, object]) -> Sample:
        """Narrow a persisted sample back into the typed shape the projection reads."""
        return cls(
            suites=_int_of(values.get("suites")),
            cases=_int_of(values.get("cases")),
            declared=_int_of(values.get("declared")),
            at=_float_of(values.get("at")),
            per_suite=_rows_of(values.get("per_suite")),
            seconds=_seconds_of(values.get("seconds")),
            broken=_names_of(values.get("broken")),
        )


def series_of(sample: Sample) -> dict[str, Points]:
    """Return the producer's `{suffix: {labels: value}}` shape for one sample."""
    per = sample.per_suite
    broken = set(sample.broken)
    return {
        "cases": {(("suite", k),): row.passed for k, row in per.items()},
        "cases_declared": {(("suite", k),): row.declared for k, row in per.items()},
        "cases_skipped": {(("suite", k),): row.skipped for k, row in per.items()},
        "broken": {(("suite", k),): (1 if k in broken else 0) for k in per},
        # ⚑ AN EMPTY MAP EMITS NO DURATION SERIES rather than a row of zeros — an absence
        # readable as an absence, where a zero would claim every suite ran instantly.
        "seconds": {(("suite", k),): secs for k, secs in sample.seconds.items()},
        "suites": {(): sample.suites},
    }
