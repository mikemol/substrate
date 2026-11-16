#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Size a memory lease for one LABEL from its recorded peaks.

⚑⚑⚑ THE AUTOBUDGET COULD NOT REACH THIS LEDGER, AND THE GAP WAS MEASURED. `_auto_mb` keys on an
argument ending in `.agda` or `.agdai`; a suite invocation is `python3 -m substrate.suite_run
<path>` and carries neither, so every one of `Selftest.mk`'s 234 `auto` requests fell through to
the default. MEASURED: the label ledger holds **166 runs of `selftest:worklist_gate.py` at max
188MB** and `membudget peaks` prints `suggested 256MB` — while every run leased 192. Four
megabytes of headroom, and two suites OOM-killed (exit 143) in a roster run that then reported
140 unrun. **The instrument was measuring correctly and nothing consumed the measurement.**

⚑⚑ THE DEFERRAL HAD A STATED TRIGGER AND IT HAS FIRED. `membudget`'s own note reads: *"NOT WIRED
TO AUTOBUDGET… Choosing a cap from one observation is the guess this exists to replace. Let the
history accumulate, then decide."* That was right when written against an empty ledger; the
labels this sizes now carry hundreds of runs each. A deferral naming its own condition is a
decision waiting to be made, not a permanent state.

⚑⚑ AND PER-LABEL IS THE CORRECT KEY HERE, which the ledger's own argument already draws:
*"per-label is the right key for a gate that runs once; per-module is the right key for work that
runs per core."* A selftest is the first kind — one label, one workload. The ingest case that
motivated that warning is the second, and this module is deliberately not offered to it.

⚑ THE ARITHMETIC IS THE ONE `cmd_peaks` ALREADY PRINTS: round the max recorded peak UP to the
next power of two, floor 64. The pow2 step IS the margin — it sits 2ⁿ ± 2ⁿ⁻¹ around the need, so
no extra fudge and no over-rounding. A lease is a hard kill cap, so rounding up keeps cap ≥ peak.

⚑ CLAMPING IS LOUD, NEVER SILENT. A recorded peak above the ceiling means the lease is knowingly
below the measured need — the state that sat invisible in a downstream consumer for weeks. The
caller is told which label, what it peaked at, and which variable raises the ceiling.

⚑ EXTRACTED RATHER THAN ADDED TO `scripts/membudget` (⟡autobudget-label). That script carries 13
pre-existing shellcheck findings and the gate is whole-file with no partial credit, so an edit
there is refused whatever it contains. The sizing is a separable concern with one input and one
number out; the shell asks this and stays as it is.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# The smallest lease worth taking, and the ceiling on this reader's extrapolation.
#
# ⚑ BOTH ARE DEFAULTS FOR AN EXTRAPOLATION, NOT BOUNDS ON WHAT A CALLER MAY ASK. An operator who
# names a size gets it; these govern only what history is allowed to infer, which is the
# distinction a downstream consumer's workaround silently lost when it hit the clamp.
FLOOR_MB = 64
CEILING_MB = 384

# The ledger's columns: label, wall seconds, peak MB, stamp, user, sys.
PEAK_COLUMN = 2
LABEL_COLUMN = 0


@dataclass(frozen=True, slots=True)
class Sizing:
    """A lease sized from history, and what the history said."""

    label: str
    # The lease to take, already rounded and clamped.
    lease_mb: int
    # The largest peak on record, or None when the label has no history.
    peak_mb: int | None
    # The ceiling bit, when the measured need exceeds what this reader may infer.
    clamped: bool

    @property
    def measured(self) -> bool:
        """Report whether any run informed this lease."""
        return self.peak_mb is not None

    @property
    def why(self) -> str:
        """Return what a caller should be told, empty when there is nothing to say.

        ⚑ A CLAMP IS THE ONLY THING WORTH SAYING ON STDERR. An unmeasured label taking the default
        is the ordinary case; a lease knowingly smaller than the measured need is the one that
        ends in a kill, and it must name the variable that raises it.
        """
        if not self.clamped or self.peak_mb is None:
            return ""
        return (
            f"membudget: {self.label} peaked at {self.peak_mb}MB but the ceiling is "
            f"{CEILING_MB}MB — leasing {self.lease_mb}, which is BELOW the measured need; "
            f"raise AGDA_MB_MAX or name a size explicitly"
        )


