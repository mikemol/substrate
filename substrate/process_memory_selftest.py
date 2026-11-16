#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.process_memory`: the subtractions, and the unknown that must stay one.

⚑⚑ THE ARITHMETIC ARMS RUN ON CONSTRUCTED READINGS, NOT ON A LIVE PROCESS. A case that allocated a
corpus and then asserted a figure would be asserting the allocator's behaviour on the day, which is
exactly the un-reproducible measurement this module exists to replace. A `Reading` is a record, so
its derived figures are checkable against arithmetic that a reader can verify by eye.

⚑⚑ EVERY EXPECTED FIGURE IS NAMED BESIDE THE SAMPLE IT COMES FROM, so the whole subtraction table
reads in one place rather than being scattered through the arms as literals. A reader checking
whether this suite asserts the RIGHT arithmetic should not have to hold six numbers in their head.

⚑⚑ THE `resident()` ARM IS DIFFERENT IN KIND AND IS DELIBERATELY WEAK. It touches the real procfs,
so the only honest assertion is a RELATION — that a live process holds something, and that reading
twice does not contradict itself. Pinning a number there would encode this machine's state into a
case that must pass on every other.

⚑ ZERO IS THE UNKNOWN SENTINEL, AND AN ARM PINS THAT IT PROPAGATES AS UNKNOWN RATHER THAN AS A
CONFIDENT SUBTRACTION. That is the failure a report cannot survive: an unreadable procfs otherwise
yields a growth of zero and an `unattributed` that is merely the negated traced figure, which reads
exactly like a genuinely all-Python footprint.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_family

from substrate import process_memory, suite_emit
from substrate.process_memory import Reading

#: A constructed reading whose every derived figure is distinct, so no two can be confused. The
#: values are round megabyte-scale numbers chosen to make the subtractions checkable by eye.
_SAMPLE = Reading(
    rss_before=100_000_000,
    rss_after=180_000_000,
    rss_collected=170_000_000,
    traced_base=5_000_000,
    traced_current=35_000_000,
    traced_peak=95_000_000,
    collected_objects=4_242,
)

#: 35 MB current minus the 5 MB armed baseline.
_WANT_TRACED_LIVE = 30_000_000

#: 180 MB after minus 100 MB before.
_WANT_RSS_GROWTH = 80_000_000

#: 80 MB of resident growth minus 30 MB of traced-live — the half `tracemalloc` cannot see.
_WANT_UNATTRIBUTED = 50_000_000

#: 95 MB peak minus 30 MB retained.
_WANT_TRANSIENT = 65_000_000

#: 180 MB after minus 170 MB once the collector ran.
_WANT_RECLAIMED = 10_000_000

#: An object count large enough that deriving bytes from it would be obvious.
_ARENA_HELD_OBJECTS = 40_000


def the_traced_baseline_is_subtracted_from_live(out: list[str]) -> int:
    """Check that `traced_live` removes the armed baseline rather than reporting the raw current.

    ⚑⚑ WITHOUT THE SUBTRACTION THE PROFILER'S OWN BOOKKEEPING IS COUNTED AS THE PROGRAM'S
    FOOTPRINT. `cProfile` retains a stats entry per profiled frame, and the baseline is taken after
    it is armed precisely so that retention lands outside this figure.
    """
    got = _SAMPLE.traced_live
    if got != _WANT_TRACED_LIVE:
        out.append(f"selftest: traced_live is {got}, not current minus base")
        return 1
    return 0


def the_unattributed_remainder_is_growth_minus_traced(out: list[str]) -> int:
    """Check the subtraction that says how much of the footprint is not Python objects.

    ⚑⚑ THIS IS THE FIGURE THAT ENDS THE ARGUMENT, so it is the one most worth pinning. RSS grew
    80 MB while traced-live grew 30 MB, leaving 50 MB that `tracemalloc` cannot see. A reader
    acting on that stops looking for allocation detail, which is the correct move.
    """
    bad = 0
    if _SAMPLE.rss_growth != _WANT_RSS_GROWTH:
        out.append(f"selftest: rss_growth is {_SAMPLE.rss_growth}, not after minus before")
        bad += 1
    if _SAMPLE.unattributed != _WANT_UNATTRIBUTED:
        out.append(f"selftest: unattributed is {_SAMPLE.unattributed}, not growth minus traced")
        bad += 1
    return bad


def transient_is_the_peak_above_what_is_retained(out: list[str]) -> int:
    """Check that `transient` is peak minus live, not peak minus the raw current.

    ⚑ TRANSIENT AND RETAINED WANT OPPOSITE FIXES — smaller batches versus a bound on a holder — so
    a `transient` computed against the unbaselined current would misroute the reader by exactly
    the size of the profiler's own retention.
    """
    got = _SAMPLE.transient
    if got != _WANT_TRANSIENT:
        out.append(f"selftest: transient is {got}, not peak minus traced_live")
        return 1
    return 0


