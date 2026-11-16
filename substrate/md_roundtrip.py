# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report what a normalizing round-trip changes — the size and shape of the drift, not a verdict.

⚑⚑⚑ NOT A PASS OR FAIL. Pandoc normalizes BY DESIGN, so `identical` is the unusual case and a bare
boolean would make every honest reflow read as a failure. What a caller needs is how MUCH moved and
WHICH lines, so the report carries both and states no judgement.

⚑⚑ AND THE DRIFT SIZE HAS TWO HONEST MEASURES THAT DISAGREE, WHICH THE DRAIN NEARLY COLLAPSED.
`md_fixpoint.changed_lines` zips positionally — line *i* against line *i* — so an inserted line
makes every following line count as changed; that is exactly right for a CONVERGENCE sequence,
where the question is how much settled between two passes of the same shape. `difflib` ALIGNS, so
an insertion costs one row; that is exactly right for a REPORT a human reads, where the question is
what a reviewer must look at. Reusing the fixpoint counter here would have silently reported a
one-line insertion as hundreds of changes, and the reader would have no way to tell an insertion
from a rewrite.

⚑ SO BOTH ARE CARRIED AND NAMED. `aligned` is what a reviewer reads; `positional` is what a
convergence check counts. A report giving one number cannot say which question it answered.

⚑⚑ IT TAKES TEXTS, NOT A PATH. The origin opened the file and shelled to pandoc, so the difference
above could only be observed by finding a real document whose normalization inserts a line — which
is why one measure stood in for the other unexamined.
"""

from __future__ import annotations

import difflib
from typing import TYPE_CHECKING, NamedTuple

from substrate import md_fixpoint

if TYPE_CHECKING:
    from collections.abc import Sequence

#: How many changed rows a report samples. Enough to see the shape, few enough to read in place.
SAMPLE = 12

#: The diff markers that name a real change, as opposed to a file header.
CHANGE_MARKS = ("+", "-")

#: The diff markers that name a file header, which is not a change.
HEADER_MARKS = ("+++", "---")


class Drift(NamedTuple):
    """What a round-trip moved, in both measures, with a sample of the rows.

    ⚑ `aligned` AND `positional` ANSWER DIFFERENT QUESTIONS AND CAN DIFFER BY ORDERS OF MAGNITUDE.
    An inserted line is one aligned row and every following positional row. Carrying one number
    would leave a reader unable to tell a reflow from an insertion, which is the whole shape of the
    drift they were asking about.
    """

    identical: bool
    aligned: int
    positional: int
    sample: tuple[str, ...]

    @property
    def inserted(self) -> bool:
        """Report whether the two measures disagree, which insertion or deletion causes.

        ⚑ A DISAGREEMENT IS INFORMATIVE, NOT AN ERROR. When the positional count far exceeds the
        aligned one, lines MOVED rather than changed — and a reviewer told only the larger number
        would go looking for edits that were never made.
        """
        return self.positional > self.aligned

    def why(self) -> str:
        """Return a one-line account naming both measures and what their gap means."""
        if self.identical:
            return "identical — the text is already at the writer's fixpoint"
        note = " (lines moved, so the positional count runs ahead)" if self.inserted else ""
        return f"{self.aligned} aligned row(s), {self.positional} positional{note}"


def _changed_rows(before: str, after: str) -> list[str]:
    """Return every added or removed row of the unified diff, headers excluded.

    ⚑ `n=0` KEEPS THE CONTEXT OUT. A report meant to be read in place should carry the rows that
    CHANGED, not three unchanged lines around each of them — which at this document's width would
    bury the sample it is supposed to be.
    """
    rows = difflib.unified_diff(before.split("\n"), after.split("\n"), lineterm="", n=0)
    return [
        row for row in rows if row.startswith(CHANGE_MARKS) and not row.startswith(HEADER_MARKS)
    ]


def compare(before: str, after: str, sample: int = SAMPLE) -> Drift:
    """Return the drift between two texts, in both measures, with a bounded sample.

    ⚑ THE IDENTICAL CASE SHORT-CIRCUITS because a diff of a text with itself is empty anyway, and
    saying so explicitly is what lets `identical` be a fact rather than an inference from a zero.
    """
    if before == after:
        return Drift(identical=True, aligned=0, positional=0, sample=())
    rows = _changed_rows(before, after)
    return Drift(
        identical=False,
        aligned=len(rows),
        positional=md_fixpoint.changed_lines(before, after),
        sample=tuple(rows[:sample]),
    )


def summarise(drifts: Sequence[Drift]) -> str:
    """Return one line covering several round-trips, with its denominator.

    ⚑ THE DENOMINATOR IS NOT OPTIONAL. `0 drifted` and `0 drifted of 40` are different claims, and
    only the second distinguishes a clean corpus from a run that examined nothing.
    """
    moved = [d for d in drifts if not d.identical]
    return f"round-trip: {len(moved)} of {len(drifts)} document(s) drift under normalization"