def bucket(peak_mb: int, floor: int = FLOOR_MB) -> int:
    """Return the smallest power of two at or above a peak.

    ⚑ THE SAME RULE `cmd_peaks` PRINTS AS `suggested`, so the suggestion and the lease cannot
    disagree — they were two derivations of one number the moment one existed without the other.
    """
    got = floor
    while got < peak_mb:
        got *= 2
    return got


def peaks(ledger: Path, label: str) -> tuple[int, ...]:
    """Return every recorded peak for one label, in the order written.

    ⚑ AN UNREADABLE LEDGER YIELDS NOTHING rather than raising: a missing history is the ordinary
    first-run state, and a sizing reader that failed there would take down the work it sizes.
    """
    try:
        text = ledger.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ()

    out: list[int] = []
    for line in text.splitlines():
        row = line.split("\t")
        if len(row) <= PEAK_COLUMN or row[LABEL_COLUMN] != label:
            continue
        found = row[PEAK_COLUMN].strip()
        if found.isdigit():
            out.append(int(found))
    return tuple(out)


def size(ledger: Path, label: str, default_mb: int, ceiling_mb: int = CEILING_MB) -> Sizing:
    """Size a lease for one label from its history, or hand back the default.

    ⚑⚑ THE MAX IS THE INPUT, NOT THE MEDIAN. A lease is a hard kill cap: a median-sized one is
    correct for half the runs and fatal for the rest, and the failure mode is a kill rather than
    a slowdown. `membudget peaks` reports median and p90 for a reader deciding; this reader is
    deciding for a process that cannot survive being wrong low.

    ⚑ AN EXPLICIT DEFAULT ABOVE THE CEILING RAISES IT. A caller that named a larger size did so
    for a reason this reader cannot see, and silently clamping it back is what made a downstream
    workaround appear to work until history existed.
    """
    cap = max(ceiling_mb, default_mb)
    found = peaks(ledger, label)
    if not found:
        return Sizing(label=label, lease_mb=default_mb, peak_mb=None, clamped=False)

    high = max(found)
    want = bucket(high)
    if want > cap:
        return Sizing(label=label, lease_mb=cap, peak_mb=high, clamped=True)
    return Sizing(label=label, lease_mb=want, peak_mb=high, clamped=False)


# ── the TIME budget, from the same ledger ────────────────────────────────────────────
#
# ⚑ RULED 2026-09-20 (W3): a multi-minute corpus fold stays on the selftest roster and the
# per-label sizer carries a WALL-TIME budget beside memory. The ledger's second column has held
# every run's wall seconds since the first lease; nothing read it. `suite_run` had NO timeout at
# all, so a hung suite hung the build, and an honest 511 s fold and a hang were the same shape.
#
# A deadline is the other kind of cap: too SHORT kills an honest run, too LONG only delays a
# hang's discovery. So the margin is a factor over the slowest recorded run, rounded up to a
# whole minute — a slowest run of 511 s budgets 1080 s — never a percentage that a slow host
# eats, and clamped loudly, as the lease is.

SECONDS_COLUMN = 1
# The child's user and sys CPU seconds — the columns `membudget` writes from `/usr/bin/time`.
CPU_COLUMNS = (4, 5)
FLOOR_S = 120
CEILING_S = 3600
# A deadline is this many times the slowest recorded run.
MARGIN = 2
# ⚑⚑ RULED 2026-09-20 (W8): *"Use cputime for your timing gate, not wall time."* Wall time is the
# box plus the work; CPU time is the work. So the deadline is budgeted from BOTH histories and
# takes the larger: MARGIN over the slowest wall (an honest run that was observed must never be
# killed), and HANG_MULTIPLE over the slowest CPU (a multi-threaded run's work exceeds its wall,
# and a loaded box stretches an unchanged workload). The wall figure is only ever a hang guard;
# `Deadline.cpu_s` is the expectation a suite's own cost is judged against.
HANG_MULTIPLE = 4
_MINUTE = 60


def child_cpu() -> float:
    """Return the CPU seconds (user + sys) every reaped child of this process has consumed.

    ⚑ CUMULATIVE, SO A CALLER TAKES A DELTA around one `subprocess.run` — which waits and reaps
    before returning, on the timeout path too, so the delta is that child's own cost.
    """
    import resource  # noqa: PLC0415

    used = resource.getrusage(resource.RUSAGE_CHILDREN)
    return used.ru_utime + used.ru_stime


