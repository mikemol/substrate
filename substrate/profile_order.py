#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Profile one named target and write the report — the composition, and the only place that prints.

⚑⚑⚑ THE ITERATION-CYCLE INSTRUMENT, WRITTEN AS A TOOL BECAUSE IT WAS WRITTEN AS A THROWAWAY TWICE
(user, 2026-08-03: *"not great to keep writing one-off python profilers"*). Both times the question
was the same — this tool takes two minutes, where does it go — and both times the answer evaporated
with the turn, so the next reader re-derived it and got a different story. That is the standing
rule's exact target: a judgement happening in the turn instead of in a program.

⚑⚑ AND THE THROWAWAY GOT THE ANSWER WRONG BEFORE IT GOT IT RIGHT. A 57s-to-117s regression was
attributed to the scan that had just been added; it did not appear in the top 28 at all. A story
about a regression, told without the profile, blames the most recent edit — which is the same
attribution error this tree records for compile failures.

⚑⚑ THE CACHE PROBES ARRIVE BY INJECTION, AND THAT IS WHAT LETS THIS MODULE LIVE IN `substrate/`.
The counters worth reading — a shared cache's per-consumer hits and misses, a lexer's mask cache —
live in `scratch/`, which this package must not import. A `Probe` is a name and a callable
returning already-formatted lines, so the CALLER owns that dependency and this module owns the
composition. Nothing here knows what a mask cache is.

⚑⚑ AND THE PER-CONSUMER COUNTERS EXISTING IS NOT THE SAME AS THEM BEING READ. They were built as
the control-loop feedback and then store-wide totals were reported instead, which cannot attribute
— so "which consumer is paying for the round trips" stayed a guess across four profiling runs. A
probe that raises is reported AS a failed probe rather than silently skipped, because a silently
absent section is indistinguishable from a section with nothing to say.

⚑ THIS IS THE ONLY MODULE IN THE GROUP THAT WRITES. The measurement, the join, the classification
and the rendering are all values; the decision to put them on a stream is made once, here.

⚑⚑⚑ THE CONSUMER IS NOT YET REWIRED, AND THE REASON IS THE FINDING. `scripts/wg_profile.py` has
exactly ONE consumer — `scripts/worklist_gate.py`, which imports `profile_order` at its line 133
and calls it once. Repointing that import at this package is a two-token edit, and it is REFUSED:
`worklist_gate.py` carries 831 pycheck findings, and the per-file gate has no partial-credit path,
so any edit to it is rejected whole. The callee being typed and ready does not help when the
CALLER is the blocked file.

⚑⚑ SO THE INSERT DOES NOT RETIRE YET, AND `drain_leverage --name wg_profile` SAYS SO DIRECTLY:
`retires 0, contested 8`. Every `sys.path` line `wg_profile` carries is SHARED with seven co-drain
siblings (`wg_engine`, `wg_order`, `wg_dispatch`, `ratchet`, `items`, `bibstruct`, `figures`), so
draining this one module removes no line from the tree — a contested insert retires only when the
LAST of its sharers is drained. Reading "its 7 sites are all path reads" as "its inserts retire"
conflates the two: what is drainable here is the module, and what is retirable is the insert.

⚑⚑ THE UNBLOCKING MOVE IS THEREFORE `worklist_gate`, NOT ANOTHER LEAF. It is also the ONE non-leaf
suite that runs the whole roster, so the sequence that finishes this is: drain the remaining `wg_*`
consumers into this package, then retire `worklist_gate` itself — at which point the shared inserts
lose their last sharers and the counter moves for all eight at once.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import profile_join, profile_report, profile_run, worklist_paths

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence
    from pathlib import Path
    from typing import TextIO


@dataclass(frozen=True, slots=True)
class Probe:
    """A named source of extra counter lines, supplied by the caller.

    ⚑ THE PROBE RETURNS LINES, NOT COUNTERS. Formatting a cache's statistics needs to know what
    they mean — a full cache evicting steadily and a cache thrashing against its cap produce the
    same numbers and want opposite responses — so that judgement stays with whoever owns the
    counter rather than being re-derived here from field names.
    """

    name: str
    lines: Callable[[], Sequence[str]]


def _probe_lines(probes: Iterable[Probe]) -> list[str]:
    """Collect each probe's lines, reporting a failure as a finding rather than a silence.

    ⚑⚑ A PROBE THAT RAISES IS NAMED. The superseded body wrapped both counter reads in a bare
    `except Exception: pass`, so a renamed function or an import error produced a report with the
    section simply missing — indistinguishable from a cache that had nothing to say, and from a
    cache that was never consulted. All three look like a complete report.

    ⚑ THE CAUGHT SET IS ENUMERATED RATHER THAN BLANKET. A bare `Exception` here would also swallow
    a `KeyboardInterrupt`-adjacent control flow and, more to the point, would hide a genuine defect
    in this module behind a probe's name. These six are what a foreign counter plausibly raises:
    a missing module, a renamed attribute, a changed return shape, or an unreadable file.
    """
    out: list[str] = []
    for probe in probes:
        try:
            lines = list(probe.lines())
        except (OSError, AttributeError, ImportError, KeyError, TypeError, ValueError) as exc:
            out.append(f"{probe.name}: UNAVAILABLE ({type(exc).__name__}: {exc})")
            out.append("   ⚑ ABSENT, not empty — this counter was not read, so nothing below")
            out.append("     rules out the behaviour it would have reported.")
            continue
        if lines:
            out.extend(lines)
    return out


def report_lines(
    target: str,
    run: Callable[[], object],
    probes: Iterable[Probe] = (),
    root: Path | None = None,
) -> list[str]:
    """Measure `run`, join both projections, and render the whole report as lines.

    ⚑ THE TARGET IS AN ARGUMENT, AND THE REPORT NAMES IT (user, 2026-08-04: *"`--profile` targets
    `order()` ... sounds like a denominator problem to me."*). It was once hardcoded, with the
    function's own name baking that in — so a reader chasing one suite's overrun got a measurement
    of a DIFFERENT PROGRAM with nothing in the output saying so.
    """
    measured = profile_run.measure(target, run)
    joined = profile_join.join(measured.timings, measured.allocations)
    repeated = profile_join.repeated_work(measured.timings)
    where = worklist_paths.ROOT if root is None else root

    lines = profile_report.memory_lines(measured.target, measured.reading)
    lines.extend(profile_report.joined_lines(joined, where))
    lines.extend(profile_report.repeated_lines(repeated, where))
    lines.extend(_probe_lines(probes))
    return lines


def profile(
    target: str,
    run: Callable[[], object],
    probes: Iterable[Probe] = (),
    out: TextIO | None = None,
) -> int:
    """Write the report for one target and return an exit code.

    ⚑ THE RETURN IS ALWAYS ZERO BECAUSE PROFILING IS A MEASUREMENT, NOT A VERDICT. A slow target
    is not a failing one, and returning non-zero for a large figure would make this instrument
    into a gate whose threshold nobody chose.
    """
    stream = sys.stdout if out is None else out
    stream.write("\n".join(report_lines(target, run, probes)) + "\n")
    return 0
