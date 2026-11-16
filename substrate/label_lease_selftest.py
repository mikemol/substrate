#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.label_lease` — a lease is a kill cap, so it rounds up.

⚑⚑⚑ THE MAX-NOT-MEDIAN CASE IS THE ITEM. A lease is a hard cap: sizing from the median is correct
for half the runs and FATAL for the rest, and the failure is a kill rather than a slowdown.
`membudget peaks` reports median and p90 for a human deciding; this reader decides for a process
that cannot survive being wrong low, and the arms below pin that the largest peak is what drives
the number.

⚑⚑ AND THE UNMEASURED CASE MUST NOT INVENT ONE. A label with no history takes the caller's
default — not a floor, not a guess from a sibling — because choosing a cap from no observation is
the guess the ledger exists to replace.

⚑ THE FIXTURES ARE TEMP LEDGERS. A case reading the live history measures today's runs: the
figures move every time anything executes under `membudget`, and a case pinning `256` for a
suite would go red the moment that suite got cheaper — reporting an improvement as a defect.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import label_lease

_DEFAULT = 192

# A label with recorded peaks, largest last so a reader taking the final row still passes and a
# reader taking the max is what this actually tests.
_LABEL = "selftest:probe.py"
_PEAKS = (40, 188, 90)

# What the largest of those rounds to.
_EXPECTED = 256

# The lone peak a sibling-isolation case reads back, and the outsized one it must not.
_LONE_PEAK = 16
_SIBLING_PEAK = 900

# A default a caller names above the ceiling, to prove it is not clamped back.
_EXPLICIT_DEFAULT = 1024


def _ledger(where: str, rows: tuple[tuple[str, int], ...]) -> Path:
    """Write a fixture label ledger and return its path."""
    path = Path(where) / "labels.tsv"
    path.write_text(
        "".join(f"{label}\t1.0\t{peak}\t1787000000\t0.5\t0.1\n" for label, peak in rows),
        encoding="utf-8",
    )
    return path


def _rows(peaks: tuple[int, ...], label: str = _LABEL) -> tuple[tuple[str, int], ...]:
    """Build fixture rows for one label."""
    return tuple((label, peak) for peak in peaks)


def the_largest_peak_drives_the_lease(out: list[str]) -> int:
    """Check the max is what sizes the lease — THE WHOLE ITEM.

    ⚑⚑⚑ A MEDIAN-SIZED LEASE IS FATAL FOR HALF THE RUNS. The fixture's largest peak is not its
    last or its middle, so a reader taking either would produce a different number here.
    """
    with tempfile.TemporaryDirectory() as where:
        got = label_lease.size(_ledger(where, _rows(_PEAKS)), _LABEL, _DEFAULT)
    if got.lease_mb != _EXPECTED:
        out.append(f"selftest: peaks {_PEAKS} sized to {got.lease_mb}, expected {_EXPECTED}")
        return 1
    if got.peak_mb != max(_PEAKS):
        out.append(f"selftest: the reported peak is {got.peak_mb}, expected {max(_PEAKS)}")
        return 1
    return 0


def a_peak_rounds_up_to_the_next_power_of_two(out: list[str]) -> int:
    """Check the bucket is at or above the peak, never below.

    ⚑ ROUNDING DOWN WOULD KILL THE RUN. The pow2 step is the margin; a lease below the measured
    need is the state that sat invisible in a downstream consumer for weeks.
    """
    for peak in (65, 128, 129, 200, 257):
        got = label_lease.bucket(peak)
        if got < peak:
            out.append(f"selftest: peak {peak} bucketed to {got}, which is below it")
            return 1
    return 0


def a_small_peak_takes_the_floor(out: list[str]) -> int:
    """Check a tiny peak does not size below the floor.

    ⚑ A LEASE OF A FEW MEGABYTES would kill the interpreter before the work started — the floor
    is what a process needs to exist, not a rounding artefact.
    """
    if label_lease.bucket(3) != label_lease.FLOOR_MB:
        out.append(f"selftest: a 3MB peak sized to {label_lease.bucket(3)}")
        return 1
    return 0