@dataclass(frozen=True, slots=True)
class Deadline:
    """A wall-time budget sized from history, and what the history said."""

    label: str
    # The timeout to run under, in whole seconds, already rounded and clamped.
    timeout_s: int
    # The slowest run on record, or None when the label has no history.
    slowest_s: float | None
    clamped: bool
    # The most CPU any recorded run spent (user + sys), or None when no row carried it.
    cpu_s: float | None = None

    @property
    def why(self) -> str:
        """Return what a caller should be told, empty when there is nothing to say."""
        if not self.clamped or self.slowest_s is None:
            return ""
        return (
            f"membudget: {self.label} ran {self.slowest_s:.0f}s at its slowest but the "
            f"time ceiling is {CEILING_S}s — budgeting {self.timeout_s}s, which may kill an "
            f"honest run; raise the ceiling or name a timeout explicitly"
        )


def seconds(ledger: Path, label: str) -> tuple[float, ...]:
    """Return every recorded wall time for one label, in the order written."""
    try:
        text = ledger.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ()
    out: list[float] = []
    for line in text.splitlines():
        row = line.split("\t")
        if len(row) <= SECONDS_COLUMN or row[LABEL_COLUMN] != label:
            continue
        try:
            out.append(float(row[SECONDS_COLUMN].strip()))
        except ValueError:
            continue
    return tuple(out)


def cpu_seconds(ledger: Path, label: str) -> tuple[float, ...]:
    """Return every recorded CPU cost (user + sys) for one label, in the order written.

    ⚑ A ROW WITHOUT THE CPU COLUMNS IS SKIPPED, NOT READ AS ZERO. Rows written before the probe
    existed (or on a host without `/usr/bin/time`, G450) carry no CPU figure; a zero would
    budget a hang guard from nothing and read as a measured cheap run.
    """
    try:
        text = ledger.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ()
    out: list[float] = []
    for line in text.splitlines():
        row = line.split("\t")
        if len(row) <= max(CPU_COLUMNS) or row[LABEL_COLUMN] != label:
            continue
        try:
            out.append(sum(float(row[c].strip()) for c in CPU_COLUMNS))
        except ValueError:
            continue
    return tuple(out)


def minutes_up(secs: float, floor: int = FLOOR_S) -> int:
    """Return `secs` rounded UP to a whole minute, never below the floor."""
    whole = int(-(-secs // _MINUTE)) * _MINUTE
    return max(floor, whole)


def deadline(ledger: Path, label: str, default_s: int, ceiling_s: int = CEILING_S) -> Deadline:
    """Budget a wall hang guard for one label from its slowest run, or hand back the default.

    The guard is the larger of MARGIN x the slowest wall and HANG_MULTIPLE x the slowest CPU
    (see the ruling at `HANG_MULTIPLE`), rounded up to a minute and clamped loudly.
    """
    cap = max(ceiling_s, default_s)
    found = seconds(ledger, label)
    if not found:
        return Deadline(label=label, timeout_s=default_s, slowest_s=None, clamped=False)
    slowest = max(found)
    worked = cpu_seconds(ledger, label)
    cpu = max(worked) if worked else None
    want = minutes_up(max(slowest * MARGIN, (cpu or 0.0) * HANG_MULTIPLE))
    if want > cap:
        return Deadline(label=label, timeout_s=cap, slowest_s=slowest, clamped=True, cpu_s=cpu)
    return Deadline(label=label, timeout_s=want, slowest_s=slowest, clamped=False, cpu_s=cpu)


if __name__ == "__main__":
    from pathlib import Path

    _MIN_ARGS = 3
    if len(sys.argv) < _MIN_ARGS:
        sys.stderr.write("usage: label_lease.py <ledger> <label> [default-mb]\n")
        sys.exit(2)

    _default = int(sys.argv[3]) if len(sys.argv) > _MIN_ARGS else 192
    _got = size(Path(sys.argv[1]), sys.argv[2], _default)
    if _got.why:
        sys.stderr.write(_got.why + "\n")
    sys.stdout.write(f"{_got.lease_mb}\n")
    sys.exit(0)
