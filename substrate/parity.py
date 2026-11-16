#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Compare a rewritten reader against the one it replaces, while both are still on disk.

⚑⚑⚑ THE WINDOW IS THE WHOLE POINT AND IT CLOSES. A rewritten reader that DISAGREES with its
origin is invisible to a suite written against the rewrite — cases pin whatever the rewrite
happens to do, so a faithful port and a subtly broken one both go green. The origin runs only
until it is retired; after that this instrument does not exist and only the cases remain.

⚑⚑ MEASURED: eleven ad-hoc probes of this shape were written across one session and caught what
no suite could — five dropped stopwords in a transcribed constant, two header spellings whose
absence cost three tools EVERY mode, and a symmetric relation compared as ordered tuples. Every
one passed its own suite, because a suite inherits the blind spot of whoever wrote both.

⚑⚑⚑ AND THE COST SIDE IS REAL, SO IT IS BUILT IN. Of five disagreements found that session,
THREE were defects in the PROBE or intended changes misread as regressions. A parity probe is a
second implementation carrying a second implementation's bugs; its output is EVIDENCE, never a
verdict. `Disagreement` is therefore a row a reader adjudicates, not a failure.

⚑⚑ AN UNREACHABLE ORIGIN IS `UNMEASURED`, NEVER `AGREED`. The single most dangerous outcome here
is a probe that cannot load its origin and reports zero disagreements — indistinguishable from a
clean comparison, and banked as one. `compare` returns the state explicitly and the exit code
separates the three.

⚑ THE SHARED POPULATION IS COMPUTED, NOT ASSUMED. An extraction usually widens what the reader
can see (a directory the origin never scanned), and rows that exist on only one side are THE
WIDENING, not a defect. Comparing over the union reports the intended change as a regression,
which is how three of those five false disagreements arose.

⚑ EXTRACTED FROM ELEVEN `parity_*.py` PROBES that lived in a session scratchpad — untracked,
ungated, and known only to their author. Operator: *"if you're going to have to write something
high-quality anyway, write it somewhere it can persist."* The pattern was one module with eleven
callers all along.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

# How many differing keys to name per row, so one wide disagreement cannot bury the rest.
SHOW = 8

# The states a comparison can end in. ⚑ THREE, and collapsing the third is the defect.
AGREED = "AGREED"
DIFFERING = "DIFFERING"
UNMEASURED = "UNMEASURED"

# Exit codes: agreement passes, disagreement fails, and an unmeasured run is neither.
CODES = {AGREED: 0, DIFFERING: 1, UNMEASURED: 2}


@dataclass(frozen=True, slots=True)
class Disagreement:
    """One place the two readers differ — a row to adjudicate, not a verdict."""

    what: str
    only_origin: tuple[str, ...]
    only_new: tuple[str, ...]

    def render(self, show: int = SHOW) -> str:
        """Return this disagreement as a reader sees it."""
        return (
            f"{self.what}\n"
            f"   only-origin: {list(self.only_origin[:show])!r}\n"
            f"   only-new:    {list(self.only_new[:show])!r}"
        )


@dataclass(frozen=True, slots=True)
class Report:
    """What a comparison established, over what population."""

    state: str
    disagreements: tuple[Disagreement, ...]
    population: int
    why: str = ""

    @property
    def exit_code(self) -> int:
        """Return 0 agreed, 1 differing, 2 unmeasured.

        ⚑ UNMEASURED IS NOT A PASS. A probe that could not load its origin has established
        nothing, and reporting 0 would bank an unmeasured claim as a clean comparison.
        """
        return CODES[self.state]

    def render(self) -> str:
        """Return the whole comparison, rendered."""
        if self.state == UNMEASURED:
            return (
                f"parity: UNMEASURED — {self.why}\n"
                f"   ⚑ NOT agreement. The origin could not be read, so nothing was compared."
            )
        lines = [row.render() for row in self.disagreements]
        lines.append(
            f"\n{self.population} shared item(s), {len(self.disagreements)} disagreement(s)"
        )
        if self.disagreements:
            lines.append(
                "   ⚑ A DISAGREEMENT IS EVIDENCE, NOT A VERDICT: it may be the probe's "
                "defect or an\n     intended change. Three of five found in one session "
                "were exactly that."
            )
        return "\n".join(lines)


def shared(
    origin_keys: Iterable[str], new_keys: Iterable[str], widened: str = ""
) -> frozenset[str]:
    """Return the population both readers can see.

    ⚑ `widened` NAMES A PREFIX THE ORIGIN STRUCTURALLY CANNOT SEE — usually a directory the
    extraction added. Rows under it are the INTENDED CHANGE, and including them would report the
    widening as a regression.
    """
    left = {key for key in origin_keys if not (widened and key.startswith(widened))}
    right = {key for key in new_keys if not (widened and key.startswith(widened))}
    return frozenset(left & right)


def differing_keys(what: str, origin: Iterable[str], new: Iterable[str]) -> Disagreement | None:
    """Return the membership difference between two key sets, or None when they agree."""
    left, right = set(origin), set(new)
    if left == right:
        return None
    return Disagreement(
        what=what, only_origin=tuple(sorted(left - right)), only_new=tuple(sorted(right - left))
    )


def differing_values(
    what: str, origin: Mapping[str, str], new: Mapping[str, str]
) -> Disagreement | None:
    """Return the keys whose VALUES differ across both readers, or None when they agree.

    ⚑ THE VALUE IS COMPARED, NOT ONLY THE KEY. Two censuses can hold identical keys and opposite
    verdicts — `FIXTURE` and `UNDOCUMENTED` are the same row with different consequences, and a
    key-only comparison calls that agreement.
    """
    both = set(origin) & set(new)
    clashing = tuple(sorted(key for key in both if origin[key] != new[key]))
    if not clashing:
        return None
    return Disagreement(
        what=what,
        only_origin=tuple(f"{key}={origin[key]}" for key in clashing),
        only_new=tuple(f"{key}={new[key]}" for key in clashing),
    )


def compare(found: Iterable[Disagreement | None], population: int) -> Report:
    """Return the report for a set of comparisons over a shared population."""
    rows = tuple(row for row in found if row is not None)
    return Report(state=DIFFERING if rows else AGREED, disagreements=rows, population=population)


def unmeasured(why: str) -> Report:
    """Return the report for a comparison that could not be made.

    ⚑ THE REASON TRAVELS. *"The origin could not be imported"* and *"the origin has no such
    attribute"* send a reader to different places, and a bare UNMEASURED sends them to neither.
    """
    return Report(state=UNMEASURED, disagreements=(), population=0, why=why)


def report(result: Report) -> int:
    """Print a comparison and return its exit code."""
    sys.stdout.write(result.render() + "\n")
    return result.exit_code