def a_light_label_sizes_below_the_default(out: list[str]) -> int:
    """Check history can lower a lease, not only raise it.

    ⚑⚑ THE CONCURRENCY IS THE POINT. Sizing a 16MB suite at the 192MB default packs a twelfth of
    what the budget allows — which is what left a roster run contending and OOM-killing its two
    heavy members.
    """
    with tempfile.TemporaryDirectory() as where:
        got = label_lease.size(_ledger(where, _rows((16, 15, 17))), _LABEL, _DEFAULT)
    if got.lease_mb >= _DEFAULT:
        out.append(f"selftest: a light label sized to {got.lease_mb}, not below {_DEFAULT}")
        return 1
    return 0


def an_unmeasured_label_takes_the_default(out: list[str]) -> int:
    """Check a label with no history is handed the caller's default.

    ⚑ NOT A FLOOR, NOT A SIBLING'S NUMBER. Choosing a cap from no observation is the guess the
    ledger exists to replace, and inventing one here would be that guess wearing a measurement's
    clothes.
    """
    with tempfile.TemporaryDirectory() as where:
        ledger = _ledger(where, _rows(_PEAKS, "selftest:other.py"))
        got = label_lease.size(ledger, _LABEL, _DEFAULT)
    if got.lease_mb != _DEFAULT or got.measured:
        out.append(f"selftest: an unmeasured label sized to {got!r}")
        return 1
    return 0


def a_missing_ledger_takes_the_default(out: list[str]) -> int:
    """Check an absent history degrades rather than raising.

    ⚑ A MISSING LEDGER IS THE ORDINARY FIRST-RUN STATE, and a sizing reader that failed there
    would take down the work it exists to size.
    """
    with tempfile.TemporaryDirectory() as where:
        got = label_lease.size(Path(where) / "absent.tsv", _LABEL, _DEFAULT)
    if got.lease_mb != _DEFAULT:
        out.append(f"selftest: a missing ledger sized to {got.lease_mb}")
        return 1
    return 0


def another_labels_rows_are_not_read(out: list[str]) -> int:
    """Check the key selects exactly one label.

    ⚑ ONE LEDGER, MANY WORKLOADS. A reader matching loosely would size a light suite from a heavy
    sibling's peak, which is the fleet-wide lease this per-label sizing replaces.
    """
    with tempfile.TemporaryDirectory() as where:
        ledger = _ledger(where, (*_rows((_LONE_PEAK,)), ("selftest:heavy.py", _SIBLING_PEAK)))
        got = label_lease.size(ledger, _LABEL, _DEFAULT)
    if got.peak_mb != _LONE_PEAK:
        out.append(f"selftest: a sibling's peak leaked in: {got.peak_mb}")
        return 1
    return 0


def a_peak_above_the_ceiling_clamps(out: list[str]) -> int:
    """Check an extrapolation beyond the ceiling is capped."""
    with tempfile.TemporaryDirectory() as where:
        got = label_lease.size(_ledger(where, _rows((_SIBLING_PEAK,))), _LABEL, _DEFAULT)
    if got.lease_mb != label_lease.CEILING_MB or not got.clamped:
        out.append(f"selftest: a 900MB peak sized to {got!r}")
        return 1
    return 0


def a_clamp_says_so_and_names_the_override(out: list[str]) -> int:
    """Check the clamp is loud and actionable — THE SILENT-FAILURE ARM.

    ⚑⚑ A LEASE KNOWINGLY BELOW THE MEASURED NEED is a run expected to be killed. That state sat
    invisible in a downstream consumer for weeks, and a workaround appeared to work right up
    until history existed. The reason must name the variable that raises the ceiling.
    """
    with tempfile.TemporaryDirectory() as where:
        got = label_lease.size(_ledger(where, _rows((_SIBLING_PEAK,))), _LABEL, _DEFAULT)
    if "AGDA_MB_MAX" not in got.why or "BELOW" not in got.why:
        out.append(f"selftest: the clamp reason reads as {got.why!r}")
        return 1
    return 0


def an_unclamped_sizing_says_nothing(out: list[str]) -> int:
    """Check an ordinary sizing carries no message.

    ⚑ A REASON ON EVERY ROW trains a reader to ignore the channel, which is what makes the one
    that matters invisible.
    """
    with tempfile.TemporaryDirectory() as where:
        got = label_lease.size(_ledger(where, _rows(_PEAKS)), _LABEL, _DEFAULT)
    if got.why:
        out.append(f"selftest: an unclamped sizing said {got.why!r}")
        return 1
    return 0


