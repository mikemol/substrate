#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.profile_join`: the join key, the three verdicts, and the outer arm.

⚑⚑ EVERY ARM HERE RUNS WITHOUT ARMING A PROFILER, and that is the property the split bought rather
than a convenience this suite happens to enjoy. The module under test takes two mappings, so the
classification a reader acts on is asserted against constructed inputs in milliseconds — instead of
being inferred from whatever a real several-second target happened to allocate on the day.

⚑⚑ THE THREE VERDICTS WANT OPPOSITE FIXES, WHICH IS WHY EACH IS PINNED SEPARATELY. Compute-bound
wants a better algorithm, repeated-work-over-large-objects wants memoisation at the owner, and
RETENTION wants a bound on a cache. A suite that only checked "a verdict was produced" would pass
on a module that sent every reader to the same wrong fix.

⚑ THE FILTER ARMS ARE WHERE THE POLARITY TRAPS LIVE. The cost filter needs `or` and the
repeated-work filter needs `and`, and each has an arm that fails ONLY if that polarity is flipped —
a flip that leaves every other row in the report looking entirely normal.
"""

from __future__ import annotations

import sys
from pathlib import Path

from mikemol.witness import witness_family

from substrate import profile_join, suite_emit
from substrate.profile_join import Allocation, Site, Timing

#: A block count carried through the join, distinctive enough that reading it back proves the
#: allocation ARRIVED rather than being defaulted. ⚑ `Allocation(0, 0)` IS THE MISS SENTINEL, so an
#: arm checking a zero-valued field cannot tell a successful match from a silent miss.
CARRIED_BLOCKS = 7


def the_join_matches_on_location_ignoring_funcname(out: list[str]) -> int:
    """Check that a `pstats` row meets its `tracemalloc` row despite carrying a function name.

    ⚑⚑ KEYING ON `funcname` TOO WOULD MATCH NOTHING AT ALL. `tracemalloc` has no name to offer, so
    a three-part key yields an empty inner arm beside a complete outer one — which reads exactly
    like "the program allocated but never ran", the most plausible-looking wrong answer available.
    """
    bad = 0
    site = Site("/tree/a.py", 10, "walk")
    result = profile_join.join(
        {site: Timing(calls=1, cumulative=2.0)},
        {Site("/tree/a.py", 10): Allocation(size=5_000_000, blocks=CARRIED_BLOCKS)},
    )
    if len(result.rows) != 1:
        out.append(f"selftest: expected one joined row, got {len(result.rows)}")
        return 1
    if result.rows[0].allocation.blocks != CARRIED_BLOCKS:
        out.append("selftest: the allocation did not reach the row — join keyed on funcname")
        bad += 1
    if result.orphans:
        out.append("selftest: a matched site was also reported as an orphan")
        bad += 1
    return bad


def an_allocating_site_with_no_call_row_survives(out: list[str]) -> int:
    """Check that the outer arm of the join is returned rather than discarded.

    ⚑⚑ AN INNER JOIN HIDES THE RETAINED-CORPUS CASE THE REPORT EXISTS TO FIND. A module-level
    table or a comprehension allocates with no `pstats` row at all; drop that arm and the one
    defect no other column can reach becomes invisible while the report still looks full.
    """
    result = profile_join.join(
        {Site("/tree/a.py", 10, "walk"): Timing(calls=1, cumulative=2.0)},
        {Site("/tree/big.py", 3): Allocation(size=9_000_000, blocks=2)},
    )
    if len(result.orphans) != 1:
        out.append(f"selftest: the unmatched allocation did not survive ({len(result.orphans)})")
        return 1
    if result.orphans[0].site.filename != "/tree/big.py":
        out.append(f"selftest: wrong orphan site {result.orphans[0].site.filename!r}")
        return 1
    return 0


def a_cold_but_heavy_row_is_kept_and_named_retention(out: list[str]) -> int:
    """Check that high live bytes alone keeps a row, and that it is classified as RETENTION.

    ⚑⚑ AN `and` IN THE COST FILTER WOULD DROP EXACTLY THIS ROW. Cold time with high live bytes is
    the case a lease bisection can never find: it passes the byte threshold and fails the time one,
    so an `and` discards it silently while every other row in the table still appears.
    """
    bad = 0
    site = Site("/tree/cache.py", 44, "load")
    result = profile_join.join(
        {site: Timing(calls=1, cumulative=profile_join.COST_SECONDS / 100)},
        {Site("/tree/cache.py", 44): Allocation(size=int(profile_join.COST_BYTES * 4), blocks=11)},
    )
    if not result.rows:
        out.append("selftest: the cold-time/high-bytes retention row was filtered out")
        return 1
    if result.rows[0].verdict != "RETENTION":
        out.append(f"selftest: expected RETENTION, got {result.rows[0].verdict!r}")
        bad += 1
    return bad


def the_verdicts_separate_the_three_shapes(out: list[str]) -> int:
    """Check that each combination of hot/cold and heavy/light gets its own verdict.

    ⚑ COLLAPSING ANY TWO SENDS THE READER TO THE WRONG FIX WITH FULL CONFIDENCE. This is the arm
    that would catch a refactor which simplified the classification into a single threshold.
    """
    hot = Timing(calls=1, cumulative=profile_join.COST_SECONDS * 2)
    cold = Timing(calls=1, cumulative=0.0)
    heavy = Allocation(size=int(profile_join.COST_BYTES * 2), blocks=1)
    light = Allocation(size=0, blocks=0)
    expected = (
        ("hot/light", hot, light, "compute-bound"),
        ("hot/heavy", hot, heavy, "repeated work over large objects"),
        ("cold/heavy", cold, heavy, "RETENTION"),
    )
    bad = 0
    for label, timing, alloc, want in expected:
        result = profile_join.join(
            {Site("/tree/x.py", 1, "f"): timing}, {Site("/tree/x.py", 1): alloc}
        )
        if not result.rows:
            out.append(f"selftest: {label}: row was filtered out entirely")
            bad += 1
            continue
        got = result.rows[0].verdict
        if got != want:
            out.append(f"selftest: {label}: expected {want!r}, got {got!r}")
            bad += 1
    return bad


def repeated_work_needs_both_the_count_and_the_cost(out: list[str]) -> int:
    """Check that many-but-cheap and few-but-costly are both excluded.

    ⚑⚑ AN `or` HERE FLOODS THE WORKLIST WITH CHEAP LOOPS. Many calls costing nothing in total is
    how a loop looks, not a finding — and this `and` is the exact opposite of the `or` the cost
    filter above requires, which is why both polarities get their own arm.
    """
    picked = profile_join.repeated_work(
        {
            Site("/tree/loop.py", 5, "step"): Timing(
                calls=profile_join.REPEAT_CALLS * 50, cumulative=0.001
            ),
            Site("/tree/slow.py", 9, "solve"): Timing(calls=2, cumulative=90.0),
            Site("/tree/mask.py", 12, "mask"): Timing(
                calls=profile_join.REPEAT_CALLS * 5, cumulative=27.0
            ),
        }
    )
    names = [r.site.funcname for r in picked]
    if names != ["mask"]:
        out.append(f"selftest: expected only the many-and-costly site, got {names}")
        return 1
    return 0


def a_foreign_path_is_left_absolute_when_rendered(out: list[str]) -> int:
    """Check that a frame outside the root stays absolute while one inside goes relative.

    ⚑⚑ `os.path.relpath` RENDERS A STDLIB FRAME AS `../../../usr/lib/...`, which reads as though
    the tree contains it. A reader then chases a path that does not exist in their checkout. Both
    halves are asserted: rendering everything absolute would be just as wrong in the other
    direction, and an arm checking only the foreign case would accept it.
    """
    bad = 0
    root = Path("/tree")
    inside = Site("/tree/pkg/a.py", 7, "f").display(root)
    outside = Site("/usr/lib/python3.13/pstats.py", 3, "g").display(root)
    if inside != "pkg/a.py:7":
        out.append(f"selftest: a path under the root should render relative, got {inside!r}")
        bad += 1
    if outside != "/usr/lib/python3.13/pstats.py:3":
        out.append(f"selftest: a foreign path should stay absolute, got {outside!r}")
        bad += 1
    return bad


def live_bytes_can_outrank_a_marginally_slower_site(out: list[str]) -> int:
    """Check that the ranking lets a large allocation beat a slightly larger time.

    ⚑ A TIME-ONLY SORT BURIES THE RETENTION CASE AT THE BOTTOM of the table — making the report's
    most valuable row the last one a reader reaches, which for a truncated table means never.
    """
    result = profile_join.join(
        {
            Site("/tree/a.py", 1, "quick"): Timing(1, profile_join.COST_SECONDS * 1.1),
            Site("/tree/b.py", 2, "holder"): Timing(1, profile_join.COST_SECONDS * 1.05),
        },
        {Site("/tree/b.py", 2): Allocation(size=100_000_000, blocks=3)},
    )
    order = [r.site.funcname for r in result.rows]
    if not order or order[0] != "holder":
        out.append(f"selftest: the 100MB site should outrank a marginally slower one, got {order}")
        return 1
    return 0


FAMILY = witness_family.of(
    key="profile_join",
    apex="joining a time profile against an allocation profile on (file, line) keeps both arms — "
    "matched rows and allocating sites with no call row — classifies each matched row into "
    "the three shapes that want opposite fixes, and ranks live bytes against time at a "
    "stated exchange rate so the retention case is reachable in a truncated table",
    subject="the pure join `substrate.profile_join` performs over two constructed mappings",
    members=(
        witness_family.Member(
            name="the_join_matches_on_location_ignoring_funcname",
            claim="a pstats row meets its tracemalloc row despite carrying a function name",
            cases=2,
        ),
        witness_family.Member(
            name="an_allocating_site_with_no_call_row_survives",
            claim="the outer arm of the join is returned rather than discarded",
        ),
        witness_family.Member(
            name="a_cold_but_heavy_row_is_kept_and_named_retention",
            claim="high live bytes alone keeps a row, and it is classified RETENTION",
        ),
        witness_family.Member(
            name="the_verdicts_separate_the_three_shapes",
            claim="hot/light, hot/heavy and cold/heavy each get their own verdict",
            cases=3,
        ),
        witness_family.Member(
            name="repeated_work_needs_both_the_count_and_the_cost",
            claim="many-but-cheap and few-but-costly are both excluded",
        ),
        witness_family.Member(
            name="a_foreign_path_is_left_absolute_when_rendered",
            claim="a frame outside the root stays absolute while one inside goes relative",
            cases=2,
        ),
        witness_family.Member(
            name="live_bytes_can_outrank_a_marginally_slower_site",
            claim="the ranking lets a large allocation beat a slightly larger time",
            premises=("the_verdicts_separate_the_three_shapes",),
        ),
    ),
)

_ARMS = (
    the_join_matches_on_location_ignoring_funcname,
    an_allocating_site_with_no_call_row_survives,
    a_cold_but_heavy_row_is_kept_and_named_retention,
    the_verdicts_separate_the_three_shapes,
    repeated_work_needs_both_the_count_and_the_cost,
    a_foreign_path_is_left_absolute_when_rendered,
    live_bytes_can_outrank_a_marginally_slower_site,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/profile_join_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
