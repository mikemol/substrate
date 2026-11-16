#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Fold a run's captured suite outputs into the four censuses a verdict needs.

⚑⚑ FOUR CENSUSES, NOT ONE TALLY, AND THE SPLIT IS THE WHOLE POINT. The run loop this replaces
computed all four and folded three of them into two integers before anything could read them —
the knew-and-threw-away shape. What a run produces is:

  · the COUNTS per suite      — passed / declared / skipped, never summed away
  · the KIND per suite        — ok / cases / vacuous / unfit / refused / silent / unread
  · the REACH per suite       — how many cases the run REACHED, for the reach ratchet
  · the LEGACY set            — which suites reported by PROSE rather than a typed record

⚑ THE PER-SUITE SPLIT CANNOT BE RECOVERED FROM A TOTAL. "One suite grew a case" and "one grew
and another lost one" are identical at the sum, and the second is the one worth waking up for.

⚑⚑⚑ A VACUOUS `0/0` IS NOT A PASS, AND THE ORIGINAL READ `passed != declared`. `0 != 0` is
False, so a suite that executed ZERO cases counted GREEN and contributed 0 to both totals —
invisible in the summary because it moved neither number. MEASURED 2026-08-03: a suite returned
True on its dependency-absent path, so eight assertions never ran and the gate said green.

⚑ AND A `0/0` IS EXCLUDED FROM THE REACH CENSUS TOO, for a different reason: it is already
`vacuous` and red, and admitting it would let a zero become a recorded reading on a first
sighting — a number no honest run could then fall below without being called a regression.

⚑ THE REACH CENSUS IS BUILT ONLY FROM SUITES THAT REPORTED. A suite with no record contributes
NO ROW. Recording it as 0 would bank an abort as its new reading, which is the false-ZERO
direction this repo banks silently.

⚑ THE KIND IS RECORDED BEFORE THE BRANCH, so it survives BOTH arms. A first cut put it between
an `if` and its `elif` — a SyntaxError, caught at once, but the shape is worth the line: the
kind is a property of the RUN, not of the reporting branch it happens to take, and computing it
inside one arm is how the other arm loses it.

⚑ AND IT IS DERIVED FROM THE NUMBERS, NEVER FROM THE RECORD'S OWN `state`. A suite must not be
able to grade itself green: a producer writing `"state": "ok"` beside `0/0` still reads VACUOUS
here, which is the whole reason the typed record does not simply carry the verdict.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡retire-the-runner). Pure: it is handed captured
output and returns rows, so its cases need no subprocess.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from substrate import suite_record

# How many trailing lines of a failing suite's output a reader is shown.
_TAIL_LINES = 3


@dataclass(frozen=True, slots=True)
class Run:
    """One suite's captured run: what it printed, how it exited, how long it took."""

    label: str
    output: str
    returncode: int
    seconds: float = 0.0


@dataclass(frozen=True, slots=True)
class Counts:
    """One suite's numbers for this run."""

    passed: int
    declared: int
    skipped: int = 0
    reason: str = ""

    @property
    def bad(self) -> bool:
        """Report whether these numbers refuse the run.

        ⚑ A VACUOUS DENOMINATOR IS NOT A PASS. `passed != declared` alone reads `0/0` green.
        """
        return self.passed != self.declared or self.declared == 0


@dataclass(slots=True)
class Census:
    """Everything one run measured, at the grain it was measured."""

    counts: dict[str, Counts] = field(default_factory=dict)
    kinds: dict[str, str] = field(default_factory=dict)
    reach: dict[str, int] = field(default_factory=dict)
    legacy: set[str] = field(default_factory=set)
    failed: list[tuple[str, list[str]]] = field(default_factory=list)
    seconds: dict[str, float] = field(default_factory=dict)

    @property
    def passed(self) -> int:
        """How many cases passed across every suite that reported."""
        return sum(row.passed for row in self.counts.values())

    @property
    def declared(self) -> int:
        """How many cases registered across every suite that reported."""
        return sum(row.declared for row in self.counts.values())

    @property
    def skipped(self) -> int:
        """How many cases were declaredly skipped across every suite that reported."""
        return sum(row.skipped for row in self.counts.values())

    @property
    def skipping(self) -> dict[str, Counts]:
        """The suites that declared a skip, so the count is reported and never swallowed."""
        return {label: row for label, row in self.counts.items() if row.skipped}

    @property
    def broken(self) -> tuple[str, ...]:
        """The labels this run refuses, in the order they were folded."""
        return tuple(label for label, _tail in self.failed)

    def by_kind(self) -> dict[str, int]:
        """Return how many refused suites each kind accounts for.

        ⚑ THE VERDICT NAMES THE PARTITION, because "N suites failed" is the tally and the
        kinds are the POPULATION. A run with one `unfit` and one `cases` needs two different
        actions; one number requests one.
        """
        out: dict[str, int] = {}
        for label, _tail in self.failed:
            kind = self.kinds.get(label, "cases")
            out[kind] = out.get(kind, 0) + 1
        return out


def _tail(output: str) -> list[str]:
    """Return the last few lines of a suite's output — what a reader needs to see first."""
    return output.strip().split("\n")[-_TAIL_LINES:]


def fold_one(census: Census, run: Run) -> None:
    """Fold ONE suite's captured run into the census."""
    census.seconds[run.label] = run.seconds
    result = suite_record.read_result(run.output, run.returncode)
    if result.by_prose:
        census.legacy.add(run.label)
    # ⚑ RECORDED BEFORE THE BRANCH, so the kind survives both arms.
    census.kinds[run.label] = result.kind
    if not result.reported.matched:
        # No record and no counted line: the suite did not report, which is itself a
        # failure — a silent selftest is indistinguishable from a passing one.
        census.failed.append((run.label, _tail(run.output)))
        return
    counts = Counts(
        passed=result.reported.ok,
        declared=result.reported.all_,
        skipped=result.skipped,
        reason=result.reason or "",
    )
    census.counts[run.label] = counts
    # ⚑ THE DENOMINATOR IS THE REACH, NOT THE NUMERATOR. A failing assertion moves `passed`
    # and is already a failure; this census watches the other number, which no pass count
    # can show. A vacuous `0/0` is excluded — already red, and admitting it would let a zero
    # become a recorded reading on a first sighting.
    if counts.declared > 0:
        census.reach[run.label] = counts.declared
    if counts.bad or run.returncode != 0:
        census.failed.append((run.label, _tail(run.output)))


def fold(runs: list[Run]) -> Census:
    """Fold every captured run into one census."""
    census = Census()
    for run in runs:
        fold_one(census, run)
    return census
