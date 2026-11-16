#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Where the multi-claim arms SIT, so the rollup ruling has a price rather than a count.

⚑⚑⚑ WHY THIS EXISTS. `arm_claims` reports how many arms assert several claims, and that number
alone cannot answer the question the operator was asked to rule on: does one multi-claim arm
block its whole module for intake? A rollup rule is CHEAP if the multi-claim arms concentrate in
a few suites and EXPENSIVE if they are spread one-per-suite across the tree — and those two
worlds produce the identical total. The count is real and it is not the deciding quantity.

⚑⚑ SO THIS IS A DISTRIBUTION, NOT A TALLY. It reports, per suite, how the arms partition — and
then the two figures a ruling actually turns on: how many suites are CLEAN (no multi-claim arm,
so a rollup costs them nothing) and how many are BLOCKED (at least one, so a rollup blocks the
whole file). Beside those it prints the arms-per-blocked-suite ratio, which is what separates
"the work concentrates and can be started" from "the work is spread and the rule blocks the tree".

⚑ AND IT REPORTS THE WORST SUITES BY NAME, because "how much work" and "where the work is" are
different questions and only the second one can be started. A suite with many multi-claim arms is
one paydown; forty suites with one each is forty.

⚑⚑⚑ THE PARTITION IS FOUR-WAY BECAUSE `arm_claims` IS, AND MY FIRST CUT MADE IT THREE. An arm
that asserts NOTHING has `count == 0`; folded into an `else` branch beside "several" it was
counted as blocking, which overstated the price by every silent arm in the tree — the exact error
this reader exists to prevent, committed inside it. A silent arm is a defect of its own kind
(`dead_case` is the reader for that) and it is not a multi-claim arm.

⚑⚑ WHAT THIS DOES NOT CLAIM. It reports over SUITES, which is the grain `arm_claims` reads.
`intake_manifest` counts MODULES, and most modules have no suite at all — so a suite counted
blocked here is not thereby a blocked intake module, and the two populations must never be
subtracted from one another. That conflation is what `intake_manifest`'s own banner warns about,
and stating it here keeps the warning attached to the second reader too.

⚑ IT ADDS NO SECOND AUTHORITY. Every figure is grouped from `arm_claims.census()`; nothing here
re-walks a suite or re-counts a claim. A concentration reader that parsed arms itself would be a
rival authority for a question `arm_claims` already answers.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from substrate import arm_claims

# How many of the heaviest suites to name before summarising.
SAMPLE = 12


@dataclass(frozen=True, slots=True)
class Suite:
    """One suite's claim distribution, partitioned the way `arm_claims` partitions."""

    name: str
    single: int
    several: int
    silent: int
    undecided: int

    @property
    def blocked(self) -> bool:
        """Whether a rollup rule would block this whole suite."""
        return self.several > 0

    @property
    def arms(self) -> int:
        """How many arms this suite declares in total."""
        return self.single + self.several + self.silent + self.undecided


def _heaviest_first(row: Suite) -> tuple[int, str]:
    """Sort key: most multi-claim arms first, then by name for a stable order.

    ⚑ NAMED RATHER THAN A LAMBDA because the per-file gate reads an inline lambda's parameter as
    untyped, and an annotated function is the honest fix — the ordering is a claim about what
    this report is FOR (start with the heaviest suite), not incidental plumbing.
    """
    return (-row.several, row.name)


def group(found: tuple[arm_claims.Claims, ...]) -> tuple[Suite, ...]:
    """Return one row per suite, heaviest first.

    ⚑⚑ FOUR BUCKETS, MATCHING THE AUTHORITY. `arm_claims.render` splits single / several / silent
    / undecided, and a grouping with three collapses one of them into another. Mine collapsed
    SILENT into SEVERAL and reported a larger blocked population than the tree has.

    ⚑ AN UNDECIDED ARM IS ITS OWN COLUMN and is NOT counted as several. A reader that could not
    decide an arm has said nothing about whether it asserts one claim or five, and folding it
    into the blocked side would report a gap in this reader as a defect in the suite.
    """
    single: dict[str, int] = {}
    several: dict[str, int] = {}
    silent: dict[str, int] = {}
    undecided: dict[str, int] = {}
    for claim in found:
        if not claim.decided:
            undecided[claim.suite] = undecided.get(claim.suite, 0) + 1
        elif claim.count == 0:
            silent[claim.suite] = silent.get(claim.suite, 0) + 1
        elif claim.single:
            single[claim.suite] = single.get(claim.suite, 0) + 1
        else:
            several[claim.suite] = several.get(claim.suite, 0) + 1

    names = set(single) | set(several) | set(silent) | set(undecided)
    rows = [
        Suite(
            name=n,
            single=single.get(n, 0),
            several=several.get(n, 0),
            silent=silent.get(n, 0),
            undecided=undecided.get(n, 0),
        )
        for n in names
    ]
    return tuple(sorted(rows, key=_heaviest_first))


def blocked(rows: tuple[Suite, ...]) -> tuple[Suite, ...]:
    """Return only the suites a rollup rule would block."""
    return tuple(r for r in rows if r.blocked)


def render(rows: tuple[Suite, ...]) -> str:
    """Render the distribution: how concentrated the multi-claim arms are.

    ⚑ THE CLEAN COUNT IS PRINTED BESIDE THE BLOCKED ONE, because a rollup rule's cost is what it
    blocks and its benefit is what it leaves alone. Printing only the blocked half would state
    the price with no scale to read it against.
    """
    if not rows:
        return "claim-concentration: no suites read — a fact about the WALK, not the tree\n"

    bad = blocked(rows)
    arms = sum(r.arms for r in rows)
    several = sum(r.several for r in rows)
    heaviest = bad[0].several if bad else 0
    # ⚑ THE DECIDING RATIO. Near 1.0 means the work is spread one-arm-per-suite and a rollup
    #   blocks the tree broadly; well above 1.0 means it concentrates and most blocked suites
    #   are one paydown each. Rendered as text so no-blocked-suites says so rather than dividing.
    spread = f"{several / len(bad):.1f}" if bad else "n/a"

    out = [
        f"  {arms} arm(s) across {len(rows)} suite(s)",
        f"    suites CLEAN (no multi-claim arm)       : {len(rows) - len(bad)}",
        f"    suites BLOCKED by a rollup rule         : {len(bad)}",
        f"    multi-claim arms in them                : {several}",
        f"    arms per blocked suite                  : {spread}",
        f"    heaviest single suite                   : {heaviest}",
    ]
    out.extend(
        f"      {r.several:>3} several, {r.single:>3} single   {r.name}" for r in bad[:SAMPLE]
    )
    if len(bad) > SAMPLE:
        out.append(f"      … and {len(bad) - SAMPLE} more blocked suite(s)")

    # ⚑ BOTH PRINTED EVEN AT ZERO. A silent arm and an unread arm are each a different fact from
    #   a cleared one, and a distribution that dropped them would overstate its own reach.
    out.append(f"    arms asserting NOTHING (not blocking)   : {sum(r.silent for r in rows)}")
    out.append(f"    UNDECIDED arms (a fact about the reader): {sum(r.undecided for r in rows)}")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    """Print where the multi-claim arms sit."""
    if argv:
        sys.stderr.write("usage: claim_concentration.py\n")
        return 2
    sys.stdout.write(render(group(arm_claims.census())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
