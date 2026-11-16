# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report which finding-key ordinals are taken, so a filer stops reusing one.

⚑⚑⚑ THREE INDEPENDENT AGENTS HAVE NOW MADE THE SAME MISTAKE AND TWO FILED A FINDING ABOUT
IT WITHOUT PRODUCING A MECHANISM. The ledger's keys are `<family>-<letter><ordinal>-<slug>`,
and the registration path refuses only an EXACT duplicate — so two findings sharing an
ordinal but differing in slug both register cleanly. The result is a family where one
ordinal names four different findings, and the ordinal no longer identifies or sorts.

⚑⚑ THE FAILURE IS THE SAME EVERY TIME: an agent reads the roster, computes the maximum
ordinal it can see, and files at max-plus-one — with no exclusion against a concurrent or
subsequent filer doing the same from the same snapshot. That is a read-modify-write with no
compare-and-swap, and naming it in prose has not stopped it recurring.

⚑ SO THIS REPORTS THE TAKEN SET RATHER THAN SUGGESTING A NEXT NUMBER. A suggestion is a
value that goes stale between the read and the write, which is the defect itself one layer
on. What a filer needs is the ability to ask whether the ordinal they are about to use is
free, and to see the collisions that already exist — the first is checkable at filing time,
the second is a paydown census.

⚑ AND THE KEYS ARE READ AS TEXT, NOT IMPORTED. The ledger module carries hundreds of its
own findings and cannot take an edit, so a reader that imported it would inherit that
freeze; and the question here is about key SPELLING, which the source text answers directly.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / ".claude" / "agents" / "findings.py"

# A witness key as the roster spells it: family, an optional letter-and-ordinal, a slug.
_KEY = re.compile(r'^\s*"([a-z]+)-([A-Z])(\d+)(?:-([a-z0-9-]+))?"\s*:', re.MULTILINE)


@dataclass(frozen=True, slots=True)
class Ordinal:
    """One family-and-number, and every slug filed under it."""

    family: str
    letter: str
    number: int
    slugs: tuple[str, ...]

    @property
    def collided(self) -> bool:
        """Whether more than one finding shares this ordinal."""
        return len(self.slugs) > 1

    @property
    def label(self) -> str:
        """The ordinal as a filer would type it."""
        return f"{self.family}-{self.letter}{self.number}"


def _position(item: Ordinal) -> tuple[str, str, int]:
    """Return the sort key: family, then letter, then number."""
    return (item.family, item.letter, item.number)


def _weight(item: Ordinal) -> tuple[int, str]:
    """Return the collision sort key: most-collided first, then label."""
    return (-len(item.slugs), item.label)


def ordinals(ledger: Path | None = None) -> list[Ordinal]:
    """Return every ordinal in the ledger, with the slugs filed under it.

    ⚑ AN UNSLUGGED KEY IS STILL AN OCCUPANT. A bare `family-O12` holds its ordinal exactly
    as a slugged one does, so it is carried with an empty slug rather than skipped — a
    reader that dropped it would report a taken ordinal as free.
    """
    path = LEDGER if ledger is None else ledger
    text = path.read_text(encoding="utf-8", errors="replace")
    seen: dict[tuple[str, str, int], list[str]] = {}
    for match in _KEY.finditer(text):
        family, letter, number, slug = match.groups()
        seen.setdefault((family, letter, int(number)), []).append(slug or "")
    rows = [Ordinal(family, letter, number, tuple(sorted(slugs)))
            for (family, letter, number), slugs in seen.items()]
    return sorted(rows, key=_position)


def taken(family: str, letter: str, ledger: Path | None = None) -> set[int]:
    """Return the ordinals already used in one family-and-letter series."""
    return {o.number for o in ordinals(ledger)
            if o.family == family and o.letter == letter}


def collisions(ledger: Path | None = None) -> list[Ordinal]:
    """Return every ordinal naming more than one finding."""
    return [o for o in ordinals(ledger) if o.collided]


def render(ledger: Path | None = None) -> str:
    """Render the collision census, most-collided first."""
    rows = collisions(ledger)
    total = len(ordinals(ledger))
    out = [f"{len(rows)} collided ordinal(s) over {total} in the ledger"]
    for row in sorted(rows, key=_weight):
        out.append(f"  {row.label:<12} {len(row.slugs)} findings")
        out.extend(f"      {slug or '(no slug)'}" for slug in row.slugs)
    out.append("   ⚑ AN ORDINAL IS NOT AN IDENTIFIER ONCE IT COLLIDES. The full key stays "
               "unique, so nothing was overwritten — but the number no longer sorts or "
               "names, and a filer reading max-plus-one keeps reusing one.")
    out.append("   ⚑ NO NEXT NUMBER IS SUGGESTED. A suggestion goes stale between the read "
               "and the write, which is the read-modify-write defect one layer on.")
    return "\n".join(out)
