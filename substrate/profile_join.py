#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Join a time profile against an allocation profile on `(file, line)` — the analytic core.

⚑⚑⚑ TIME AND MEMORY ARE TWO PROJECTIONS OF ONE PROFILE RECORD, AND THE JOIN IS THE WHOLE POINT
(user, 2026-08-04: *"You don't do 'time or memory'. Those are both different projections of what
SHOULD be the same profile record."*). The superseded body printed a time table and then a SECOND
memory table beside it — two reports over one run, the same site appearing twice keyed differently,
with a reader left to join them by eye. `pstats` keys `(file, line, func)`; `tracemalloc`'s
`statistics("lineno")` keys `(file, line)`. The join was always available.

⚑⚑ AND THE COMBINATION IS WHAT NAMES THE DEFECT — no single column does:

    hot time,  low bytes            -> compute-bound; memoise or do it once
    hot time,  high TRANSIENT bytes -> repeated work over large objects
    cold time, high LIVE bytes      -> RETENTION: a cache holding the corpus

The third is the one a lease bisection can never find, and it is the one that was missed three
times in a row by looking at scalars. `Verdict` makes that table a value rather than a comment, so
a case can assert the classification instead of a reader inferring it from two numbers.

⚑⚑ ALLOCATING SITES WITH NO CALL ROW ARE A SECOND RESULT, NEVER DROPPED. A line that allocates but
is not a FUNCTION — a comprehension, a literal, a module-level table — has no `pstats` entry, so an
INNER join silently hides exactly the retained-corpus case the join exists to surface. `join`
therefore returns both arms, and the caller cannot accidentally read one as the whole.

⚑ THIS MODULE TAKES DICTS, NOT PROFILERS. Everything here is a pure function of two mappings, so
the analysis is testable without arming a profiler, without allocating a corpus, and without the
several seconds a real target costs. The instrumentation that PRODUCES those mappings is a
different responsibility and lives elsewhere; that separation is what makes this half assertable.

⚑ IT IMPORTS NOTHING FROM `jea/`, `scripts/` OR `scratch/`, AND NOTHING THAT SPAWNS OR READS THE
FILESYSTEM. Relative-path rendering takes its root as an ARGUMENT rather than reaching for a global,
for the reason `worklist_paths.project_for` does: a case measuring a fixture tree must be able to
ask without rebinding anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

#: A row is surfaced when it costs at least this many cumulative seconds...
COST_SECONDS = 0.5

#: ...or holds at least this many live bytes. ⚑ EITHER, NEVER BOTH — an `and` here would drop the
#: cold-time/high-live retention case, which is precisely the one no other column finds.
COST_BYTES = 1e6

#: A repeated-work candidate needs at least this many calls...
REPEAT_CALLS = 1000

#: ...AND at least this much cumulative time. ⚑ `and` IS CORRECT HERE, unlike above: a million
#: cheap calls that cost nothing in total is not a finding, it is how a loop looks.
REPEAT_SECONDS = 1.0

#: An orphan allocation site is reported once it holds at least this many bytes.
ORPHAN_BYTES = 1e6

#: Weight applied to bytes when ranking a joined row against time. ⚑ 10 MB of live bytes ranks
#: level with one cumulative second — a stated exchange rate rather than an invisible one, so a
#: reader can say the ordering is wrong for their question instead of guessing what it encodes.
BYTES_PER_SECOND = 1e7


@dataclass(frozen=True, slots=True)
class Site:
    """One `(file, line)` location, with the function name when a call row supplied one."""

    filename: str
    lineno: int
    funcname: str = ""

    def display(self, root: Path | None = None) -> str:
        """Render the location, relative to `root` when the file sits beneath it.

        ⚑ A PATH OUTSIDE THE TREE IS LEFT ABSOLUTE, NOT FORCED RELATIVE. `os.path.relpath` happily
        produces `../../../usr/lib/...` for a stdlib frame, which reads as though the tree contains
        it. The prefix test is what keeps a foreign frame legible as foreign.
        """
        shown = self.filename
        if root is not None:
            shown = shown.removeprefix(f"{root}/")
        return f"{shown}:{self.lineno}"


@dataclass(frozen=True, slots=True)
class Timing:
    """What a time profile knows about one site: how often it ran, and what it cost."""

    calls: int
    cumulative: float


@dataclass(frozen=True, slots=True)
class Allocation:
    """What an allocation profile knows about one site: live bytes, in how many blocks."""

    size: int
    blocks: int


@dataclass(frozen=True, slots=True)
class Row:
    """One site with BOTH projections joined, and the verdict the pair supports."""

    site: Site
    timing: Timing
    allocation: Allocation

    @property
    def rank(self) -> float:
        """Ordering key: seconds plus bytes at the stated exchange rate. Higher sorts first."""
        return self.timing.cumulative + self.allocation.size / BYTES_PER_SECOND

    @property
    def verdict(self) -> str:
        """Which of the three shapes this row is — the classification the join exists to make.

        ⚑ THE VERDICT MUST TRACK WHAT THE COUNTERS MEAN, and the superseded body carried a comment
        that had stopped doing so: it described a counter that had since been renamed, so the
        sentence and the number disagreed with nobody able to see it. A derived property cannot
        drift from its inputs, which is the entire reason this is code and not a comment.
        """
        hot = self.timing.cumulative >= COST_SECONDS
        heavy = self.allocation.size >= COST_BYTES
        if hot and heavy:
            return "repeated work over large objects"
        if hot:
            return "compute-bound"
        if heavy:
            return "RETENTION"
        return "below threshold"


@dataclass(frozen=True, slots=True)
class Orphan:
    """An allocating site with NO call row — a comprehension, a literal, a module-level table.

    ⚑ THIS CLASS EXISTS SO THE OUTER ARM CANNOT BE SILENTLY DROPPED. Returning these as bare
    tuples beside `Row`s invites a caller to concatenate and lose them; a distinct type makes the
    second arm something the caller must decide about.
    """

    site: Site
    allocation: Allocation


@dataclass(frozen=True, slots=True)
class Joined:
    """Both arms of the join: rows that matched, and allocating sites that had no call row."""

    rows: tuple[Row, ...]
    orphans: tuple[Orphan, ...]


def repeated_work(timings: Mapping[Site, Timing]) -> tuple[Row, ...]:
    """Select the REPEATED-WORK candidates: many calls, and a real total cost.

    ⚑ THE DISCRIMINATOR IS CALLS-PER-DISTINCT-QUESTION, NOT TOTAL TIME. A big cumulative time over
    few calls wants a faster algorithm; a modest cost over tens of thousands of calls is repeated
    work and wants memoisation AT THE OWNER of the relation — a 300s to 2.7s change that was not a
    parallelism problem. Surfacing the high-count rows is what turns a table into a worklist.

    ⚑ AND A CACHE THAT EXISTS IS NOT A CACHE THAT WORKS. A site already memoised can still appear
    here, which says nothing on its own about WHY: a thrashing cache (working set over cap) and
    redundant callers (the same input recomputed within one walk) produce the same call count and
    want OPPOSITE fixes. This function reports the candidate; it does not pretend to diagnose it.
    """
    picked = [
        Row(site, timing, Allocation(0, 0))
        for site, timing in timings.items()
        if timing.calls >= REPEAT_CALLS and timing.cumulative >= REPEAT_SECONDS
    ]
    picked.sort(key=lambda r: -r.timing.cumulative)
    return tuple(picked)


def join(
    timings: Mapping[Site, Timing],
    allocations: Mapping[Site, Allocation],
) -> Joined:
    """Join the two projections on `(file, line)`, keeping the unmatched allocations separately.

    ⚑ THE JOIN KEY DROPS `funcname` DELIBERATELY. `pstats` carries it and `tracemalloc` does not,
    so keying on all three would match nothing at all — the join would return an empty inner arm
    and a complete outer one, which reads exactly like "the program allocated but never ran".
    """
    by_location = {(s.filename, s.lineno): a for s, a in allocations.items()}
    matched: set[tuple[str, int]] = set()
    rows: list[Row] = []
    for site, timing in timings.items():
        key = (site.filename, site.lineno)
        alloc = by_location.get(key, Allocation(0, 0))
        if key in by_location:
            matched.add(key)
        if timing.cumulative < COST_SECONDS and alloc.size < COST_BYTES:
            continue
        rows.append(Row(site, timing, alloc))
    rows.sort(key=lambda r: -r.rank)

    orphans = [
        Orphan(site, alloc)
        for site, alloc in allocations.items()
        if (site.filename, site.lineno) not in matched and alloc.size >= ORPHAN_BYTES
    ]
    orphans.sort(key=lambda o: -o.allocation.size)
    return Joined(tuple(rows), tuple(orphans))
