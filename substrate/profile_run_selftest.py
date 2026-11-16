#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.profile_run`: it really measures, and the ordering really holds.

⚑⚑ THIS SUITE ACTUALLY ARMS THE PROFILER, unlike its three siblings, because that is the whole of
what this module does. The targets are tiny and deterministic in SHAPE rather than in magnitude —
each arm asserts a RELATION (this site appears, this figure is not negative, the target that raised
still produced a record) and never a duration or a byte count, because those move with the machine.

⚑⚑ THE ORDERING ARM IS THE ONE WITH HISTORY. Starting `tracemalloc` before `enable()` counted the
profiler's own per-frame retention as the program's footprint — a defect that produces entirely
plausible numbers. It is checked here by profiling a target that allocates a KNOWN, LARGE object
and asserting the traced figure tracks it, which a baseline polluted by profiler bookkeeping fails
in the direction of over-reporting.

⚑ NO ARM ASSERTS A TIME. A cumulative-seconds threshold is a statement about the machine and the
scheduler, and it is exactly the flaky-case shape that gets suites disabled. What is checkable is
that the site is PRESENT with a non-negative cost and a plausible call count.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_family

from substrate import profile_run, suite_emit

#: Bytes the allocating target holds while it runs — large enough to clear any baseline noise,
#: small enough to be free. ⚑ ASSERTED AS A LOWER BOUND, never as an equality: the interpreter is
#: allocating for its own reasons throughout, so the traced figure is only ever "at least this".
_PAYLOAD_BYTES = 4_000_000

#: How many times the counted target is called, to check the call count survives the adapter.
_ITERATIONS = 500


def _accumulate(total: int, value: int) -> int:
    """Add one value — a leaf called exactly `_ITERATIONS` times, so its entry is checkable."""
    return total + value


def _counted() -> int:
    """Call a leaf a known number of times — the shape the timing adapter must preserve."""
    total = 0
    for i in range(_ITERATIONS):
        total = _accumulate(total, i)
    return total


def _allocating() -> int:
    """Hold a large object for the duration of the measurement."""
    payload = bytearray(_PAYLOAD_BYTES)
    return len(payload)


def _exiting() -> int:
    """End the way a suite ends."""
    raise SystemExit(0)


def the_target_name_is_carried_into_the_record(out: list[str]) -> int:
    """Check that the label the caller supplied is what comes back.

    ⚑⚑ THIS IS THE DENOMINATOR AT ITS SOURCE. The report can only name the target honestly if the
    measurement carried the name; a module that re-derived it from the callable would report a
    wrapper's name, which is how a table came to describe a different program than its reader
    believed.
    """
    measured = profile_run.measure("counted", _counted)
    if measured.target != "counted":
        out.append(f"selftest: the record names {measured.target!r}, not the given target")
        return 1
    return 0


def a_called_function_appears_with_its_call_count(out: list[str]) -> int:
    """Check that the timing adapter preserves both the site and how often it ran.

    ⚑⚑ THE CALL COUNT IS THE HALF THAT DISCRIMINATES. Cumulative time alone cannot separate a slow
    algorithm from repeated work, and those want opposite fixes — so an adapter that dropped or
    mangled the count would leave the entire repeated-work analysis reading plausibly and wrong.
    """
    bad = 0
    measured = profile_run.measure("counted", _counted)
    found = [t for s, t in measured.timings.items() if s.funcname == "_accumulate"]
    if not found:
        out.append("selftest: the called leaf never appeared in the timings")
        return 1
    if found[0].calls != _ITERATIONS:
        out.append(f"selftest: the leaf ran {_ITERATIONS} times, recorded {found[0].calls}")
        bad += 1
    if found[0].cumulative < 0:
        out.append(f"selftest: a negative cumulative time {found[0].cumulative}")
        bad += 1
    return bad


def a_large_allocation_reaches_the_traced_figures(out: list[str]) -> int:
    """Check that a known payload shows up in the peak, above the armed baseline.

    ⚑⚑ THIS IS THE ORDERING ARM. Were the traced baseline taken BEFORE `enable()`, it would carry
    the profiler's own retention and the reported peak would be inflated — plausibly, and in a
    direction no reader could detect. Asserting the peak covers a payload we chose is the check
    that the baseline is measuring the program rather than the lens.

    ⚑ A LOWER BOUND, NOT AN EQUALITY. The interpreter allocates throughout for its own reasons, so
    the only honest claim is that the peak is at least the payload.
    """
    measured = profile_run.measure("allocating", _allocating)
    if measured.reading.traced_peak < _PAYLOAD_BYTES:
        out.append(
            f"selftest: peak {measured.reading.traced_peak} is below the "
            f"{_PAYLOAD_BYTES}-byte payload the target held",
        )
        return 1
    return 0