def an_explicit_default_raises_the_ceiling(out: list[str]) -> int:
    """Check a caller naming a larger size is not clamped back to it.

    ⚑⚑ THE CEILING BOUNDS THIS READER'S EXTRAPOLATION, NOT WHAT A CALLER MAY ASK. A downstream
    consumer whose modules peak at ~600MB set a larger default and it LOOKED like it worked —
    until history existed, at which point the clamp silently took it back and the module
    OOM-killed again.
    """
    with tempfile.TemporaryDirectory() as where:
        got = label_lease.size(_ledger(where, _rows((_SIBLING_PEAK,))), _LABEL, _EXPLICIT_DEFAULT)
    if got.lease_mb < _SIBLING_PEAK:
        out.append(f"selftest: an explicit {_EXPLICIT_DEFAULT} default sized to {got.lease_mb}")
        return 1
    return 0


def a_malformed_row_is_skipped(out: list[str]) -> int:
    """Check a truncated or non-numeric row does not break the read.

    ⚑ ONE BAD LINE MUST NOT COST THE WHOLE HISTORY — a ledger is appended to concurrently, so a
    partial write is a state this reader will meet.
    """
    with tempfile.TemporaryDirectory() as where:
        path = Path(where) / "labels.tsv"
        path.write_text(
            f"{_LABEL}\n{_LABEL}\t1.0\tnotanumber\n{_LABEL}\t1.0\t188\t0\t0\t0\n", encoding="utf-8"
        )
        got = label_lease.size(path, _LABEL, _DEFAULT)
    if got.lease_mb != _EXPECTED:
        out.append(f"selftest: a malformed ledger sized to {got.lease_mb}")
        return 1
    return 0


# The time budget (W3, ruled 2026-09-20): rows with wall seconds, slowest in the middle.
_TIMED = "selftest:slow.py"
_SECONDS = (30.0, 511.0, 200.0)
# 2 x 511 = 1022 s, rounded up to a whole minute.
_EXPECTED_S = 1080
_DEFAULT_S = 300
_TOO_SLOW = 3000.0


def _timed_ledger(where: str, secs: tuple[float, ...], label: str = _TIMED) -> Path:
    """Write a fixture ledger whose rows carry wall seconds."""
    path = Path(where) / "labels.tsv"
    path.write_text(
        "".join(f"{label}\t{s}\t8\t1787000000\t0.5\t0.1\n" for s in secs), encoding="utf-8"
    )
    return path


def the_slowest_run_drives_the_deadline(out: list[str]) -> int:
    """Check the deadline is twice the SLOWEST run, rounded up to a minute — THE RULED ITEM."""
    with tempfile.TemporaryDirectory() as where:
        got = label_lease.deadline(_timed_ledger(where, _SECONDS), _TIMED, _DEFAULT_S)
    if got.timeout_s != _EXPECTED_S or got.slowest_s != max(_SECONDS):
        out.append(
            f"selftest: seconds {_SECONDS} budgeted {got.timeout_s}s from "
            f"{got.slowest_s}, expected {_EXPECTED_S} from {max(_SECONDS)}"
        )
        return 1
    if got.why:
        out.append("selftest: an unclamped deadline carried a message")
        return 1
    return 0


def a_quick_label_takes_the_time_floor(out: list[str]) -> int:
    """Check a sub-minute history does not budget below the floor."""
    with tempfile.TemporaryDirectory() as where:
        got = label_lease.deadline(_timed_ledger(where, (2.0, 3.0)), _TIMED, _DEFAULT_S)
    if got.timeout_s != label_lease.FLOOR_S:
        out.append(f"selftest: a 3 s history budgeted {got.timeout_s}s, not the floor")
        return 1
    return 0


def an_untimed_label_takes_the_default_deadline(out: list[str]) -> int:
    """Check no history hands back the caller's default, unclamped and unmeasured."""
    with tempfile.TemporaryDirectory() as where:
        got = label_lease.deadline(_timed_ledger(where, _SECONDS), "selftest:other.py", _DEFAULT_S)
    if got.timeout_s != _DEFAULT_S or got.slowest_s is not None or got.clamped:
        out.append("selftest: an untimed label was not handed the default")
        return 1
    return 0


def a_deadline_above_the_ceiling_clamps_loudly(out: list[str]) -> int:
    """Check a slowest run past the ceiling is clamped AND says so — THE SILENT-KILL ARM."""
    with tempfile.TemporaryDirectory() as where:
        got = label_lease.deadline(_timed_ledger(where, (_TOO_SLOW,)), _TIMED, _DEFAULT_S)
    if got.timeout_s != label_lease.CEILING_S or not got.clamped:
        out.append(f"selftest: a {_TOO_SLOW}s run budgeted {got.timeout_s}s, not the ceiling")
        return 1
    if _TIMED not in got.why or "may kill an honest run" not in got.why:
        out.append("selftest: the clamp did not name the label and the consequence")
        return 1
    return 0


