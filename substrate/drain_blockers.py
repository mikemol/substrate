# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Rank the files that block drains, by how many drains each one gates.

⚑⚑⚑ THE QUEUE'S DUAL, AND THE MEASUREMENT SAYS IT IS THE MORE ACTIONABLE HALF. The
cost-ordered queue reports one-file one-site drains at its head, every one blocked by a
single dirty consumer — and THE BLOCKERS REPEAT. So the population is not many independent
walls but a small set of files gating many cheap drains, and cleaning one unblocks several
at once. A plan that walks the queue top-down pays for each drain separately; a plan that
walks THIS list pays once and collects several.

⚑⚑ AND IT INVERTS BOTH OTHER ORDERINGS. `drain_leverage` ranks by what draining a name
RETIRES and selects the hardest work; `drain_order` ranks by what draining a name COSTS and
selects what could begin. This ranks by what CLEANING A FILE UNBLOCKS, which is the only one
of the three that names an action available when the startable count is zero.

⚑⚑⚑ BUT THE HEAD OF THIS RANKING IS MONOLITHS BY CONSTRUCTION, AND THE FIRST CUT DID NOT
SAY SO. Measured: the top-ranked blocker carried hundreds of its own findings, as did the
third — both refused outright by the per-file gate, each gating a drain that is one import
line. The correlation is structural: a file becomes a BLOCKER by importing several bare
names, and accumulates several bare imports by being large and doing many things, which is
the same property that gives it a large untyped surface. So a ranking by drains-unblocked
alone keeps nominating files that cannot take an edit, and the reader discovers it one call
later. Each row now carries the blocker's own finding count so an unactionable row says so.

⚑ A BLOCKER'S WEIGHT IS DRAINS GATED, NOT SITES. A file holding twenty import sites of one
name blocks one drain; a file holding one site each of five names blocks five. Weighing by
sites would rank the first above the second and send an operator to the file whose paydown
frees the least.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from substrate.drain_order import Cost


@dataclass(frozen=True, slots=True)
class Blocker:
    """One dirty file, and the drains its own paydown would release.

    ⚑ ONLY DRAINS THIS FILE BLOCKS ALONE ARE CARRIED. A drain with two dirty consumers is
    not released by cleaning either one, so counting it toward both would promise a payoff
    neither delivers. Only a sole blocker converts a paydown into an unblocked drain.

    ⚑⚑ `own` IS THE BLOCKER'S OWN FINDING COUNT, and `None` means it was not measured
    rather than that it is clean. A reader that defaulted an unmeasured file to zero would
    report every blocker as actionable, which is the false green this column exists to
    prevent.
    """

    path: str
    gates: tuple[str, ...]
    own: int | None = None

    @property
    def actionable(self) -> bool:
        """Whether this file can itself take an edit today.

        ⚑ AN UNMEASURED BLOCKER IS NOT ACTIONABLE. Unknown and clean are different, and
        collapsing them would put a monolith at the head of a plan.
        """
        return self.own == 0


def _weight(blocker: Blocker) -> tuple[bool, int, str]:
    """Return the sort key: actionable first, then most drains unblocked, then path.

    ⚑ ACTIONABILITY LEADS THE KEY, because a row that cannot be acted on is not a plan
    however many drains it gates. The gated count still orders within each group, so the
    unactionable rows remain readable as the paydown they represent.
    """
    return (not blocker.actionable, -len(blocker.gates), blocker.path)


def blockers(costs: list[Cost], own: dict[str, int] | None = None) -> list[Blocker]:
    """Return each file that solely blocks at least one drain, most actionable first.

    `own` maps a blocker path to its own finding count; a path absent from it is reported
    as unmeasured. ⚑ A DRAIN WAITING ON SEVERAL DIRTY FILES CONTRIBUTES TO NONE OF THEM.
    That is deliberately pessimistic: it reports what a single paydown DEFINITELY releases
    rather than what it might, so a caller acting on this list cannot be disappointed by a
    drain that stayed blocked.
    """
    counts = own or {}
    sole: dict[str, list[str]] = {}
    for cost in costs:
        if len(cost.dirty) == 1:
            sole.setdefault(cost.dirty[0], []).append(cost.name)
    rows = [Blocker(path, tuple(sorted(names)), counts.get(path)) for path, names in sole.items()]
    return sorted(rows, key=_weight)


def multiply_blocked(costs: list[Cost]) -> list[Cost]:
    """Return the drains waiting on more than one dirty file.

    ⚑ REPORTED SEPARATELY BECAUSE THEY ARE INVISIBLE TO THE RANKING ABOVE. A drain with
    three dirty consumers appears under no blocker, so a reader seeing only the ranking
    would conclude those consumers gate nothing. They gate this drain jointly, and it is
    released only when all of them are clean.
    """
    return [c for c in costs if len(c.dirty) > 1]


def _own_column(blocker: Blocker) -> str:
    """Render the blocker's own finding count, distinguishing unmeasured from clean."""
    if blocker.own is None:
        return "own ?"
    return f"own {blocker.own}"


def render(costs: list[Cost], limit: int, own: dict[str, int] | None = None) -> str:
    """Render the blocker ranking, actionable rows first."""
    rows = blockers(costs, own)
    joint = multiply_blocked(costs)
    ready = [b for b in rows if b.actionable]
    head = (
        f"{len(rows)} file(s) solely block at least one drain, {len(ready)} of them editable today"
    )
    out = [head]
    for b in rows[:limit]:
        mark = "✓" if b.actionable else " "
        out.append(f"  {mark} {b.path:<44} unblocks {len(b.gates):>3}  {_own_column(b)}")
        out.append(f"      {', '.join(b.gates)}")
    if joint:
        out.append(
            f"   ⚑ {len(joint)} drain(s) wait on SEVERAL dirty files and appear "
            f"under no blocker above — cleaning any one releases none of them."
        )
    out.append(
        "   ⚑ RANKED BY DRAINS UNBLOCKED, NOT BY SITES. A file holding many sites "
        "of one name blocks one drain."
    )
    out.append(
        "   ⚑ `own ?` MEANS UNMEASURED, NOT CLEAN. A blocker carrying its own "
        "findings cannot take an edit, whatever it gates."
    )
    return "\n".join(out)
