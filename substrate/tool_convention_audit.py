#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Measure the DECLARED conventions against the live census — the two ways a record rots.

⚑⚑⚑ A DECLARATION THAT NOTHING CHECKS IS WHAT `farm.py`'s `Arm` REFUSES. An F-arm is evidence
only because it declares the message its mutation must provoke and reports VACUOUS when the red
comes from elsewhere. A `Convention` claims a flag's meaning is SHARED, so the claim must be
measured against what tools actually accept — and it can rot two ways, neither inferable from the
record alone:

    STALE   declared, and NO tool accepts it → the convention outlived its flag
    SOLO    declared, and ONE tool accepts it → not shared; a per-tool mode wearing a contract's
            clothes

⚑⚑ A REQUIRED PAIR IS A CONTRACT THE CENSUS CAN MEASURE, and measuring it is what keeps
`contract` from being prose. `--apply`/`--dry-run` are declared MUTUALLY EXCLUSIVE AND REQUIRED —
no default in either direction — because a default is silent in BOTH failure modes: a default-dry
tool does nothing when the caller meant to write, a default-apply tool writes when the caller
meant to look. A tool accepting ONE side still defaults on the other, so it is HALF-PAIRED.

⚑⚑ AND THE TENANT PAIR HAS NO SECOND FLAG, WHICH *IS* THE FINDING. There is no explicit live
selector, so the absence of `--sandbox` means "live" silently — and "forgot to care" becomes
indistinguishable from "chose". The missing half is what a report must name; treating the pair as
complete would hide it.

⚑ THE OTHER DIRECTION IS THE ONE THAT FINDS WORK: a flag many tools accept and NO record explains.
That is either an undeclared convention (declare it) or real divergence (converge it), and the
census CANNOT TELL WHICH — which is the whole reason a human writes the `why`.

⚑⚑ AND THE PAIR FLAGS ARE DERIVED FROM THE RECORDS, NOT RETYPED. The origin's own comment says
they are *"read from `CONVENTIONS`, never retyped — hardcoding the two words here would put the
contract in two places"* — and the line immediately below it retypes them. A second spelling of
one contract is exactly what the record type exists to prevent, so this reads the `mutually
exclusive` declaration out of the contracts themselves. → ⟡pair-flags-derived

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers). This module MEASURES; rendering is
the caller's.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import tool_convention

if TYPE_CHECKING:
    from substrate.tool_census import Tool

# How a declared convention can read against the live census.
SHARED = "SHARED"
SOLO = "SOLO"
STALE = "STALE"

# Fewest tools that make an undeclared flag a RECURRENCE worth a decide-or-converge call.
RECURRENCE = 3

# The phrase a contract uses to declare its other half. ⚑ READ, NOT RETYPED — see the module note.
PAIR_MARK = "MUTUALLY EXCLUSIVE WITH"

# ⚑⚑ SLOTTED DATACLASSES, NOT `NamedTuple` (⟡symbolic-reference-only). A `NamedTuple` subclasses
# `tuple`, so `a, b = record` and `record[0]` both work — numeric access to a thing that HAS
# NAMES. A slotted dataclass carries neither `tp_iter` nor the sequence protocol, so a positional
# site becomes a static error naming its own line rather than a convention to remember.


@dataclass(frozen=True, slots=True)
class Standing:
    """One declared convention, measured against what tools accept."""

    convention: tool_convention.Convention
    accepted_by: tuple[str, ...]

    @property
    def verdict(self) -> str:
        """Return SHARED, SOLO or STALE."""
        if not self.accepted_by:
            return STALE
        return SOLO if len(self.accepted_by) == 1 else SHARED

    @property
    def holds(self) -> bool:
        """Report whether the claim that this flag's meaning is shared still stands."""
        return self.verdict == SHARED


@dataclass(frozen=True, slots=True)
class Pair:
    """A required-pair contract, and how many tools honour only one side of it."""

    kind: str
    left: str
    right: str | None
    both: tuple[str, ...]
    only_left: tuple[str, ...]
    only_right: tuple[str, ...]

    @property
    def half_paired(self) -> int:
        """Return how many tools still carry a silent default on the other side."""
        return len(self.only_left) + len(self.only_right)

    @property
    def incomplete(self) -> bool:
        """Report whether the pair's other half does not exist as a flag at all.

        ⚑ THE ABSENT HALF IS THE FINDING, not a gap in this reader. With no explicit live
        selector, `--sandbox`'s absence is a DEFAULT rather than a choice.
        """
        return self.right is None


