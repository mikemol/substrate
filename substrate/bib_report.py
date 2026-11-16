# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""How every read mode reports: rows, then `n of m` — the denominator, never a bare count.

⚑⚑⚑ THE DENOMINATOR IS THE WHOLE POINT, AND THE ORIGIN STATES IT TWICE IN ITS OWN COMMENTS. A bare
`0 losses` cannot distinguish a TOTAL read from a probe that examined nothing; `roundtrip`'s arm
says so outright — *"report the denominator the probe covered, not just the failures… the same
reason every other mode prints `n of m`."* An empty result is a fact about the METHOD until the
population it ran over is printed beside it.

⚑⚑ SO A ZERO HERE IS TWO DIFFERENT CLAIMS AND ONLY THE DENOMINATOR SEPARATES THEM. `0 of 84` says
the probe covered 84 entries and found nothing. `0 of 0` says the probe found nothing because it
read nothing — a fact about the invocation, which reads identically without the second number and
gets banked as a clean bill of health. That is the census-green-is-a-fact-about-the-census defect,
and this module exists so no read mode can commit it by forgetting a print.

⚑ PLURALISATION IS HERE FOR ONE REASON: THE ORIGIN SPELLED IT SIX TIMES. Six copies of
`"y" if len(have) == 1 else "ies"`, and the `--mentions` arm's copy tests `len(have) == 2` because
its denominator excludes the entry itself. Six chances to get an off-by-one wrong, in code whose
only job is to make a number legible.

⚑ EXTRACTED, NOT EDITED IN PLACE. `scratch/bibstruct.py` carries enough findings that the per-file
gate refuses every write to it, so this is rebuilt whole and the origin is left alone until it can
be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

from dataclasses import dataclass

# The width the origin aligns keys to in every row it prints.
KEY_WIDTH = 16

# How long a field value may be before it is elided, and what marks the elision. ⚑ THE ELLIPSIS
# IS PART OF THE REPORT, not decoration: a truncated value that does not SAY it was truncated is a
# value the reader will quote as complete.
VALUE_WIDTH = 110
ELIDED = "…"


def entry_word(n: int) -> str:
    """Return `entry` or `entries` for a count of n."""
    return "entry" if n == 1 else "entries"


def elide(value: str, width: int = VALUE_WIDTH) -> str:
    """Return `value` cut to `width`, marked when anything was removed."""
    return value if len(value) <= width else value[:width] + ELIDED


@dataclass(frozen=True, slots=True)
class Census:
    """A read's result: how many rows it found, over how large a population.

    ⚑ BOTH NUMBERS OR NEITHER. A `Census` cannot be constructed with only a count, which is the
    structural form of the rule the origin's comments state in prose — the reason `--roundtrip`
    grew its denominator after `0 losses` was found to be unreadable.
    """

    subject: str
    found: int
    population: int

    def line(self) -> str:
        """Return the `n of m` summary line."""
        return f"{self.subject}: {self.found} of {self.population} {entry_word(self.population)}"

    @property
    def total(self) -> bool:
        """Whether the read found nothing over a population it actually covered.

        ⚑⚑ THIS IS THE PREDICATE THE BARE COUNT COULD NOT EXPRESS, and it is why the denominator
        is carried rather than printed and discarded. `found == 0` alone is ambiguous; `found == 0
        and population > 0` is a claim about the input, which is what a caller wants to branch on.
        """
        return self.found == 0 and self.population > 0


def rows(pairs: list[tuple[str, str]]) -> tuple[str, ...]:
    """Return aligned `key value` rows, values elided to the report width."""
    return tuple(f"  {key:<{KEY_WIDTH}} {elide(value)}" for key, value in pairs)


def edge_rows(triples: list[tuple[str, str, str]]) -> tuple[str, ...]:
    """Return the `kind source -> dest` rows the edge modes print."""
    return tuple(f"  {kind:<9} {src:<{KEY_WIDTH}} -> {dest}" for kind, src, dest in triples)


def dangling_rows(triples: list[tuple[str, str, str]]) -> tuple[str, ...]:
    """Return the edge rows the orphan mode prints, each marked and explained.

    ⚑ THE `(no such entry)` SUFFIX IS THE REPORT'S ONLY STATEMENT OF WHAT IS WRONG. An orphan row
    is shaped exactly like an edge row, so without it a reader sees a list of edges and must infer
    from the mode name that these are the broken ones.
    """
    return tuple(
        f"  ⚠ {kind:<9} {src:<{KEY_WIDTH}} -> {dest}   (no such entry)"
        for kind, src, dest in triples
    )
