#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report leverage classes whose members differ by an order of magnitude in discovered size.

⚑⚑⚑ THE RANK SAYS *EQUAL* AND THE MEASUREMENT SAYS OTHERWISE. Declared leverage counts open items
in the WARRANT closure, so a provider cone spanning thousands of modules adds nothing to it; and a
single scalar per key means a route split is gone before anything sorts. Two items can therefore
sit at the same rank while what was DISCOVERED about them differs by orders of magnitude — the
rank is uninformed by the measurement, and nothing about the table says so.

⚑⚑ MEASURED AS A DISAGREEMENT, NEVER AS A CODE SHAPE. A census asking *"does the ranking mention a
cone"* verifies presence, which this arc has paid for repeatedly. This asks whether two items with
the SAME declared leverage carry DIFFERENT discovered sizes — the condition that makes the rank
wrong, stated as a property of the numbers rather than of the code that produced them.

⚑⚑ AND THE SIZES ARE AN ARGUMENT, WHICH IS THE WHOLE REASON THE ORIGIN COMPUTED ITS OWN. Reading
a shared memo made the answer depend on CALL ORDER: the memo held only items that had already run,
so this witness saw 1 of 20 sizes when it fired first, emitted an *"ask me differently"* verdict,
and the ordering read that as a citation and ranked the highest-leverage item BLOCKED. **A figure
whose denominator moves with its position in the sweep is not measuring the tree.** Taking the
population as an input makes the answer the same whether it runs first, last, or alone.

⚑ THE THRESHOLD IS A DECLARED CONSTANT. An order of magnitude is a judgement about when a shared
rank becomes misleading, and burying it in a comparison would make it unreadable to anyone asking
what the item actually claims.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

# How far two members of one leverage class may differ before the rank is uninformative.
SPAN = 10


def _largest_first(member: tuple[str, int]) -> tuple[int, str]:
    """Order members by descending size, breaking ties by key.

    ⚑ A NAMED FUNCTION, NOT A KEY LAMBDA. An inline `key=lambda row: (-row[1], row[0])` infers
    `Callable[[Any], tuple[Any, Any]]` under the strict bar and carries that `Any` into the
    result — the same untyped-lambda defect the rung ordering hit.
    """
    key, size = member
    return -size, key


@dataclass(frozen=True, slots=True)
class Klass:
    """One leverage class and the discovered sizes inside it."""

    leverage: int
    # (key, discovered size), largest first.
    members: tuple[tuple[str, int], ...]

    @property
    def low(self) -> int:
        """Return the smallest discovered size in the class."""
        return min(size for _key, size in self.members)

    @property
    def high(self) -> int:
        """Return the largest discovered size in the class."""
        return max(size for _key, size in self.members)

    @property
    def blind(self) -> bool:
        """Report whether the class hides an order-of-magnitude difference.

        ⚑ A SINGLETON CLASS CANNOT DISAGREE WITH ITSELF. One member means the rank has nothing to
        be wrong about, so it is not a finding — and counting it would report every unique
        leverage value as debt.
        """
        return len(self.members) > 1 and self.high >= SPAN * max(self.low, 1)


def classes(leverage: dict[str, int], sizes: dict[str, int]) -> tuple[Klass, ...]:
    """Group items by declared leverage, carrying their discovered sizes.

    ⚑ ZERO-SIZE ITEMS ARE EXCLUDED, NOT COUNTED AS SMALL. An item with nothing discovered has not
    been measured against its rank at all; folding it in as `0` would make every class it joins
    look like it spans infinitely.
    """
    grouped: dict[int, list[tuple[str, int]]] = {}
    for key, size in sizes.items():
        if size:
            grouped.setdefault(leverage.get(key, 0), []).append((key, size))
    return tuple(
        Klass(leverage=lev, members=tuple(sorted(members, key=_largest_first)))
        for lev, members in sorted(grouped.items())
    )


def blind(rows: tuple[Klass, ...]) -> tuple[Klass, ...]:
    """Return the leverage classes whose rank is uninformed by the measurement."""
    return tuple(row for row in rows if row.blind)


def render(rows: tuple[Klass, ...]) -> str:
    """Render the census, naming what an empty population means."""
    if not rows:
        return "  no item carries a discovered size — UNMEASURED, not clean"

    found = blind(rows)
    if not found:
        return (
            f"  no leverage class hides a {SPAN}x difference in discovered size "
            f"({len(rows)} class(es))"
        )

    out = [f"  {len(found)} of {len(rows)} leverage class(es) span {SPAN}x or more:"]
    for row in found:
        listed = ", ".join(f"{key}={size}" for key, size in row.members)
        out.append(f"    ⚑ lev {row.leverage}: {listed}")
    return "\n".join(out)


if __name__ == "__main__":
    # ⚑ A DEMONSTRATION, NOT THE LIVE CENSUS. The real populations come from the bib walk and the
    # size computation; this shows the shape without pretending to measure the tree.
    _example = classes({"a": 1, "b": 1, "c": 2}, {"a": 218, "b": 12, "c": 4})
    sys.stdout.write(render(_example) + "\n")
    sys.exit(0)