def _accepts(rows: tuple[Tool, ...]) -> dict[str, tuple[str, ...]]:
    """Return `{flag: tools that accept or declare it}` over the census."""
    out: dict[str, list[str]] = {}
    for tool in rows:
        for flag in tool.accepted | set(tool.modes):
            out.setdefault(flag, []).append(tool.relpath)
    return {flag: tuple(sorted(tools)) for flag, tools in out.items()}


def pair_flags() -> tuple[str, ...]:
    """Return the flags a declared contract names as mutually exclusive with another.

    ⚑⚑ DERIVED FROM THE RECORDS, WHICH IS WHAT THE ORIGIN'S OWN COMMENT ASKED FOR AND THE LINE
    BELOW IT DID NOT DO. Retyping the two spellings puts one contract in two places, so a
    convention added tomorrow — or a flag renamed — silently stops being measured while both
    copies still look right.
    """
    return tuple(c.flag for c in tool_convention.CONVENTIONS if PAIR_MARK in c.contract)


def standing(rows: tuple[Tool, ...]) -> tuple[Standing, ...]:
    """Return each declared convention measured against the census."""
    accepts = _accepts(rows)
    return tuple(
        Standing(convention=c, accepted_by=accepts.get(c.flag, ()))
        for c in tool_convention.CONVENTIONS
    )


def _mutation_pair(accepts: dict[str, tuple[str, ...]]) -> Pair | None:
    """Return the mutually-exclusive mutation pair, or None when fewer than two are declared.

    ⚑⚑ THE TWO SIDES ARE UNPACKED BY NAME, NOT BY INDEX (⟡symbolic-reference-only). This read
    `mutation[0], mutation[1]` — numeric subscripts deciding WHICH FLAG IS WHICH, so a contract
    reordered in `CONVENTIONS` would silently swap `only_left` and `only_right` and the report
    would name the wrong half as defaulting. The pair is destructured once, here, with names.
    """
    declared = pair_flags()
    if len(declared) < RECURRENCE - 1:
        return None
    left, right = declared[:2]
    has_left, has_right = set(accepts.get(left, ())), set(accepts.get(right, ()))
    return Pair(
        kind="mutation",
        left=left,
        right=right,
        both=tuple(sorted(has_left & has_right)),
        only_left=tuple(sorted(has_left - has_right)),
        only_right=tuple(sorted(has_right - has_left)),
    )


def _tenant_pair(accepts: dict[str, tuple[str, ...]]) -> Pair | None:
    """Return the tenant pair, whose other half does not exist as a flag."""
    tenant = tool_convention.by_flag("--sandbox")
    if tenant is None:
        return None
    has = set(accepts.get(tenant.flag, ()))
    return Pair(
        kind="tenant",
        left=tenant.flag,
        right=None,
        both=(),
        only_left=tuple(sorted(has)),
        only_right=(),
    )


def required_pairs(rows: tuple[Tool, ...]) -> tuple[Pair, ...]:
    """Return each required-pair contract with the tools that honour only one side.

    ⚑ THE PAIRS ARE READ FROM THE CONTRACTS. `pair_flags` returns the flags whose contract
    declares a mutually-exclusive partner, and the mutation pair is exactly those two; the tenant
    pair is declared with no partner, which is why it is carried with `right=None` rather than
    dropped.
    """
    accepts = _accepts(rows)
    found = (_mutation_pair(accepts), _tenant_pair(accepts))
    return tuple(pair for pair in found if pair is not None)


def undeclared_recurrences(rows: tuple[Tool, ...]) -> dict[str, tuple[str, ...]]:
    """Return flags several tools accept that no convention explains.

    ⚑ EITHER AN UNDECLARED CONVENTION OR REAL DIVERGENCE, AND THE CENSUS CANNOT TELL WHICH. That
    is not a limitation to fix: it is why a human writes the `why`, and why this arm reports a
    DECIDE rather than a defect.
    """
    return {
        flag: tools
        for flag, tools in sorted(_accepts(rows).items())
        if len(tools) >= RECURRENCE and flag not in tool_convention.HARNESS_CONTRACTS
    }