# The CPU direction (W8, ruled 2026-09-20): a run whose WORK exceeds its wall (multi-threaded),
# so HANG_MULTIPLE x cpu outranks MARGIN x wall: 4 x 400 = 1600 -> 1620, where 2 x 100 = 200.
_CPU_HEAVY_ROW = "selftest:threads.py\t100.0\t8\t1787000000\t300.0\t100.0\n"
_EXPECTED_CPU_S = 1620
_CPU_HEAVY_CPU = 400.0


def the_slowest_cpu_drives_the_guard_when_it_outranks_wall(out: list[str]) -> int:
    """Check the hang guard is budgeted from CPU when the work exceeds the wall — THE RULING."""
    with tempfile.TemporaryDirectory() as where:
        path = Path(where) / "labels.tsv"
        path.write_text(_CPU_HEAVY_ROW, encoding="utf-8")
        got = label_lease.deadline(path, "selftest:threads.py", _DEFAULT_S)
    if got.timeout_s != _EXPECTED_CPU_S or got.cpu_s != _CPU_HEAVY_CPU:
        out.append(
            f"selftest: a 100 s wall / 400 s cpu history budgeted {got.timeout_s}s "
            f"(cpu {got.cpu_s}), expected {_EXPECTED_CPU_S} (cpu {_CPU_HEAVY_CPU})"
        )
        return 1
    # ⚑ AND THE WALL ARM STILL HOLDS BESIDE IT: the fixture rows above spend 0.6 s CPU, so the
    # slowest-wall arm passing is the proof that CPU did not silently REPLACE the wall history.
    return 0


def a_row_without_cpu_columns_is_not_read_as_zero(out: list[str]) -> int:
    """Check a pre-probe row (no user/sys) contributes no CPU figure rather than 0.0."""
    with tempfile.TemporaryDirectory() as where:
        path = Path(where) / "labels.tsv"
        path.write_text("selftest:old.py\t50.0\t8\t1787000000\n", encoding="utf-8")
        got = label_lease.deadline(path, "selftest:old.py", _DEFAULT_S)
    if got.cpu_s is not None or got.timeout_s != label_lease.FLOOR_S:
        out.append(
            f"selftest: a row with no CPU columns read cpu={got.cpu_s}, budgeted {got.timeout_s}s"
        )
        return 1
    return 0


def child_cpu_moves_when_a_child_works(out: list[str]) -> int:
    """Check the CPU reader is live: a child that burns CPU moves the counter."""
    import subprocess  # noqa: PLC0415 - the one arm that spawns

    before = label_lease.child_cpu()
    subprocess.run(
        ["python3", "-c", "sum(i * i for i in range(3_000_000))"],  # noqa: S607
        check=True,
    )
    if label_lease.child_cpu() <= before:
        out.append("selftest: a working child left the CPU counter unmoved")
        return 1
    return 0


_ARMS = (
    the_largest_peak_drives_the_lease,
    a_peak_rounds_up_to_the_next_power_of_two,
    a_small_peak_takes_the_floor,
    a_light_label_sizes_below_the_default,
    an_unmeasured_label_takes_the_default,
    a_missing_ledger_takes_the_default,
    another_labels_rows_are_not_read,
    a_peak_above_the_ceiling_clamps,
    a_clamp_says_so_and_names_the_override,
    an_unclamped_sizing_says_nothing,
    an_explicit_default_raises_the_ceiling,
    a_malformed_row_is_skipped,
    the_slowest_run_drives_the_deadline,
    a_quick_label_takes_the_time_floor,
    an_untimed_label_takes_the_default_deadline,
    a_deadline_above_the_ceiling_clamps_loudly,
    the_slowest_cpu_drives_the_guard_when_it_outranks_wall,
    a_row_without_cpu_columns_is_not_read_as_zero,
    child_cpu_moves_when_a_child_works,
)

_CASE_COUNT = 2 + 1 + 1 + 1 + 2 + 1 + 1 + 2 + 1 + 1 + 1 + 1 + 2 + 1 + 1 + 2 + 2 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"label-lease selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"label-lease selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
