#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.engine_grades` — reading the ladder rather than restating it.

⚑⚑⚑ THE CASES PIN THE MECHANISM, NOT THE RUNGS. Asserting the exact list would make this suite a
SECOND copy of the engine's ladder — the very thing the module exists to avoid — and it would fail
the day the engine adds a rung, reporting correct upstream work as a defect. What is asserted is
that the reading comes FROM the engine and that the derivations over it hold.

⚑⚑ AND `below()` MUST FAIL CLOSED. The engine's own argument: *"Stated as a blacklist it would
admit every future rung by default; stated as `rank < rank(floor)` a new rung is judged the moment
it exists."* A case pinning the four rungs currently below `behavioral` would freeze that
blacklist here instead.

⚑ THE UNKNOWN-GRADE CASE IS THE SHARP ONE. `vacuous` ranks 0 and `broken` ranks -1, so a reader
mapping an unknown name onto 0 silently calls it vacuous — a REAL rung — rather than reporting
that the ladder has no such name.
"""

from __future__ import annotations

import sys

import paperkit.grade

from substrate import engine_grades


def the_ladder_is_the_engines_own(out: list[str]) -> int:
    """Check the reading is identity with the engine's table.

    ⚑⚑ THE ONLY FAILURE WORTH CATCHING HERE. If this module ever restates the rungs locally, this
    diverges the moment upstream changes — which is precisely when a stale copy does its damage,
    and precisely when nothing else would notice.
    """
    if engine_grades.ladder() != dict(paperkit.grade.RANK_C):
        out.append(f"selftest: the ladder {engine_grades.ladder()!r} is not the engine's")
        return 1
    return 0


def the_ladder_is_not_empty(out: list[str]) -> int:
    """Check the read did not degrade to nothing.

    ⚑ AN EMPTY LADDER WOULD SATISFY THE IDENTITY CASE against an equally empty engine read, and
    would make every derivation below it vacuously true — the collection-destruction shape that
    only a non-empty claim can catch.
    """
    if not engine_grades.ladder():
        out.append("selftest: the ladder read EMPTY — a degraded read, not a ladder")
        return 1
    return 0


def the_rungs_are_ordered_strongest_first(out: list[str]) -> int:
    """Check the ordering is by rank, descending.

    ⚑ ORDER IS THE DISPLAY CONTRACT. A summary listing rungs in dict order would put them in
    insertion sequence — stable, meaningless, and indistinguishable from sorted to a reader.

    ⚑⚑ THE NARROWING IS A COMPREHENSION, NOT A GUARD. A `list[int | None]` filtered by an `any()`
    check is still typed optional and `sorted` refuses it — correctly, since a runtime guard
    proves nothing to the type system. Reading ranks out of the ladder makes the element type
    `int` by construction.
    """
    got = engine_grades.rungs()
    ladder = engine_grades.ladder()
    missing = [name for name in got if name not in ladder]
    if missing:
        out.append(f"selftest: rung(s) with no rank: {missing!r}")
        return 1
    ranks = [ladder[name] for name in got]
    if ranks != sorted(ranks, reverse=True):
        out.append(f"selftest: the rungs are not strongest-first: {got!r}")
        return 1
    return 0


def every_rung_appears_exactly_once(out: list[str]) -> int:
    """Check the ordering neither drops nor duplicates a rung.

    ⚑ A REPORT THAT OMITS A RUNG QUIETLY UNDER-COUNTS ITS OWN POPULATION — the engine's stated
    reason for exposing the ladder at all.
    """
    got = engine_grades.rungs()
    if sorted(got) != sorted(engine_grades.ladder()):
        out.append(f"selftest: the ordering lost or repeated a rung: {got!r}")
        return 1
    return 0


def a_known_grade_has_its_engine_rank(out: list[str]) -> int:
    """Check a rank lookup agrees with the engine for every rung."""
    bad = [name for name, got in paperkit.grade.RANK_C.items() if engine_grades.rank(name) != got]
    if bad:
        out.append(f"selftest: rank disagrees with the engine for {bad!r}")
        return 1
    return 0


def an_unknown_grade_ranks_none_not_zero(out: list[str]) -> int:
    """Check an undefined grade returns None rather than a real rung's rank.

    ⚑⚑ ZERO IS `vacuous`. A reader mapping an unknown name onto 0 would report it as a graded
    check that measured nothing, instead of reporting that the ladder does not define it — a
    plausible verdict about a name the engine has never heard of.
    """
    if engine_grades.rank("no-such-rung") is not None:
        out.append("selftest: an unknown grade returned a rank")
        return 1
    return 0


def below_excludes_the_floor_itself(out: list[str]) -> int:
    """Check the floor is not reported as failing its own bar.

    ⚑ THE COMPARISON IS STRICT. A `<=` would put `behavioral` in the set of grades that fail
    `behavioral`, so a check meeting the bar exactly would be reported as below it.
    """
    if engine_grades.FLOOR in engine_grades.below():
        out.append("selftest: the floor is reported as below itself")
        return 1
    return 0


def below_holds_only_weaker_rungs(out: list[str]) -> int:
    """Check every reported grade really ranks under the floor — derived, not listed.

    ⚑⚑ THIS IS THE FAIL-CLOSED PROPERTY, ASSERTED WITHOUT NAMING THE MEMBERS. Pinning the four
    rungs currently below `behavioral` would freeze a blacklist in the suite and make a new
    upstream rung read as a defect here.
    """
    ladder = engine_grades.ladder()
    bar = ladder.get(engine_grades.FLOOR)
    if bar is None:
        out.append(f"selftest: the floor {engine_grades.FLOOR!r} is not a rung")
        return 1
    bad = [name for name in engine_grades.below() if ladder.get(name, bar) >= bar]
    if bad:
        out.append(f"selftest: below() reported rungs at or above the floor: {bad!r}")
        return 1
    return 0


def below_holds_every_weaker_rung(out: list[str]) -> int:
    """Check nothing weaker than the floor is omitted — the POSITIVE CONTROL.

    ⚑ WITHOUT THIS, A `below()` RETURNING NOTHING would satisfy the case above and silently admit
    every failing grade. The pair says the set is exactly the weaker rungs.
    """
    ladder = engine_grades.ladder()
    bar = ladder.get(engine_grades.FLOOR)
    if bar is None:
        out.append("selftest: the floor is not a rung")
        return 1
    missing = [
        name for name, got in ladder.items() if got < bar and name not in engine_grades.below()
    ]
    if missing:
        out.append(f"selftest: below() omits weaker rungs: {missing!r}")
        return 1
    return 0


def an_unknown_floor_yields_nothing(out: list[str]) -> int:
    """Check a floor the ladder does not define reports no failing grades.

    ⚑⚑ THE SILENT DIRECTION IS THE DANGEROUS ONE, and this arm pins the safe half of a real
    trade. A typo'd floor grading EVERY rung as failing would be loud and obvious; one grading
    none is quiet. Returning nothing is correct because the caller asked about a bar that does not
    exist — but a caller who cannot tell that from a clean tree needs `rank()` to say so, which
    the unknown-grade case above pins.
    """
    if engine_grades.below("no-such-floor") != ():
        out.append("selftest: an unknown floor reported failing grades")
        return 1
    return 0


def the_floor_is_a_real_rung(out: list[str]) -> int:
    """Check this repo's declared floor exists in the engine's ladder.

    ⚑ A FLOOR NAMING NO RUNG MAKES EVERY DERIVATION OVER IT EMPTY, and by the arm above that is
    the silent failure — so the floor's existence is asserted rather than assumed.
    """
    if engine_grades.rank(engine_grades.FLOOR) is None:
        out.append(f"selftest: the declared floor {engine_grades.FLOOR!r} is not a rung")
        return 1
    return 0


_ARMS = (
    the_ladder_is_the_engines_own,
    the_ladder_is_not_empty,
    the_rungs_are_ordered_strongest_first,
    every_rung_appears_exactly_once,
    a_known_grade_has_its_engine_rank,
    an_unknown_grade_ranks_none_not_zero,
    below_excludes_the_floor_itself,
    below_holds_only_weaker_rungs,
    below_holds_every_weaker_rung,
    an_unknown_floor_yields_nothing,
    the_floor_is_a_real_rung,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"engine-grades selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"engine-grades selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
