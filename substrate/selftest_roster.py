#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read the DECLARED selftest roster against what discovery FOUND.

⚑⚑⚑ THE THIRD AND LAST PROMOTION UNIT (gate-G80), completing the five capabilities that
blocked the bare-import repoint. `selftest_decl` carried the declaration and the static cycle
read; `mode_dispatch` carried the branch locator and the contract check; this carries the
roster comparison. With it landed, every name `procstruct` and `check_mode_contracts` import
from the origin exists in the package.

⚑⚑ THIS IS THE READER THE RUNNER COULD NOT HAVE, AND ITS ABSENCE ADMITTED THE FORK BOMB.
Discovery answers *is this file in the roster*; it cannot answer *should it be*. So a member
that invokes the roster is indistinguishable from any other member — membership by convention,
with nowhere to state an intent that contradicts it. Declared state and discovered membership
are two independent readings, and **every disagreement between them is a finding**.

⚑⚑⚑ AND `undeclared` IS REPORTED, NOT OMITTED. A row-set listing only disagreements cannot
distinguish *every tool is declared and consistent* from *nothing is declared yet* — a false
ZERO gets banked while a false positive gets investigated, so the paydown population has to be
visible. That is the same third-outcome discipline `mode_dispatch` keeps for an unlocatable
branch, arriving one layer up.

⚑ THE ROW CONSTRUCTORS ARE NAMED RATHER THAN POSITIONAL, which the gate asked for and which is
right: `Row(tool, state, False, why)` puts a bare boolean in the third slot, and a reader at
the call site cannot tell a verdict from a flag. `_agrees` / `_disagrees` / `_undeclared_row`
say what they mean.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from substrate.selftest_decl import Selftest

# The state a row carries when nobody has declared the tool at all.
UNDECLARED = "undeclared"


@dataclass(frozen=True, slots=True)
class Row:
    """One tool's declared state weighed against whether discovery reached it."""

    tool: str
    state: str
    ok: bool | None
    why: str

    @property
    def undeclared(self) -> bool:
        """Whether this row is the census's own boundary rather than a defect."""
        return self.state == UNDECLARED


def _agrees(tool: str, state: str) -> Row:
    """Build the row for a declaration the tree agrees with."""
    return Row(tool=tool, state=state, ok=True, why="")


def _disagrees(tool: str, state: str, why: str) -> Row:
    """Build the row for a declaration the tree contradicts."""
    return Row(tool=tool, state=state, ok=False, why=why)


def _undeclared_row(tool: str, *, discovered: bool) -> Row:
    """Build the row for a tool with no declaration at all.

    ⚑ NOT A FAILURE, AND `ok is None` SAYS SO. An undeclared tool is the census reporting
    what it has not been told, which is a different fact from a declaration that disagrees
    with the tree.
    """
    why = (
        "in the discovered roster with no Selftest declaration"
        if discovered
        else "declared nowhere and not discovered"
    )
    return Row(tool=tool, state=UNDECLARED, ok=None, why=why)


def _mismatch(tool: str, decl: Selftest, *, discovered: bool) -> Row | None:
    """Return the row when a declaration and the tree disagree, else None."""
    if decl.state == "suite" and not discovered:
        return _disagrees(
            tool,
            decl.state,
            "DECLARED a suite, but discovery cannot reach it — no `--selftest` "
            "dispatch the runner recognises, or the file is unreadable",
        )
    if decl.state == "none" and discovered:
        return _disagrees(
            tool,
            decl.state,
            "DECLARED state='none', but discovery found a suite and the runner "
            "is invoking it — the declaration and the tree disagree",
        )
    if decl.state == "fixture" and discovered:
        # ⚑ A FIXTURE IS MEANT TO FAIL, so its presence in the roster makes the gate red by
        #   design. It is invoked BY the runner's own suite as a positive control, never AS
        #   a member of the roster.
        return _disagrees(
            tool,
            decl.state,
            "a FIXTURE is in the roster — it is MEANT to fail, so the gate is "
            "red by design. A fixture is invoked BY the runner's own suite as "
            "a positive control, never AS a member of the roster",
        )
    return None


def rows(declared: Mapping[str, Selftest], discovered: Iterable[str]) -> list[Row]:
    """Return one row per tool across the UNION of the declared and discovered sets.

    ⚑ THE UNION, NEVER ONE SIDE. Walking only the declarations misses a discovered tool
    nobody declared; walking only discovery misses a declaration the runner cannot reach.
    Both are findings and each is invisible from the other side.
    """
    found = set(discovered)
    out: list[Row] = []
    for tool in sorted(set(declared) | found):
        decl = declared.get(tool)
        if decl is None:
            out.append(_undeclared_row(tool, discovered=tool in found))
            continue
        ok, why = decl.contract()
        if not ok:
            out.append(_disagrees(tool, decl.state, why))
            continue
        clash = _mismatch(tool, decl, discovered=tool in found)
        out.append(clash if clash is not None else _agrees(tool, decl.state))
    return out


def failing(found: Iterable[Row]) -> tuple[Row, ...]:
    """Return the rows that are genuine disagreements — never the undeclared ones."""
    return tuple(row for row in found if row.ok is False)


def unmeasured(found: Iterable[Row]) -> tuple[Row, ...]:
    """Return the rows the census has not been told about.

    ⚑ SEPARATE FROM THE FAILURES, because an undeclared tool is a gap in the DECLARATION
    and a disagreement is a gap in the TREE. Summing them would let the paydown population
    inflate the defect count, and hiding them would let an all-undeclared roster read clean.
    """
    return tuple(row for row in found if row.undeclared)
