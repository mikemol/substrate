#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the concentration reader, and pin it AGAINST the authority it groups.

⚑⚑⚑ THE LOAD-BEARING CASE IS THE DIFFERENTIAL, because this reader's whole job is to regroup
another reader's output and the failure mode is a partition that does not match. My first cut had
three buckets where `arm_claims` has four, so every arm asserting NOTHING was counted as a
multi-claim arm and the blocked population read larger than the tree's. The totals disagreed by
exactly the silent count — and nothing but a cross-reader comparison would have caught it.

⚑⚑ SO THE SUITE ASSERTS AGREEMENT WITH THE AUTHORITY ON THE LIVE TREE, not against a fixture. A
fixture would only prove the grouping agrees with my transcription of the partition, which is the
very thing that was wrong. The census is read from `arm_claims` at suite time and never typed in.

⚑ AND THE NEGATIVE CONTROL IS THE ONE MOST LIKELY TO BE MISSING. A `blocked` predicate stuck at
True satisfies every positive row here — so a suite with only single-claim arms is asserted CLEAN,
and a suite with a silent arm and no multi-claim arm is asserted clean too, which is the exact
case the partition bug got wrong.
"""

from __future__ import annotations

import sys

from substrate import arm_claims, claim_concentration

Case = tuple[str, bool]

_TWO = 2
_THREE = 3


def _made(**kinds: int) -> tuple[arm_claims.Claims, ...]:
    """Build a census fixture: `single`, `several`, `silent` and `unread` arm counts."""
    out: list[arm_claims.Claims] = []
    for _ in range(kinds.get("single", 0)):
        out.append(arm_claims.Claims("a.py", f"one{len(out)}", 1, ""))
    for _ in range(kinds.get("several", 0)):
        out.append(arm_claims.Claims("a.py", f"many{len(out)}", 3, ""))
    for _ in range(kinds.get("silent", 0)):
        out.append(arm_claims.Claims("a.py", f"quiet{len(out)}", 0, ""))
    for _ in range(kinds.get("unread", 0)):
        out.append(arm_claims.Claims("a.py", f"unread{len(out)}", None, "not modelled"))
    return tuple(out)


def _partition_cases() -> list[Case]:
    """Return the cases pinning the four-way partition — the bug this suite exists for."""
    rows = claim_concentration.group(_made(single=2, several=3, silent=1, unread=1))
    row = rows[0]
    return [
        ("one suite is grouped", len(rows) == 1),
        ("single arms are counted", row.single == _TWO),
        ("several arms are counted", row.several == _THREE),
        # ⚑ THE MEASURED BUG. A silent arm has count 0 and an `else` branch beside `several`
        #   swallows it, inflating the blocked population by every silent arm in the tree.
        ("a silent arm is its OWN bucket, not several", row.silent == 1),
        ("an unread arm is its own bucket", row.undecided == 1),
        ("every arm is accounted for", row.arms == 2 + 3 + 1 + 1),
    ]


def _blocked_cases() -> list[Case]:
    """Return the cases pinning what a rollup rule would and would not block."""
    blocking = claim_concentration.group(_made(single=1, several=1))
    clean = claim_concentration.group(_made(single=3))
    quiet = claim_concentration.group(_made(single=1, silent=2))
    return [
        ("a suite with a multi-claim arm is BLOCKED", blocking[0].blocked),
        # ⚑ THE CONTROL: without these a `blocked` stuck at True passes every row above.
        ("a suite of single-claim arms is CLEAN", not clean[0].blocked),
        # ⚑⚑ THE CASE THE PARTITION BUG GOT WRONG. Silent arms are a defect of a different kind
        #   and must not block a rollup — `dead_case` is the reader that owns them.
        ("a suite whose only oddity is silence is CLEAN", not quiet[0].blocked),
        ("blocked() returns only blocked suites", len(claim_concentration.blocked(blocking)) == 1),
        ("blocked() returns none for a clean suite", len(claim_concentration.blocked(clean)) == 0),
    ]


def _order_cases() -> list[Case]:
    """Return the cases pinning that the heaviest suite is reported first."""
    made = (
        arm_claims.Claims("light.py", "a", 2, ""),
        arm_claims.Claims("heavy.py", "b", 2, ""),
        arm_claims.Claims("heavy.py", "c", 2, ""),
    )
    rows = claim_concentration.group(made)
    return [
        ("both suites are grouped", len(rows) == _TWO),
        # ⚑ THE ORDER IS THE REPORT'S PURPOSE — start with the suite where a paydown buys most.
        ("the heaviest suite is first", rows[0].name == "heavy.py"),
        ("it carries the larger count", rows[0].several == _TWO),
    ]


def _render_cases() -> list[Case]:
    """Return the cases pinning that the render states its own scale and gaps."""
    out = claim_concentration.render(
        claim_concentration.group(_made(single=1, several=2, silent=1, unread=1))
    )
    empty = claim_concentration.render(())
    return [
        ("the render names the blocked population", "BLOCKED" in out),
        # ⚑ THE CLEAN COUNT IS THE SCALE. A price with no scale cannot be read.
        ("it names the clean population too", "CLEAN" in out),
        ("it reports the deciding ratio", "arms per blocked suite" in out),
        ("it reports silent arms as NOT blocking", "not blocking" in out),
        ("it reports the undecided column", "UNDECIDED" in out),
        ("an empty census is a fact about the WALK", "fact about the WALK" in empty),
        # ⚑ NO BLOCKED SUITES MUST NOT DIVIDE BY ZERO — the ratio says so instead.
        (
            "a clean tree reports no ratio rather than crashing",
            "n/a" in claim_concentration.render(claim_concentration.group(_made(single=2))),
        ),
    ]


def _live_cases() -> list[Case]:
    """Assert this reader AGREES with the authority it regroups, on the live tree.

    ⚑⚑ THIS IS THE CASE THAT CAUGHT THE BUG, and it is a differential rather than a reading. The
    claim is not *the grouping totals N* but *the grouping totals what `arm_claims` totals* — and
    only a comparison carries that. It goes red the moment the two partitions diverge again.
    """
    found = arm_claims.census()
    if not found:
        return [("the authority yields a census", False)]
    rows = claim_concentration.group(found)

    several = sum(1 for c in found if c.decided and c.count is not None and c.count > 1)
    silent = sum(1 for c in found if c.count == 0)
    return [
        ("the live census groups into suites", len(rows) > 0),
        # ⚑ THE THREE TOTALS MUST MATCH THE AUTHORITY'S, ARM FOR ARM.
        ("the arm total matches the authority", sum(r.arms for r in rows) == len(found)),
        ("the multi-claim total matches the authority", sum(r.several for r in rows) == several),
        ("the silent total matches the authority", sum(r.silent for r in rows) == silent),
        # And the grouping loses no suite.
        ("every suite in the census has a row", {r.name for r in rows} == {c.suite for c in found}),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = _partition_cases() + _blocked_cases() + _order_cases() + _render_cases() + _live_cases()
    bad = [label for label, holds in cases if not holds]
    print(f"claim_concentration: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
