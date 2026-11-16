# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Find figures a later section contradicts — one phrase carrying two values.

⚑⚑⚑ A FIGURE IS A CLAIM WITH A DATE, AND THIS ARC QUOTED SIX THAT A LATER SECTION SUPERSEDED —
589-vs-1322 leaves, 21-vs-27 gates, 113-vs-345 leaf-own, 12-vs-19 percent, 95-vs-81 conduits,
66-vs-216 ban additions. **Each was found by a human noticing; none by the document.** A number
appearing with two different values beside the SAME phrase is the mechanical signature.

⚑⚑ AND THE PREDICATE WAS WRONG THREE TIMES, EACH FAILURE RECORDED BECAUSE EACH LOOKED RIGHT:

  KEYING ON THE BARE NOUN REPORTED NOISE. Twelve nouns with up to forty values each — `2 files`
  and `2941 files` colliding as a supersession when they are different measurements in different
  sections. A census that wide is one nobody reads, which is the failure it exists to prevent.

  THEN A BARE-NOUN FILTER KILLED THE MOTIVATING CASE. Dropping phrases with no space was meant to
  discard unqualified nouns, but the pattern captures zero to two modifiers, so `589 leaves`
  yields the phrase `leave` with no space and was discarded — the tool reported NOTHING for the
  very supersession that motivated it.

  AND THE TWO SURVIVING CASES ARE STRUCTURALLY IDENTICAL. `589 leaves` vs `1322 leaves` (a real
  supersession) and `2 files` vs `2941 files` (a coincidence) share a noun, carry two values, and
  have no modifier either way. No phrasing rule separates them, so each of the first two attempts
  satisfied one case by breaking the other.

⚑ WHAT SEPARATES THEM IS ORDER OF MAGNITUDE. A supersession re-measures ONE population, so its
values stay within about a factor of ten (589→1322, 21→27, 113→345, 12→19, 95→81, 66→216); a
coincidence spans the document's whole numeric range (2 vs 2941). So a collision is reported only
when the values are PLAUSIBLY THE SAME QUANTITY — and that is a heuristic on a reported census,
never a gate verdict. The tool surfaces the collision; a reader decides.

⚑⚑ THE NOUN ROSTER IS THE KNOWN WEAKNESS AND IT IS EXPOSED RATHER THAN BURIED. `NOUNS` is a
frozen list, which is the shape this repo's own rules name as rotting: a figure counted in a noun
nobody listed is invisible, and the census reports its own vocabulary as if it were the document's.
It is a parameter so a caller can widen it and a case can prove the widening reaches.

⚑⚑⚑ AND IT TAKES LINES, NOT A PATH. The origin opened the file, so the three failed predicates
above could only be exercised against a real document — the same seam that let two wrong
termination rules survive in `fixpoint`.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

#: The nouns a figure is counted in. ⚑ A FROZEN ROSTER, and the census cannot see a figure counted
#: in a noun absent from it — so this is a parameter, not a secret.
NOUNS = (
    "leaves",
    "leaf",
    "gates",
    "gate",
    "modules",
    "module",
    "files",
    "file",
    "keys",
    "key",
    "consumers",
    "consumer",
    "importers",
    "importer",
    "sites",
    "site",
    "cases",
    "case",
    "suites",
    "suite",
    "additions",
    "addition",
)

#: How many words of modifier a phrase may carry. Zero admits the bare noun, which is what makes
#: `589 leaves` visible at all.
MODIFIERS = 2

#: Two distinct values are what a collision IS — fewer is one measurement, not a disagreement.
DISAGREEING = 2

#: Values further apart than this factor are two populations, not one re-measured. Every recorded
#: supersession sits well inside it; the one recorded coincidence spans three orders of magnitude.
RATIO = 10


class Figure(NamedTuple):
    """One value of one phrase, and where it was written."""

    value: int
    line: int


