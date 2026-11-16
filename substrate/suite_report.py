#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Render a run's verdict for the operator — the projection an operator actually reads.

⚑⚑⚑ THIS IS THE THIRD VIEW OF ONE VERDICT, AND IT WAS THE ONE READ ALL SESSION. The staleness
reader and the ledger were both taught to carry the KIND while this printer still said
"BROKEN … failed" — so the in-run output, which is what an operator sees, kept the collapse
after both other views had shed it. Fixing a reader and a writer while leaving a third
projection stale is the derived-view defect, and here it was the projection with a reader.

⚑ THE KIND LEADS THE ROW, because it decides where to look. A bare mark sent a reader hunting
a defect in a suite that passes 67/67 — it had been killed by its memory lease before it could
report. `unfit` sends you to the lease; `vacuous` to a suite that asserted nothing; `refused`
to the invocation; `unread` to the emitter's spelling. Four different next actions.

⚑ AND THE HINTS EXIST BECAUSE THREE OF THOSE KINDS ARE NOT TEST FAILURES AT ALL:

  · `unfit`   — a LEASE finding. The suite was killed before it could report. Raising the
                lease is one answer; the other is that its footprint is debt.
  · `refused` — a GUARD exited 2 on the INVOCATION (unknown flag, unstated mutation, unstated
                tenant), so the suite died on its own harness having assessed NOTHING.
  · `unread`  — the suite PRINTED a count that neither reader could parse. Its assertions are
                green and UNREAD. ⚑ DO NOT widen the prose reader to accept the spelling: that
                banks one more accepted form and leaves the class open. Fix the emitter.

⚑ A DECLARED SKIP IS PRINTED, NEVER SWALLOWED. It is not in the denominator, so this is the
ONLY place it can be seen — and an unrun case nobody is told about is the defect one layer over.

⚑ THE VERDICT IS A LINE, NOT ONLY AN EXIT CODE. Reading a program's status via `echo $?` is the
reasoning-not-codified shape: the code stays for the hook, the sentence is for the reader.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡retire-the-runner). It RETURNS lines rather than
printing them, so a case can drive it — inline, this reasoning was unreachable from any suite.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from substrate import suite_census

# Why each not-ok kind happened, in the words that name the next action.
WHY = {
    "cases": "assertions failed",
    "vacuous": "ran ZERO cases — asserted nothing",
    "unfit": "KILLED by its memory lease — did not fit, did NOT fail",
    "refused": (
        "a GUARD refused the invocation (exit 2) — died on its own harness, assessed NOTHING"
    ),
    "silent": "printed no counted line",
    "unread": (
        "PRINTED a count neither reader could parse — the emitter exists and its "
        "spelling is unreadable; its cases are green and UNREAD"
    ),
    "BROKEN": "failed (pre-kind ledger; re-run to classify)",
}

# The kinds that are NOT test failures, and what a reader should do instead.
HINTS = {
    "unfit": (
        "⚑ `unfit` is a LEASE finding, NOT a test failure: the suite was killed before "
        "it could report. Raising the lease is one answer; the other is that its "
        "footprint is debt."
    ),
    "refused": (
        "⚑ `refused` is NOT a test failure and NOT this suite's defect: a guard "
        "exited 2 on the INVOCATION (unknown flag / unstated mutation / unstated "
        "tenant), so the suite died on its own harness having assessed nothing."
    ),
    "unread": (
        "⚑ `unread` is NOT a test failure and NOT an absent emitter: the suite PRINTED "
        "a count that neither the typed record nor the transitional prose reader could "
        "parse, so its green assertions went UNREAD. ⚑ DO NOT widen the prose reader "
        "to accept the spelling — that banks one more accepted form and leaves the "
        "class open. Emit the record instead."
    ),
}

# How wide the kind column is, so the labels line up under it.
_KIND_WIDTH = 8

# How many suites the slowest-first listing names.
_TOP_SLOWEST = 8


def passing_line(label: str, row: suite_census.Counts) -> str:
    """Render one passing suite's line, naming any declared skip."""
    skip = f"  ({row.skipped} skipped: {row.reason})" if row.skipped else ""
    return f"  {label}: selftest: {row.passed}/{row.declared}{skip}"


def _partition(by_kind: dict[str, int]) -> str:
    """Render the failure partition — the population, not the tally."""
    return ", ".join(f"{n} {kind}" for kind, n in sorted(by_kind.items()))


def failure_lines(census: suite_census.Census, suites: int) -> list[str]:
    """Render the NOT-OK verdict: the partition, each row with its kind, then the hints."""
    by_kind = census.by_kind()
    head = f"selftests: NOT-OK — {len(census.failed)} of {suites} suite(s): {_partition(by_kind)}"
    lines = [head]
    for label, tail in census.failed:
        kind = census.kinds.get(label, "cases")
        lines.append(f"    {kind.upper():<{_KIND_WIDTH}} {label}")
        lines.extend(f"        {line}" for line in tail)
    # ⚑ EVERY NOT-A-FAILURE KIND PRESENT GETS ITS HINT, in a stable order — a run with two of
    # them needs both, and printing only the first is the same collapse one layer down.
    lines.extend(HINTS[kind] for kind in sorted(HINTS) if by_kind.get(kind))
    return lines


def summary_line(census: suite_census.Census, suites: int) -> str:
    """Render the passing verdict, naming declared skips rather than swallowing them."""
    skipped = census.skipped
    tail = f"; {skipped} declared skip(s) in {len(census.skipping)} suite(s)." if skipped else "."
    return f"selftests: {census.passed}/{census.declared} case(s) across {suites} suite(s){tail}"


def _slower(row: tuple[str, float]) -> float:
    """Sort key ranking the slowest suite first."""
    return -row[1]


def slowest_lines(seconds: dict[str, float], jobs: int) -> list[str]:
    """Render the slowest suites — the parallel floor, which no `-j` beats.

    ⚑ REPORT THE POPULATION, NOT THE TALLY. A wall-clock total hides WHICH suite dominates,
    and with a pool the slowest suite is the floor. Naming it is what makes the next
    optimisation targetable instead of guessed.
    """
    ranked = sorted(seconds.items(), key=_slower)[:_TOP_SLOWEST]
    lines = ["  slowest suites (wall seconds, the parallel floor):"]
    lines.extend(f"    {dt:6.1f}  {label}" for label, dt in ranked)
    lines.append(f"  serial cost {sum(seconds.values()):.1f}s across {jobs} worker(s)")
    return lines
