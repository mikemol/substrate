#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Render a profile as lines — the report, as a value rather than a side effect.

⚑⚑⚑ THE TARGET IS THE DENOMINATOR, AND IT IS RENDERED FIRST. `--profile` was once hardcoded to one
function while its name and its output said nothing about which program had run, so a reader
chasing one suite's overrun got a measurement of a DIFFERENT PROGRAM with nothing in the table
saying so. The limitation had to be stated in PROSE, which is the reasoning-in-the-turn the standing
rule forbids: it evaporates, and the next reader reads the table as covering whatever they had in
mind. `n of m` for a profiler is: SAY WHAT WAS RUN.

⚑⚑ THIS RETURNS LINES; IT DOES NOT PRINT. That is what makes the report assertable — a case can
check that the target is named, that the unattributed remainder appears, and that a truncated table
says it was truncated, none of which is reachable through a function whose only output is stdout.
The caller owns the writing, and there is exactly one place that decides where it goes.

⚑⚑ TRUNCATION IS ANNOUNCED, NEVER SILENT. A table cut to its top rows with no note is the implicit
population defect the whole instrument exists to avoid: the reader cannot tell "these are all the
rows" from "these are the rows that fit", and both look like a complete answer.

⚑ EACH COMPOSED LINE IS BOUND TO A NAME BEFORE IT JOINS A LIST. An f-string split across two source
lines inside a list literal is one missing comma away from silently becoming two elements — or, as
written, from being read as a mistake by anyone auditing it. The local says which it is.

⚑ IT IMPORTS NOTHING FROM `jea/`, `scripts/` OR `scratch/`, AND NOTHING THAT SPAWNS OR READS THE
FILESYSTEM. Every figure it renders arrives as an argument.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate.process_memory import BYTES_PER_MB

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from substrate.process_memory import Reading
    from substrate.profile_join import Joined, Row

#: How many joined rows the table shows before it truncates — and says that it truncated.
JOINED_ROWS = 20

#: How many orphan allocation sites are shown.
ORPHAN_ROWS = 10

#: How many repeated-work candidates are shown.
REPEAT_ROWS = 12

#: Shown in the resident column when the procfs read failed. ⚑ NOT `0.0` — a zero renders as a
#: measurement, and the whole point is that this is the absence of one.
NO_RSS = "unknown"

#: Stated where the numbers are, not in a docstring a reader will never open.
PARTICIPANT_NOTE = (
    "  ⚑ AND THE PROFILER IS A PARTICIPANT: cProfile retains a stats entry\n"
    "    per profiled frame, so these figures are measured with it ALREADY\n"
    "    ARMED — its own retention is excluded from traced-live, NOT from RSS."
)

#: What replaces the resident half when it could not be read. ⚑ ABSENT, NEVER ZERO.
NO_RSS_NOTE = (
    f"  RSS      {NO_RSS} — /proc/self/status was unreadable, so the resident half\n"
    "    of this report is ABSENT, not zero. The unattributed remainder cannot be\n"
    "    computed, and a footprint outside Python cannot be ruled out from here."
)

#: The fix the repeated-work shape implies, which the table alone invites getting wrong.
REPEAT_NOTE = (
    "   ⚑ a modest per-call cost over thousands of calls is REPEATED work — memoise at\n"
    "     the OWNER of the relation, not by parallelising the repetition."
)


def _mb(value: float) -> str:
    """Render a byte count in megabytes, at the one precision the whole report uses."""
    return f"{value / BYTES_PER_MB:.1f}"