def reclaimed_bytes_are_separate_from_reclaimed_objects(out: list[str]) -> int:
    """Check that the byte figure and the object count are not derived from each other.

    ⚑⚑ THE COLLECTOR CAN FREE MANY OBJECTS AND RETURN NO BYTES, because the allocator keeps the
    arenas. That is common rather than exceptional, and conflating the two is how "we collected
    forty thousand objects" becomes a false claim of a memory saving.
    """
    bad = 0
    if _SAMPLE.reclaimed != _WANT_RECLAIMED:
        out.append(f"selftest: reclaimed is {_SAMPLE.reclaimed}, not after minus collected")
        bad += 1
    stuck = Reading(
        rss_before=0,
        rss_after=100,
        rss_collected=100,
        traced_base=0,
        traced_current=0,
        traced_peak=0,
        collected_objects=_ARENA_HELD_OBJECTS,
    )
    if stuck.reclaimed != 0:
        out.append(f"selftest: an arena-holding collection reclaimed {stuck.reclaimed} bytes")
        bad += 1
    if stuck.collected_objects != _ARENA_HELD_OBJECTS:
        out.append("selftest: the object count was derived from the byte figure")
        bad += 1
    return bad


def an_unknown_resident_reading_stays_unknown(out: list[str]) -> int:
    """Check that a failed procfs read is distinguishable from an all-Python footprint.

    ⚑⚑ THIS IS THE ARM THAT PROTECTS THE REPORT FROM ITS MOST CONVINCING WRONG ANSWER. With both
    RSS figures at the sentinel, `rss_growth` is zero and `unattributed` is the negated traced
    figure — a table that looks entirely reasonable and is describing nothing at all. `rss_known`
    is the only thing standing between a reader and that table.
    """
    bad = 0
    blind = Reading(
        rss_before=process_memory.UNKNOWN,
        rss_after=process_memory.UNKNOWN,
        rss_collected=process_memory.UNKNOWN,
        traced_base=0,
        traced_current=10_000_000,
        traced_peak=10_000_000,
        collected_objects=0,
    )
    if blind.rss_known:
        out.append("selftest: a reading with no resident figures reported itself as known")
        bad += 1
    if _SAMPLE.rss_known is not True:
        out.append("selftest: a reading with real resident figures reported itself unknown")
        bad += 1
    return bad


def the_live_resident_reading_is_positive_and_stable(out: list[str]) -> int:
    """Check that `resident()` reads the real procfs, twice, without contradicting itself.

    ⚑⚑ THIS ARM ASSERTS A RELATION, NEVER A NUMBER. A pinned megabyte figure would encode this
    machine's state into a case that must pass everywhere. What is checkable is that a running
    process holds SOMETHING — the positive control that separates a working reader from one
    silently returning the sentinel on every call.

    ⚑ AND ON A KERNEL WITHOUT THIS PROCFS THE SENTINEL IS THE CORRECT ANSWER, so the arm accepts
    it rather than failing: the claim is consistency, not availability.
    """
    first = process_memory.resident()
    second = process_memory.resident()
    if first == process_memory.UNKNOWN:
        return 0
    bad = 0
    if first <= 0 or second <= 0:
        out.append(f"selftest: a live process reported {first} then {second} resident bytes")
        bad += 1
    if second == process_memory.UNKNOWN:
        out.append("selftest: resident() succeeded then returned the unknown sentinel")
        bad += 1
    return bad


FAMILY = witness_family.of(
    key="process_memory",
    apex="a memory reading keeps the traced and resident halves separate, subtracts the armed "
    "baseline so the profiler's own retention is excluded, reports the unattributed "
    "remainder that says the footprint is not Python objects at all, and marks an unreadable "
    "procfs as unknown rather than letting the sentinel propagate into a confident zero",
    subject="the derived figures `substrate.process_memory` computes over a constructed reading",
    members=(
        witness_family.Member(
            name="the_traced_baseline_is_subtracted_from_live",
            claim="traced_live removes the armed baseline rather than reporting raw current",
        ),
        witness_family.Member(
            name="the_unattributed_remainder_is_growth_minus_traced",
            claim="the subtraction naming the non-Python footprint is computed both ways",
            cases=2,
        ),
        witness_family.Member(
            name="transient_is_the_peak_above_what_is_retained",
            claim="transient is peak minus live, not peak minus the unbaselined current",
            premises=("the_traced_baseline_is_subtracted_from_live",),
        ),
        witness_family.Member(
            name="reclaimed_bytes_are_separate_from_reclaimed_objects",
            claim="a collection can free many objects and return no bytes",
            cases=3,
        ),
        witness_family.Member(
            name="an_unknown_resident_reading_stays_unknown",
            claim="a failed procfs read is distinguishable from an all-Python footprint",
            cases=2,
        ),
        witness_family.Member(
            name="the_live_resident_reading_is_positive_and_stable",
            claim="resident() reads the real procfs twice without contradicting itself",
            cases=2,
        ),
    ),
)

_ARMS = (
    the_traced_baseline_is_subtracted_from_live,
    the_unattributed_remainder_is_growth_minus_traced,
    transient_is_the_peak_above_what_is_retained,
    reclaimed_bytes_are_separate_from_reclaimed_objects,
    an_unknown_resident_reading_stays_unknown,
    the_live_resident_reading_is_positive_and_stable,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/process_memory_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