class Collision(NamedTuple):
    """One phrase carrying conflicting values, with every value's first sighting.

    ⚑ THE SPREAD IS REPORTED, NEVER A VERDICT. Two values for one phrase is usually a supersession
    with the later winning, and is sometimes two real populations — so the row names both and a
    reader decides. Collapsing it to `superseded: yes` would make the tool wrong on every honest
    second population.
    """

    phrase: str
    figures: tuple[Figure, ...]

    @property
    def spread(self) -> float:
        """Return the ratio between the largest and smallest value."""
        values = [f.value for f in self.figures]
        return max(values) / min(values)

    def why(self) -> str:
        """Return a one-line account naming the phrase and each value with its line."""
        seen = ", ".join(f"{f.value} at :{f.line}" for f in self.figures)
        return f"{self.phrase!r}: {seen}"


def _order(collision: Collision) -> tuple[int, str]:
    """Return the sort key — most-disagreeing first, then the phrase.

    ⚑ NAMED RATHER THAN A LAMBDA, AND THIS IS THE THIRD TIME IN THIS ARC. An unannotated sort key
    is `Any`, and one `Any` makes every expression downstream unverifiable; the identical leak
    refused `borrowed_root_census` and then `md_lint`, and the named fix written for the second
    was not carried to this one.
    """
    return (-len(collision.figures), collision.phrase)


def _pattern(nouns: Sequence[str]) -> re.Pattern[str]:
    """Return the figure pattern over `nouns`, longest first so a plural is not clipped."""
    ordered = sorted(nouns, key=len, reverse=True)
    return re.compile(
        r"(\d[\d,]*)\s+((?:[a-z][\w-]*\s+){0," + str(MODIFIERS) + r"}"
        r"(?:" + "|".join(re.escape(n) for n in ordered) + r"))"
    )


def _phrase_of(match: re.Match[str]) -> str:
    """Return the normalised phrase a match carries — modifiers included, singularised.

    ⚑ THE GROUPS ARE NARROWED EXPLICITLY. `Match.group` is typed `str | Any`, and one `Any` here
    would make every expression downstream of the phrase unverifiable.
    """
    raw: str = match.group(2)
    return " ".join(raw.lower().split()).rstrip("s")


def _value_of(match: re.Match[str]) -> int:
    """Return the integer a match's figure carries, commas removed."""
    raw: str = match.group(1)
    return int(raw.replace(",", ""))


def figures(lines: Iterable[str], nouns: Sequence[str] = NOUNS) -> dict[str, list[Figure]]:
    """Return every figure found, keyed by its normalised phrase.

    ⚑ THE PHRASE IS THE NOUN PLUS ITS MODIFIERS, singularised. `589 leaves` and `1322 leaves` are
    one claim measured twice; `2 files` and `2941 files` never share a modifier — which is the
    distinction the bare noun could not make and the reason the key is the whole phrase.
    """
    pattern = _pattern(nouns)
    found: dict[str, list[Figure]] = {}
    for i, line in enumerate(lines, 1):
        for m in pattern.finditer(line):
            phrase = _phrase_of(m)
            if not phrase:
                continue
            found.setdefault(phrase, []).append(Figure(_value_of(m), i))
    return found


def collisions(
    lines: Iterable[str], nouns: Sequence[str] = NOUNS, ratio: float = RATIO
) -> list[Collision]:
    """Return every phrase carrying two or more plausibly-same-quantity values.

    ⚑⚑ A ZERO VALUE IS EXCLUDED because no ratio is defined against it, and admitting it would
    make every phrase that ever counted nothing collide with every other value it carries.

    ⚑ ORDERED BY HOW MANY DISTINCT VALUES COLLIDE, so the phrase measured most often — the one
    most likely to have been superseded repeatedly — is read first.
    """
    out: list[Collision] = []
    for phrase, seen in figures(lines, nouns).items():
        first: dict[int, int] = {}
        for figure in seen:
            first.setdefault(figure.value, figure.line)
        if len(first) < DISAGREEING:
            continue
        lo, hi = min(first), max(first)
        if lo == 0 or hi / lo > ratio:
            continue
        rows = tuple(Figure(value, first[value]) for value in sorted(first))
        out.append(Collision(phrase, rows))
    return sorted(out, key=_order)
