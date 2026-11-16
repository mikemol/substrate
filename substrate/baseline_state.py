#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""A ratchet baseline's state, WITH its properties — not a bare string.

Extracted from `ratchet.py` as part of ⟡ratchet-seams. A state vocabulary is a value
type, distinct from the ratchet that produces it: `gate_census` and
`check_baseline_health` read these states without ratcheting anything.

⚑⚑ THE STRINGS WERE A SUM TYPE NOBODY DECLARED, AND EVERY READER RE-DERIVED ITS
PROPERTIES (operator, 2026-08-22: *"`("ok", "EMPTY", "ABSENT", "UNREAD")` — let's talk
about enum-lifting"*). `baseline_health` returned four bare strings and SIX sites then
asked questions of them by comparison: `state == "ABSENT"` (is it a violation),
`state == "EMPTY"` (is it a strength), `state == "UNREAD"` (is it a reader gap),
`state != "ok"` (does it deserve a mark, in two printers), and a hand-typed roster in a
selftest. A property of the state living in whoever LOOKS at the state is the same defect
in six places, and it produced all three of these:

  · `gate_census.cmd_baselines` counted `!= "ok"` and printed "8 with a DEGRADED
    baseline" — collapsing a vacuous green and the zero-tolerance setting into one
    number, two lines above a legend explaining they are opposites;
  · `check_baseline_health --list` marked all eight EMPTY rows with a flag while its own
    summary called them the strong setting;
  · `gate_census.selftest`'s roster omitted UNREAD entirely, so a genuine UNREAD row
    would have FAILED the suite claiming the state was wrong.

⚑ AND FIXING THE THREE INSTANCES CHANGED NOTHING STRUCTURAL — the generator was still
emitting bare strings, so the next reader re-invents the predicate. That is why this is a
lift and not three edits.

⚑ THE TWO PROPERTIES ARE INDEPENDENT, WHICH IS WHY A BOOLEAN COULD NOT CARRY THEM.
`is_defect` says the GATE cannot be trusted; `deserves_mark` says a READER should look.
UNREAD is `deserves_mark` without `is_defect` (a gap in the parser, not a verdict about
the gate), and EMPTY is neither (the strongest setting). Any single `!= "ok"` flattens
that 2-bit space to 1 bit, and always in the direction that reads strictness as debt.

⚑ THE CASES LIVE IN `baseline_state_selftest.py`, NOT IN THIS FILE'S TAIL
(⟡n-split-the-tails). They were inline until a coverage census counted that as a convention
rather than as debt; operator: *"n-split that crap. No more in-line/tail testing."* Inline
cases cannot run without importing the module under test, and a module too dirty to edit
takes its own suite hostage.
"""

from __future__ import annotations

from typing import ClassVar


class BaselineState:
    """One declared baseline state, carrying the properties readers used to re-derive."""

    __slots__ = ("deserves_mark", "gloss", "is_defect", "name")

    OK: ClassVar[BaselineState]
    EMPTY: ClassVar[BaselineState]
    ABSENT: ClassVar[BaselineState]
    UNREAD: ClassVar[BaselineState]

    def __init__(self, name: str, *, is_defect: bool, deserves_mark: bool, gloss: str) -> None:
        """Declare a state and the two independent properties readers ask of it."""
        self.name = name
        self.is_defect = is_defect
        self.deserves_mark = deserves_mark
        self.gloss = gloss

    # ⚑ IT COMPARES AND RENDERS AS ITS NAME, so every existing `state == "EMPTY"` call
    # site and every `%-7s` keeps working unchanged. The lift is ADDITIVE: a caller that
    # has not migrated is not broken, which is what lets the six sites convert one at a
    # time instead of in one flag-day edit.
    def __eq__(self, other: object) -> bool:
        """Compare by name, so a bare-string call site keeps working."""
        return self.name == (other.name if isinstance(other, BaselineState) else other)

    def __hash__(self) -> int:
        """Hash by name, so a state and its string share a bucket."""
        return hash(self.name)

    # ⚑ ORDERED BY NAME, because a reader sorting a set of states is a normal thing to do
    # and the first cut made it a TypeError — caught by the selftest, which sorted
    # `{r[2] for r in bh}`. A lift that keeps `==` working but breaks `sorted()` has
    # MOVED the breakage rather than removed it: the string it replaced was totally
    # ordered, so the object must be too, or every migrating call site pays for the lift.
    def __lt__(self, other: object) -> bool:
        """Order by name, so a mixed set of states and strings still sorts."""
        return self.name < (other.name if isinstance(other, BaselineState) else str(other))

    def __str__(self) -> str:
        """Render as the bare name, for `%-7s` and every existing format string."""
        return self.name

    def __repr__(self) -> str:
        """Render unambiguously, naming the type."""
        return f"BaselineState({self.name!r})"

    @classmethod
    def all(cls) -> tuple[BaselineState, ...]:
        """Return every declared state.

        ⚑ THE ROSTER AND THE DEFINITION ARE ONE OBJECT, so a selftest asking "is every
        state known" CANNOT omit a member the way the hand-typed `("ok", "EMPTY",
        "ABSENT")` tuple omitted UNREAD — and that omission would have failed a suite on
        a genuine UNREAD row while claiming the STATE was wrong.
        """
        return (cls.OK, cls.EMPTY, cls.ABSENT, cls.UNREAD)

    @classmethod
    def of(cls, name: str) -> BaselineState:
        """Resolve a name to its state, REFUSING an unknown one.

        ⚑ A LOOKUP THAT FELL BACK TO A DEFAULT WOULD RE-CREATE THE BUG: an unrecognised
        state silently reading as `ok` is precisely the false-green this whole surface
        exists to prevent.
        """
        for s in cls.all():
            if s.name == name:
                return s
        known = ", ".join(s.name for s in cls.all())
        msg = f"unknown baseline state {name!r}; known: {known}"
        raise KeyError(msg)


BaselineState.OK = BaselineState(
    "ok",
    is_defect=False,
    deserves_mark=False,
    gloss="a recorded baseline with keys — the ratchet is holding a grandfathered set",
)
BaselineState.EMPTY = BaselineState(
    "EMPTY",
    is_defect=False,
    deserves_mark=False,
    gloss="ZERO-TOLERANCE: the empty set as baseline, so every offender is a NEW key and "
    "NO exception is grandfathered. The STRONGEST setting, never a defect",
)
BaselineState.ABSENT = BaselineState(
    "ABSENT",
    is_defect=True,
    deserves_mark=True,
    gloss="VACUOUS GREEN: no baseline file, so set_ratchet takes the 'record and pass' "
    "branch and the gate exits 0 REGARDLESS of what it measured",
)
BaselineState.UNREAD = BaselineState(
    "UNREAD",
    is_defect=False,
    deserves_mark=True,
    gloss="no baseline literal found at any call site — a fact about the READER, not a "
    "verdict about the gate",
)
