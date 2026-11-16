#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read the engine's grade ladder — the rungs, and what falls below a floor.

⚑⚑⚑ THE LADDER IS THE ENGINE'S AND MUST BE READ, NEVER RESTATED. `paperkit.grade` defines the
rungs (`broken` -1, `vacuous` 0, `indeterminate` 1, `existence` 2, `behavioral` 3, `imported` 4)
and says why listing them by hand is wrong: *"Listing rungs by hand is how a report comes to omit
one and quietly under-count its own population."* A local copy goes stale in the direction that
reports a NEW rung as an unknown grade — a false finding pointing at correct work.

⚑⚑ THE STUB HAD TO DECLARE THE WHOLE MODULE, AND THAT IS A MEASURED DEPARTURE FROM `bib.pyi`.
`stubtest` in strict mode requires every runtime name to be present, so a stub carrying only the
three names this repo reads failed with eleven "not present in stub" errors for names nobody here
calls. The narrowness `bib.pyi` argues for buys silence only with an allowlist that must then be
maintained against someone else's edits. The ladder module is a LEAF — *"pure data and one pure
function, no engine imports"* — so declaring all of it is cheap and has no transitive surface.

⚑⚑ AND THE GATE THAT VERIFIES STUBS COULD NOT SEE EITHER OF THEM. MEASURED:
`check_stub_authority.py` globs `stubs/*.pyi` NON-RECURSIVELY, so it verifies exactly one
top-level stub and reports *"clean (1 stub(s) match)"* while three package stub directories
(`networkx`, `panflute`, `paperkit`) go unverified. This stub was checked by running `stubtest`
directly. Filed as ⟡stub-gate-nonrecursive — it is a live gate, and widening what it enumerates
would newly surface three unverified stubs, which is a gate-state change rather than a repair to
make in passing.

⚑ THE REACH IS CONFINED HERE, narrowed at the seam, so every consumer downstream stays typed —
the same construction `engine_edges` uses for the bib field roster.
"""

from __future__ import annotations

import sys

import paperkit.grade

# The engine attribute holding the rung ladder: grade name -> rank.
LADDER_ATTR = "RANK_C"

# The rung a witness must reach to be more than an existence check. ⚑ NAMED, NOT INLINED: the
# floor is a policy THIS repo holds, while the LADDER is the engine's — two different authorities,
# and conflating them is how a local copy of someone else's rungs gets written.
FLOOR = "behavioral"


def ladder() -> dict[str, int]:
    """Return the engine's rung ladder.

    ⚑ A FUNCTION, NOT A MODULE CONSTANT, so the read happens at CALL time. A constant binds at
    import and freezes whatever the engine held then — the same staleness a hand-copied ladder
    has, moved one layer in and made harder to see.
    """
    return dict(paperkit.grade.RANK_C)


def rungs() -> tuple[str, ...]:
    """Return every grade the ladder defines, strongest first.

    ⚑ SORTED BY THE PAIR, NOT BY A KEY LAMBDA. An inline `key=lambda name: -got[name]` infers
    `Callable[[Any], int]` under the strict bar and carries that `Any` into the result — the same
    untyped-lambda defect a `re.sub` replacement hit elsewhere in this tree. Ordering `(rank,
    name)` tuples needs no key at all, and ties break by name rather than by dict order.
    """
    return tuple(name for _rank, name in sorted(((-got, name) for name, got in ladder().items())))


def rank(grade: str) -> int | None:
    """Return a grade's rank, or None when the ladder does not define it.

    ⚑ NONE IS NOT ZERO. `vacuous` ranks 0 and `broken` ranks -1, so a reader mapping an unknown
    grade onto 0 would silently call it vacuous — a real rung — instead of reporting that the
    ladder has no such name.
    """
    return ladder().get(grade)


def below(floor: str = FLOOR) -> tuple[str, ...]:
    """Return the grades that FAIL a floor, derived from the ladder rather than listed.

    ⚑⚑ DERIVED SO THE CHECK FAILS CLOSED, which is the engine's own argument: *"Stated as a
    blacklist it would admit every future rung by default; stated as `rank < rank(floor)` a new
    rung is judged the moment it exists."*

    ⚑ AN UNKNOWN FLOOR YIELDS NOTHING RATHER THAN EVERYTHING. A typo'd floor grading every rung
    as failing would be loud; one grading none would be silent, and silence is the direction that
    ships.
    """
    bar = rank(floor)
    if bar is None:
        return ()
    return tuple(name for name, got in sorted(ladder().items()) if got < bar)


if __name__ == "__main__":
    sys.stdout.write(f"  ladder: {', '.join(rungs())}\n")
    sys.stdout.write(f"  below {FLOOR}: {', '.join(below())}\n")
    sys.exit(0)
