#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Render whether the recorded run still describes today's tree, and the reach census beside it.

⚑⚑ THESE ARE THE TWO DIAGNOSTIC READS, AND NEITHER RUNS ANYTHING. "Have I run the suite since
these edits" and "what does each suite's recorded reach look like against its source today" are
both questions a reader has WHEN THE GATE HAS ALREADY REFUSED — so answering either by running
the roster would make the diagnostic cost the thing it diagnoses.

⚑ THE VERDICT IS A LINE, NOT ONLY AN EXIT CODE. Reading a program's status via `echo $?` is the
reasoning-not-codified shape: the code stays for the hook, the sentence is for the reader.

⚑ AND THE KIND IS THE ACTIONABLE HALF OF A STALENESS REPORT. "FAILED" sends a reader looking
for a defect; `unfit` sends them to the memory lease and `vacuous` to a suite that asserted
nothing. Three different next actions, one word until the kind became a column.

⚑⚑⚑ THE TWO REACH LENSES ARE NOT COMPARABLE AS ABSOLUTE NUMBERS, and printing them side by
side INVITES exactly that misreading — so the boundary is stated at the point of the
misreading rather than left in a docstring. `recorded` counts cases a RUN REACHED; `source now`
counts case CALL SITES, and a case registered inside a loop is one site and many cases. Only
each lens against its OWN history is meaningful.

⚑ AN ABSENT REACH BASELINE IS NAMED, NOT SILENTLY EMPTY. It is minted by the commit path, so a
reader seeing no rows must be told the difference between "nothing recorded yet" and "nothing
to record" — the ABSENT-versus-EMPTY distinction this repo has measured a gate getting wrong.

⚑ THE LINES ARE RETURNED, NOT PRINTED, so a case can drive them.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡retire-the-runner).
"""

from __future__ import annotations

from dataclasses import dataclass

from substrate import reach_baseline, suite_ledger, suite_reach_lens, suite_report

# How wide the label column is, so the two readings line up under each other.
_LABEL_WIDTH = 42

# How wide the recorded-reading column is.
_READING_WIDTH = 6

# What the reach mode says about comparing its two columns.
_LENS_NOTE = (
    "    ⚑ `recorded` counts cases a RUN REACHED; `source now` counts case CALL\n"
    "      SITES. They are different questions and their absolute values do NOT\n"
    "      match — a case in a loop is one site and many cases. Only each lens\n"
    "      against its OWN history is meaningful; the gate compares them as DELTAS."
)

# What an absent reach baseline means, so nobody reads it as an empty one.
_NO_BASELINE = (
    "no reach baseline at {path} — it is MINTED BY THE COMMIT PATH,\n"
    "  which is the promotion gate:  git commit"
)

# What to do when no run has been recorded at all.
NEVER_RUN = "no suite run recorded; run: scripts/run_selftests.py"


@dataclass(frozen=True, slots=True)
class Verdict:
    """One diagnostic read: what to print, and what the process should exit with."""

    lines: tuple[str, ...]
    code: int


def _partition(broken: tuple[tuple[str, str], ...]) -> str:
    """Render the failure partition — the population, not the tally."""
    counts: dict[str, int] = {}
    for _label, kind in broken:
        counts[kind] = counts.get(kind, 0) + 1
    return ", ".join(f"{n} {kind}" for kind, n in sorted(counts.items()))


def _rows(reading: suite_ledger.Reading) -> list[str]:
    """Render each suite whose recorded row disagrees with today's tree."""
    lines: list[str] = []
    for label in reading.stale:
        seen = "(edited since the run)" if label in reading.rows else "(new suite, never run)"
        lines.append(f"  STALE     {label}  {seen}")
    lines += [f"  GONE      {label}  (recorded, no longer a suite)" for label in reading.gone]
    lines += [
        f"  {kind.upper():<9} {label}  ({suite_report.WHY.get(kind, kind)})"
        for label, kind in reading.broken
    ]
    return lines


def currency(body: str, suites: list[tuple[str, str]]) -> Verdict:
    """Rule on whether the recorded run still describes today's tree."""
    reading = suite_ledger.read(body, suites)
    lines = [reading.header or "# (unstamped)", *_rows(reading)]
    if not reading.current:
        lines.append(
            f"VERDICT: STALE — {len(reading.stale)} suite(s) edited or added and "
            f"{len(reading.gone)} removed since the recorded run."
        )
        lines.append("  That record does NOT describe today's tree; re-run.")
        return Verdict(tuple(lines), 1)
    if reading.broken:
        lines.append(
            f"VERDICT: CURRENT and NOT-OK — {len(reading.broken)} suite(s): "
            f"{_partition(reading.broken)}"
        )
        if any(kind == "unfit" for _label, kind in reading.broken):
            lines.append(f"  {suite_report.HINTS['unfit']}")
        return Verdict(tuple(lines), 1)
    lines.append(
        f"VERDICT: CURRENT — every one of {reading.suites} suite(s) is unchanged "
        f"since the recorded run."
    )
    return Verdict(tuple(lines), 0)


def reach(suites: list[tuple[str, str]], baseline_path: str, shown_path: str) -> Verdict:
    """Render the recorded reach census against what each suite's source holds today."""
    base = reach_baseline.read_reach(baseline_path)
    lines = [] if base else [_NO_BASELINE.format(path=shown_path)]
    for label, path in suites:
        now = suite_reach_lens.static_cases(path)
        rec = base.get(label)
        recorded = "-" if rec is None else f"{rec[0]}/{'?' if rec[1] is None else rec[1]}"
        source = "unparseable" if now is None else str(now)
        lines.append(
            f"  {label:<{_LABEL_WIDTH}} recorded {recorded:<{_READING_WIDTH}} source now {source}"
        )
    lines.append(f"  {len(suites)} suite(s); {len(base)} carry a recorded reading.")
    lines.append(_LENS_NOTE)
    return Verdict(tuple(lines), 0)
