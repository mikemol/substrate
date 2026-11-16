#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report which files REIMPLEMENT a shared capability rather than delegating to its home.

⚑⚑⚑ A SHARED NAME IS NOT A SHARED AUTHORITY. Four bodies once sat under `agda_files`, two of them
feeding pre-commit gates, disagreeing silently. That is the defect this reads for.

⚑⚑ AND THE CONVERSE IS WHAT THE FIRST PREDICATE GOT WRONG: A DUPLICATED NAME IS NOT A DUPLICATED
BODY. It searched for a `def` of that name at the start of a line — a count of `def` SITES, i.e.
of SHAPE. Measured: every surviving definition beyond the home is a ONE-LINE WRAPPER delegating
to the authority, differing only in which root it binds. The divergence had already been paid
down and **the census was counting its own repair** — so the item could never read as done no
matter how much converging happened. A shape predicate cannot distinguish the defect from its fix.

⚑⚑ WORSE, THE COUNT MOVES THE WRONG WAY. Consolidation ADDS a delegator per site, so a def count
goes UP as the repair lands — which is how `4 → 5` was once read as the incident getting worse
when it was the incident being closed. **The verdict must come from the BODIES, never the names.**

⚑ THE HOME IS EXEMPT BY CONSTRUCTION. The authority necessarily reimplements the capability — it
IS the implementation — so counting it would leave the item permanently one short of closed, a
floor no amount of correct work could reach.

⚑⚑ AND THE EXEMPTION IS COMPARED ON NORMALISED PATHS, WHICH THE FIRST CUT DID NOT DO. The census
yields ABSOLUTE paths; the home was passed repo-relative, so the string compare never matched and
the authority reported ITSELF as debt — an item that cannot close, produced by the exemption
written to let it close. Both sides are made repo-relative before comparing, and the rows are
reported that way too.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Protocol, cast

from substrate import corpus, scratch_module

# The tool that owns the reimplements/delegates distinction.
CENSUS = "pycodemod"

# The verdict naming a body that re-derives the capability instead of calling it.
REIMPLEMENTS = "REIMPLEMENTS"


class Census(Protocol):
    """The part of the codemod tool this reader consults."""

    def rivals(self, name: str) -> list[tuple[str, int, str, str, int]]:
        """Return `(path, line, verdict, callee, statements)` per definition."""
        ...


def relative(path: str) -> str:
    """Return a path as repo-relative, whatever spelling it arrived in.

    ⚑ ONE NORMALISER, USED ON BOTH SIDES. Two spellings of one path is how an exemption silently
    stops exempting — measured here, and measured before in the collision census where an
    absolute label made every cross-tree bucket read empty.
    """
    root = f"{corpus.ROOT}/"
    return path.removeprefix(root)


@dataclass(frozen=True, slots=True)
class Rival:
    """One definition of a shared name, and what it does."""

    path: str
    line: int
    verdict: str
    # What a delegator calls; empty for a reimplementation.
    callee: str
    statements: int

    @property
    def reimplements(self) -> bool:
        """Report whether this body re-derives the capability."""
        return self.verdict == REIMPLEMENTS


@dataclass(frozen=True, slots=True)
class Authority:
    """The rival definitions of one capability, or why they could not be read."""

    capability: str
    rivals: tuple[Rival, ...]
    # The home, excluded from the debt — it IS the implementation.
    home: str
    why: str

    @property
    def known(self) -> bool:
        """Report whether the census was actually read."""
        return not self.why

    @property
    def debt(self) -> tuple[Rival, ...]:
        """Return the reimplementations that are not the home."""
        home = relative(self.home)
        return tuple(row for row in self.rivals if row.reimplements and row.path != home)

    @property
    def sole(self) -> bool:
        """Report whether the home is the only implementation."""
        return self.known and not self.debt


def census() -> tuple[Census | None, str]:
    """Load the tool that owns the rivals census."""
    found, why = scratch_module.scratch_module(CENSUS)
    if found is None:
        return None, f"{CENSUS} will not load: {why}"
    return cast("Census", found), ""


def authority(capability: str, home: str) -> Authority:
    """Read every definition of a capability and say whether the home is sole.

    ⚑ THE HOME IS NAMED BY THE CALLER, NOT GUESSED. Inferring it from the census — say, as the
    only reimplementation — would make the verdict circular: any single remaining rival would be
    read as the authority and the item would close on exactly the state it exists to find.
    """
    api, missing = census()
    if api is None:
        return Authority(capability=capability, rivals=(), home=home, why=missing)

    rows = tuple(
        Rival(path=relative(path), line=line, verdict=verdict, callee=callee, statements=count)
        for path, line, verdict, callee, count in api.rivals(capability)
    )
    if not rows:
        return Authority(
            capability=capability,
            rivals=(),
            home=home,
            why=f"no definition of {capability} found — UNMEASURED, not sole",
        )
    return Authority(capability=capability, rivals=rows, home=home, why="")


def render(got: Authority) -> str:
    """Render the verdict, keeping unmeasured distinct from sole."""
    if not got.known:
        return f"  UNMEASURED — {got.why}"

    delegating = sum(1 for row in got.rivals if not row.reimplements)
    if got.sole:
        return (
            f"  {relative(got.home)} is the sole implementation of {got.capability} "
            f"({delegating} delegator(s))"
        )

    out = [f"  {len(got.debt)} file(s) reimplement {got.capability} instead of delegating:"]
    out.extend(f"    ⚑ {row.path}:{row.line}  {row.statements} statement(s)" for row in got.debt)
    return "\n".join(out)


if __name__ == "__main__":
    _got = authority("agda_files", "scratch/agda_lex.py")
    sys.stdout.write(render(_got) + "\n")
    sys.exit(0)