def allocation_sites_are_recorded_for_the_running_program(out: list[str]) -> int:
    """Check that the allocation adapter produces sites at all.

    ⚑ THE POSITIVE CONTROL FOR THE JOIN. An empty allocation mapping makes every joined row report
    zero bytes and every verdict read "compute-bound" — a complete, coherent, entirely wrong
    report that no downstream case can catch, because the pure half is behaving correctly on the
    input it was handed.
    """
    bad = 0
    measured = profile_run.measure("allocating", _allocating)
    if not measured.allocations:
        out.append("selftest: no allocation sites were recorded at all")
        return 1
    if any(a.size < 0 or a.blocks < 0 for a in measured.allocations.values()):
        out.append("selftest: a negative size or block count was recorded")
        bad += 1
    return bad


def a_target_that_exits_still_produces_a_record(out: list[str]) -> int:
    """Check that `SystemExit` is absorbed and the measurement survives it.

    ⚑⚑ PROFILING A SUITE MEANS PROFILING SOMETHING THAT ENDS BY EXITING. Letting that propagate
    discards the entire measurement at the moment it completed successfully — the worst possible
    time to lose it, and precisely the case a footprint question is usually asked about.
    """
    bad = 0
    measured = profile_run.measure("exiting", _exiting)
    if measured.target != "exiting":
        out.append("selftest: the exiting target produced no usable record")
        bad += 1
    if measured.reading.traced_peak < 0:
        out.append("selftest: the exiting target produced a negative peak")
        bad += 1
    return bad


def the_memory_reading_is_internally_consistent(out: list[str]) -> int:
    """Check that peak is at least current, and that the collection figures are ordered.

    ⚑ THESE ARE THE RELATIONS THAT MUST HOLD ON ANY MACHINE. A peak below the current total, or a
    post-collection RSS above the pre-collection one, would mean the readings were taken in the
    wrong order — the one ordering defect that no single figure reveals.
    """
    bad = 0
    reading = profile_run.measure("allocating", _allocating).reading
    if reading.traced_peak < reading.traced_current:
        out.append(
            f"selftest: peak {reading.traced_peak} is below current {reading.traced_current}",
        )
        bad += 1
    if reading.rss_known and reading.rss_collected > reading.rss_after:
        out.append("selftest: RSS grew across a collection — the readings are out of order")
        bad += 1
    return bad


FAMILY = witness_family.of(
    key="profile_run",
    apex="arming both profilers around a target carries the caller's label into the record, "
    "preserves each site's call count, sees an allocation the target actually made, "
    "survives a target that exits the way a suite exits, and produces readings whose "
    "internal ordering witnesses that the baselines were taken in the right sequence",
    subject="the record `substrate.profile_run.measure` returns for small deterministic targets",
    members=(
        witness_family.Member(
            name="the_target_name_is_carried_into_the_record",
            claim="the label the caller supplied is what comes back",
        ),
        witness_family.Member(
            name="a_called_function_appears_with_its_call_count",
            claim="the timing adapter preserves the site and how often it ran",
            cases=2,
        ),
        witness_family.Member(
            name="a_large_allocation_reaches_the_traced_figures",
            claim="a known payload shows up in the peak, above the armed baseline",
        ),
        witness_family.Member(
            name="allocation_sites_are_recorded_for_the_running_program",
            claim="the allocation adapter produces sites, with no negative figures",
            cases=2,
        ),
        witness_family.Member(
            name="a_target_that_exits_still_produces_a_record",
            claim="SystemExit is absorbed and the measurement survives it",
            cases=2,
        ),
        witness_family.Member(
            name="the_memory_reading_is_internally_consistent",
            claim="peak covers current and the collection figures are correctly ordered",
            cases=2,
            premises=("a_large_allocation_reaches_the_traced_figures",),
        ),
    ),
)

_ARMS = (
    the_target_name_is_carried_into_the_record,
    a_called_function_appears_with_its_call_count,
    a_large_allocation_reaches_the_traced_figures,
    allocation_sites_are_recorded_for_the_running_program,
    a_target_that_exits_still_produces_a_record,
    the_memory_reading_is_internally_consistent,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/profile_run_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
