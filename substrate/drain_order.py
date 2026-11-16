# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Order drain candidates by what draining one COSTS, not by what it retires.

⚑⚑⚑ THE RETIRE-COUNT RANKING SELECTS THE HARDEST DRAINS FIRST, and that is not a defect
in the ranking — it is a defect in reading it as a work queue. A name retires many
`sys.path` inserts precisely BECAUSE many files reach it, and every one of those files
must be rewired for the drain to land. Measured on the ranking's second-place candidate:
the ranking calls it fifteen retired inserts, and `module_importers` reports its import
sites spread across dozens of files. Meanwhile a candidate retiring nothing on its own
had one site in one file — invisible to the ranking, and startable immediately.

⚑⚑ THE TWO NUMBERS ANSWER DIFFERENT QUESTIONS AND BOTH ARE RIGHT. Retire-count answers
*what does draining this FINISH*; consumer-count answers *what does it COST*. This module
reports the second so a plan can order by it, and deliberately does not replace the first:
`drain_leverage`'s own header refuses collapsing retired and contested into one score for
the same reason a cost/value collapse would be wrong here.

⚑ EDITABILITY IS PER-FILE AND ASKED OF THE CHECKER, never curated. A consumer carrying
findings cannot take an edit under the zero-tolerance per-file gate, so a drain whose
consumers are all clean is startable TODAY and one with a dirty consumer is blocked behind
that file's own paydown. `promote_frontier` answers this for one directory and returns
basenames; the drain population spans several trees, so the predicate here is the
checker's per-file verdict, which works anywhere.

⚑ AND A BLOCKED CANDIDATE NAMES ITS BLOCKERS, because *"drain this and you must first
clean these"* is a queue while *"blocked"* is a wall. Same discipline as the contested
column it sits beside.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cost:
    """What draining one name would cost, and what stands in the way."""

    name: str
    sites: int
    files: tuple[str, ...]
    dirty: tuple[str, ...]

    @property
    def startable(self) -> bool:
        """Whether every consumer can take an edit today."""
        return not self.dirty


def cost_of(
    name: str,
    consumers: dict[str, int],
    dirty: frozenset[str],
) -> Cost:
    """Return the cost of draining `name` given its consumers and the dirty set.

    `consumers` maps a consumer path to how many import sites it holds. ⚑ SITES AND
    FILES ARE BOTH KEPT: a file importing one name five times is one edit, but five
    sites is a bigger edit than one, and collapsing to either number alone loses a
    distinction a planner uses.
    """
    files = tuple(sorted(consumers))
    return Cost(
        name=name,
        sites=sum(consumers.values()),
        files=files,
        dirty=tuple(f for f in files if f in dirty),
    )


def _tractability(cost: Cost) -> tuple[bool, int, int, str]:
    """Return the sort key: startable first, then fewest files, then fewest sites.

    ⚑ THE KEY IS COST AND THE TIE-BREAK IS NAME, with retire-count deliberately absent.
    A plan that sorted by value here would reproduce the ordering this module exists to
    invert; a caller wanting value reads `drain_leverage`, and the two are meant to be
    read together rather than merged.
    """
    return (not cost.startable, len(cost.files), cost.sites, cost.name)


def ordered(costs: list[Cost]) -> list[Cost]:
    """Order candidates by tractability."""
    return sorted(costs, key=_tractability)


def render(costs: list[Cost], limit: int) -> str:
    """Render the cost ordering, startable candidates first."""
    rows = ordered(costs)
    ready = [c for c in rows if c.startable]
    head = (
        f"{len(rows)} candidate(s), {len(ready)} startable "
        f"(every consumer clean enough to take an edit)"
    )
    out = [head]
    for c in rows[:limit]:
        mark = "✓" if c.startable else " "
        out.append(f"  {mark} {c.name:<28} {len(c.files):>3} file(s)  {c.sites:>3} site(s)")
        if c.dirty:
            out.append(f"      blocked by: {', '.join(c.dirty)}")
    out.append(
        "   ⚑ ORDERED BY COST, NOT VALUE. What draining a name RETIRES is "
        "`drain_leverage`'s question; the two are read together, never summed."
    )
    return "\n".join(out)