def memory_lines(target: str, reading: Reading) -> list[str]:
    """Summarise memory: traced, resident, collected, and what none of them attribute.

    ⚑⚑ THE UNATTRIBUTED REMAINDER IS RENDERED AS A FIGURE, NOT A CAVEAT — it is what turns "not
    attributable here" into "this much is not Python objects", which tells a reader that more
    allocation detail will not find it. It is suppressed when RSS is unknown, because a
    subtraction against a sentinel is a confident-looking fiction.
    """
    traced = (
        f"  TRACED   peak {_mb(reading.traced_peak)} MB, "
        f"live at exit {_mb(reading.traced_live)} MB  (Python objects)"
    )
    lines = [f"PROFILE of {target}()", traced]
    if reading.rss_known:
        resident = (
            f"  RSS      {_mb(reading.rss_before)} -> {_mb(reading.rss_after)} MB, "
            f"grew {_mb(reading.rss_growth)} MB  (what a cgroup cap kills on)"
        )
        collected = (
            f"  GC       collect() freed {reading.collected_objects} object(s), "
            f"RSS {_mb(reading.rss_after)} -> {_mb(reading.rss_collected)} MB"
        )
        gap = (
            f"  ⚑ UNATTRIBUTED {_mb(reading.unattributed)} MB = RSS growth minus traced-live — "
            "interpreter,\n    C extensions, and allocator arenas Python holds but does not "
            "return.\n    `tracemalloc` cannot see any of it."
        )
        lines.extend((resident, collected, gap))
    else:
        lines.append(NO_RSS_NOTE)
    split = (
        f"  ⚑ TRANSIENT {_mb(reading.transient)} MB (peaked then released) vs "
        f"{_mb(reading.traced_live)} MB RETAINED — opposite fixes."
    )
    lines.extend((split, PARTICIPANT_NOTE))
    return lines


def _joined_row(row: Row, root: Path | None) -> str:
    """Format one joined row: both projections, the site, and the verdict the pair supports."""
    return (
        f"  {row.timing.cumulative:>8.1f} {row.allocation.size / BYTES_PER_MB:>10.2f} "
        f"{row.timing.calls:>8} {row.allocation.blocks:>8}  "
        f"{row.site.funcname}  {row.site.display(root)}  [{row.verdict}]"
    )


def _row_lines(rows: Sequence[Row], limit: int, root: Path | None) -> list[str]:
    """Format one ranked table, announcing a truncation rather than performing it silently."""
    header = f"  {'cum s':>8} {'live MB':>10} {'calls':>8} {'blocks':>8}  site"
    lines = [header]
    lines.extend(_joined_row(row, root) for row in rows[:limit])
    if len(rows) > limit:
        lines.append(f"  ⚑ {len(rows) - limit} further row(s) not shown of {len(rows)} total.")
    return lines


def joined_lines(joined: Joined, root: Path | None = None) -> list[str]:
    """Render both arms: the ranked rows, then the allocating sites with no call row.

    ⚑⚑ THE SECOND ARM IS LABELLED AS WHAT IT IS. Presented without explanation, an allocation with
    no time column reads as a measurement failure; it is in fact a comprehension, a literal or a
    module-level table — the retained-corpus shape no call row can carry.
    """
    lines: list[str] = []
    if joined.rows:
        lines.extend(_row_lines(joined.rows, JOINED_ROWS, root))
    if joined.orphans:
        head = "  ALLOCATING SITES WITH NO CALL ROW (not a function — a comprehension,"
        tail = "  a literal, or a module-level table; no pstats row exists to join):"
        lines.extend((head, tail))
        lines.extend(
            f"  {'-':>8} {orphan.allocation.size / BYTES_PER_MB:>10.2f} {'-':>8} "
            f"{orphan.allocation.blocks:>8}  {orphan.site.display(root)}"
            for orphan in joined.orphans[:ORPHAN_ROWS]
        )
        if len(joined.orphans) > ORPHAN_ROWS:
            more = (
                f"  ⚑ {len(joined.orphans) - ORPHAN_ROWS} further site(s) not shown "
                f"of {len(joined.orphans)} total."
            )
            lines.append(more)
    return lines


def repeated_lines(rows: Sequence[Row], root: Path | None = None) -> list[str]:
    """Render the repeated-work candidates, with the fix the shape implies.

    ⚑ THE ADVICE IS PART OF THE REPORT BECAUSE THE TABLE ALONE INVITES THE WRONG FIX. A modest
    per-call cost over thousands of calls is repeated work; parallelising the repetition speeds up
    doing the same thing many times, where memoising at the OWNER of the relation stops doing it.
    """
    if not rows:
        return []
    lines = ["REPEATED-WORK CANDIDATES (many calls, and a real total cost):"]
    lines.extend(
        f"  {row.timing.cumulative:>7.1f}s  {row.timing.calls:>8} calls  "
        f"{row.site.funcname:<22} {row.site.display(root)}"
        for row in rows[:REPEAT_ROWS]
    )
    if len(rows) > REPEAT_ROWS:
        lines.append(f"  ⚑ {len(rows) - REPEAT_ROWS} further candidate(s) not shown.")
    lines.append(REPEAT_NOTE)
    return lines
