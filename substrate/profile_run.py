#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Arm the profiler around one target and adapt the stdlib's output into typed records.

⚑⚑⚑ THIS IS THE ONLY HALF THAT CANNOT BE PURE, WHICH IS EXACTLY WHY IT IS SEPARATE. Arming
`cProfile`, starting `tracemalloc`, running an arbitrary callable and collecting garbage are
irreducibly effectful. Everything downstream of them — the join, the classification, the report —
is a function of the records this module produces, and is asserted without any of this running.

⚑⚑ THE BASELINE ORDER IS LOAD-BEARING AND WAS ONCE WRONG. `cProfile.Profile()` RETAINS a stats
entry per profiled frame for the whole run — millions, for a deep walk — and `tracemalloc` was
being started BEFORE `pr.enable()`, so every reported figure counted the profiler's own bookkeeping
as the program's footprint. This is the same class as a reader spying `open()`: measuring through a
lens that is itself part of what is measured. So RSS is read before anything is armed, and the
traced baseline is taken AFTER the profiler is enabled.

⚑⚑ THE SNAPSHOT IS TAKEN IN `finally`, PEAK BEFORE SNAPSHOT, BEFORE `stop()`. `get_traced_memory`
reports `(current, peak)` and the peak is gone the moment tracing stops — and it is the peak a
cgroup kills on. Taking it inside `finally` means a target that RAISES still reports what it
allocated, which is when a footprint question is usually being asked.

⚑⚑ THREE RSS READINGS AROUND ONE COLLECTION, because one figure cannot separate the two
explanations. Bytes a `gc.collect()` reclaims were cyclic garbage already abandoned; bytes that
survive are live, or are arenas Python will not return. `gc.collect()` returns what it reclaimed,
which is a measurement rather than a theory.

⚑⚑ THE TIME PROJECTION IS READ FROM `Profile.getstats()`, NOT FROM `pstats.Stats.stats`. Both hold
the same numbers, but the `pstats` attribute is undeclared in typeshed, so reading it forces the
whole adapter through `Any` — every field arriving untyped at exactly the boundary where a wrong
column silently becomes a wrong verdict. `getstats()` returns typed entries carrying `callcount`
and `totaltime` on a real code object, so the adapter checks.

⚑ `SystemExit` FROM THE TARGET IS CAUGHT, NOT PROPAGATED. Profiling a suite means profiling
something that ends by exiting; letting that escape would discard the entire measurement at the
moment it completed successfully.

⚑ IT IMPORTS NOTHING FROM `jea/`, `scripts/` OR `scratch/`, AND SPAWNS NOTHING. The target arrives
as a callable, so this module never decides WHAT is measured — the caller does, and the report
names it.
"""

from __future__ import annotations

import cProfile
import gc
import tracemalloc
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import process_memory
from substrate.profile_join import Allocation, Site, Timing

if TYPE_CHECKING:
    from collections.abc import Callable

#: Frames of traceback `tracemalloc` retains per allocation. ⚑ ONE IS DELIBERATE: the join keys on
#: the allocating line itself, and deeper tracebacks cost memory inside the measurement.
TRACE_DEPTH = 1

#: Where a builtin's entry reports its origin, having no Python source file of its own.
BUILTIN_FILE = "~"


@dataclass(frozen=True, slots=True)
class Measured:
    """Everything one profiled run produced, in the vocabulary the pure half consumes."""

    #: What was run, as the report will name it. ⚑ THE DENOMINATOR — resolved before anything ran.
    target: str
    #: Per-site cumulative time and call counts.
    timings: dict[Site, Timing]
    #: Per-site live bytes and block counts, from `tracemalloc`.
    allocations: dict[Site, Allocation]
    #: The memory story: traced and resident, before and after a collection.
    reading: process_memory.Reading


def _timings(profiler: cProfile.Profile) -> dict[Site, Timing]:
    """Adapt the profiler's own entries into typed records keyed by site.

    ⚑ `totaltime` HERE IS THE CUMULATIVE FIGURE — time in the frame INCLUDING its callees, which is
    what answers "where does this tool's two minutes go". The per-frame-only figure is
    `inlinetime`, and using it would make every orchestrating function look free while the cost
    scattered across leaves.

    ⚑ A BUILTIN HAS NO SOURCE LOCATION, so it is keyed on its name at line zero. Dropping those
    entries would hide a program whose time is genuinely in C — which is a finding, not noise.
    """
    out: dict[Site, Timing] = {}
    for entry in profiler.getstats():
        code = entry.code
        if isinstance(code, str):
            site = Site(BUILTIN_FILE, 0, code)
        else:
            site = Site(code.co_filename, code.co_firstlineno, code.co_name)
        out[site] = Timing(calls=entry.callcount, cumulative=entry.totaltime)
    return out


def _allocations(snapshot: tracemalloc.Snapshot) -> dict[Site, Allocation]:
    """Adapt a `tracemalloc` snapshot's per-line statistics into typed records."""
    out: dict[Site, Allocation] = {}
    for stat in snapshot.statistics("lineno"):
        frame = stat.traceback[0]
        out[Site(frame.filename, frame.lineno)] = Allocation(size=stat.size, blocks=stat.count)
    return out


def measure(target: str, run: Callable[[], object]) -> Measured:
    """Run `run` under both profilers and return what they saw, without interpreting any of it.

    ⚑⚑ THE TARGET IS RESOLVED AND NAMED BEFORE ANYTHING RUNS, so the label in the report cannot
    drift from what was executed. That drift is the defect this whole instrument was rebuilt
    around: a table read against the wrong program is worse than no table.

    ⚑ THE ORDER HERE IS THE MEASUREMENT. Read the module note before changing it — RSS before
    arming, traced baseline after `enable()`, peak and snapshot inside `finally` before `stop()`,
    and RSS either side of the collection.
    """
    rss_before = process_memory.resident()
    profiler = cProfile.Profile()
    profiler.enable()
    tracemalloc.start(TRACE_DEPTH)
    traced_base = tracemalloc.get_traced_memory()[0]
    try:
        run()
    except SystemExit:
        pass
    finally:
        profiler.disable()
        traced_current, traced_peak = tracemalloc.get_traced_memory()
        snapshot = tracemalloc.take_snapshot()
        tracemalloc.stop()
        rss_after = process_memory.resident()
        collected_objects = gc.collect()
        rss_collected = process_memory.resident()

    return Measured(
        target=target,
        timings=_timings(profiler),
        allocations=_allocations(snapshot),
        reading=process_memory.Reading(
            rss_before=rss_before,
            rss_after=rss_after,
            rss_collected=rss_collected,
            traced_base=traced_base,
            traced_current=traced_current,
            traced_peak=traced_peak,
            collected_objects=collected_objects,
        ),
    )
