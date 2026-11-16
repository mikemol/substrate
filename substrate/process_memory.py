#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What this process is holding: resident bytes, and the traced/resident subtraction.

⚑⚑⚑ THE UNATTRIBUTED REMAINDER IS A NUMBER, NOT A CAVEAT. Every memory figure in the superseded
report was traced-only, and four separate attributions reasoned about the gap between traced and
resident without ever reading the resident half. `tracemalloc` counts PYTHON allocations; a cgroup
kills on RSS. Printing the subtraction is what turns "not attributable here" into "this much is not
Python objects" — at which point a reader knows that more allocation detail will not find it,
because it is in C extensions, the interpreter, or allocator arenas.

⚑⚑ THIS IS SELF-MEASUREMENT, AND IT IS A DIFFERENT CAPABILITY FROM THE LEDGER'S `peak_mb`. That
column records the maxRSS of a FINISHED SUBPROCESS, read back from history by `buildtime` and
`label_lease` to size a future lease. This module answers what the CURRENT process is holding right
now, which no ledger can supply and which is the only figure a live profile can subtract against.
The reuse-search fired on this before the module was written and found the two do not overlap.

⚑⚑ THREE RSS READINGS, NOT ONE, BECAUSE ONE CANNOT SEPARATE THE TWO EXPLANATIONS. Bytes a
`gc.collect()` RECLAIMS were cyclic garbage the program had already abandoned; bytes that survive
it are genuinely live, or are arenas Python will not return to the OS. A single figure is
consistent with both and names neither — and libcst-style parent/child linked nodes are exactly the
shape that produces unreachable cycles, so this is not a hypothetical.

⚑⚑ AND THE PROFILER IS A PARTICIPANT IN ITS OWN MEASUREMENT. `cProfile.Profile()` retains a stats
entry per profiled frame for the whole run, so a traced baseline taken BEFORE the profiler is armed
counts the profiler's own bookkeeping as the program's footprint. `Reading.traced_live` subtracts a
baseline the caller is expected to take AFTER arming — which excludes that retention from the
traced figure but NOT from RSS, and `Reading` says so rather than leaving it to a footnote.

⚑ NO `gc.get_count()` BASELINE IS OFFERED, DELIBERATELY. The generational counters say how many
allocations are PENDING inspection, not how much garbage exists; the answerable question is what a
collection RECLAIMS. A recorded number nothing consumes is the dead-field shape this tree censuses.

⚑ IT IMPORTS NOTHING FROM `jea/`, `scripts/` OR `scratch/`, AND NOTHING THAT SPAWNS.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

#: Where the kernel reports this process's resident set, on Linux.
STATUS_PATH = Path("/proc/self/status")

#: The field naming the resident set within that file, whose value is in kibibytes.
RSS_FIELD = "VmRSS:"

#: Bytes per unit of the `VmRSS` value. ⚑ THE FILE REPORTS kB AND MEANS KIBIBYTES.
RSS_UNIT = 1024

#: What `resident()` returns when it cannot read the figure. ⚑ ZERO IS "UNKNOWN", NOT "EMPTY" — a
#: process holding no resident memory is not a thing, so a caller seeing 0 has learned about the
#: READER (a non-Linux kernel, a restricted procfs), never about the process.
UNKNOWN = 0

#: Divisor turning bytes into the megabytes a report shows.
BYTES_PER_MB = 1e6


def resident() -> int:
    """Resident set in bytes, or `UNKNOWN` — the figure a cgroup cap actually kills on.

    ⚑ EVERY MEMORY NUMBER IN THE SUPERSEDED REPORT WAS TRACED-ONLY UNTIL THIS EXISTED. `VmRSS` is
    one line of `/proc/self/status`, and the delta against `tracemalloc` is what says whether a
    footprint is Python objects at all — the question four attributions had reasoned around.

    ⚑ AN UNREADABLE PROCFS RETURNS `UNKNOWN` RATHER THAN RAISING, because a profile that dies
    because it could not read a supplementary figure has destroyed the measurement it was taken
    for. The caller distinguishes the cases with `Reading.rss_known`.
    """
    try:
        with STATUS_PATH.open(encoding="utf-8") as fh:
            for line in fh:
                if line.startswith(RSS_FIELD):
                    return int(line.split()[1]) * RSS_UNIT
    except (OSError, ValueError, IndexError):
        return UNKNOWN
    return UNKNOWN


@dataclass(frozen=True, slots=True)
class Reading:
    """One target's memory story: what was traced, what was resident, and what a collection freed.

    Every field is raw — bytes, or an object count — so the arithmetic that turns them into a
    verdict lives in the properties below rather than in whatever formats the report.
    """

    #: Resident bytes before anything was armed.
    rss_before: int
    #: Resident bytes after the target finished, before any collection.
    rss_after: int
    #: Resident bytes after `gc.collect()` ran.
    rss_collected: int
    #: Traced bytes at the baseline. ⚑ TAKEN AFTER THE PROFILER IS ARMED — see the module note.
    traced_base: int
    #: Traced bytes still live when the target finished.
    traced_current: int
    #: The high-water mark of traced bytes, which is what a cap kills on.
    traced_peak: int
    #: Objects `gc.collect()` reclaimed.
    collected_objects: int

    @property
    def rss_known(self) -> bool:
        """Whether the resident figures mean anything.

        ⚑ WITHOUT THIS, `UNKNOWN` PROPAGATES INTO A CONFIDENT-LOOKING SUBTRACTION: an unreadable
        procfs yields `rss_growth` of 0.0 and an `unattributed` that is merely the negated traced
        figure, which a reader has no way to tell from a genuinely all-Python footprint.
        """
        return self.rss_before != UNKNOWN or self.rss_after != UNKNOWN

    @property
    def traced_live(self) -> int:
        """Traced bytes the target added and still holds, with the armed baseline removed."""
        return self.traced_current - self.traced_base

    @property
    def rss_growth(self) -> int:
        """Resident bytes the target added, before any collection ran."""
        return self.rss_after - self.rss_before

    @property
    def reclaimed(self) -> int:
        """Resident bytes a `gc.collect()` returned — the cyclic-garbage half.

        ⚑ THIS CAN BE ZERO WHILE `collected_objects` IS LARGE. The collector freed the objects; the
        allocator kept the arenas. That is a real and common outcome, not a failed measurement, and
        conflating the two is how "we collected 40,000 objects" becomes a false memory saving.
        """
        return self.rss_after - self.rss_collected

    @property
    def unattributed(self) -> int:
        """Resident growth that `tracemalloc` cannot see: interpreter, C extensions, arenas.

        ⚑ THIS IS THE FIGURE THAT ENDS THE ARGUMENT. A cap exceeded while the traced total reports
        a fraction of it means the footprint is NOT Python objects, so more allocation detail will
        not find it — which is the opposite of the conclusion a traced-only report invites.
        """
        return self.rss_growth - self.traced_live

    @property
    def transient(self) -> int:
        """Traced bytes that peaked and were then released — allocated, used, collected.

        ⚑ PEAK-MINUS-LIVE IS TRANSIENT; LIVE IS RETAINED. They want opposite fixes: transient wants
        the work done once or in smaller batches, retained wants a bound on whatever is holding it.
        """
        return self.traced_peak - self.traced_live
