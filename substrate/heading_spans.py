# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Anchor rendered headings to their source lines and compute each section's span.

⚑⚑⚑ THE ORIGIN DROPPED AN UNANCHORED HEADING IN SILENCE, AND THAT SILENCE IS THE REAL DEFECT.
Its inner scan simply fell through when no source line matched, so the heading vanished from the
result with nothing recorded — and a document whose headings all fail to anchor read as a document
with no sections. Two sessions independently read that emptiness as a fact about the markdown
rather than about the reader, which is what a silent drop buys.

⚑⚑ SO THE RESULT CARRIES BOTH SIDES. `Anchored` holds the spans AND the headings that could not be
placed, because those are different facts and a caller that sees only the first cannot tell a
document with three sections from a document with fourteen where eleven failed to anchor. The
denominator travels with the verdict, which is this tree's standing rule applied to a reader that
had no way to state it.

⚑⚑⚑ THE MATCH IS KEYED THROUGH `heading_key`, WHICH IS WHERE THE TRIGGER CLASSES LIVE. Pandoc
rewrites as it renders — inline markup stripped, smart punctuation transformed — so a rendered
heading and its raw line differ in ways that have nothing to do with the author. The origin's key
covered markup and not punctuation, so `## Overview --- two layers` never matched its own source.

⚑ A SPAN ENDS AT THE NEXT HEADER OF THE SAME-OR-SHALLOWER LEVEL, never simply the next header.
`### 69` containing a `#### sub` does not end at `sub`. Getting that wrong yields a correct-looking
short section, which is the failure a line-regex produces and a reader cannot see.

⚑ AND THE SCAN IS A FORWARD CURSOR ON PURPOSE, so a repeated heading text cannot rebind to an
earlier occurrence. That is also why an unanchored heading is expensive: the cursor does not
advance, so the failure is local, but every later heading is matched against a source region that
still contains the unplaced one.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from substrate import heading_key

if TYPE_CHECKING:
    from collections.abc import Sequence


class Span(NamedTuple):
    """One section: its level, its rendered text, and its 1-indexed bounds, `end` EXCLUSIVE."""

    level: int
    text: str
    start: int
    end: int


class Anchored(NamedTuple):
    """Placed spans AND the headings that could not be placed.

    ⚑ `total` AND `placed` ARE BOTH CARRIED so a caller can state the denominator. A bare list of
    spans cannot distinguish a short document from a document the reader could not read, and that
    ambiguity is exactly what let a fourteen-heading file report as empty.
    """

    spans: list[Span]
    unanchored: list[tuple[int, str]]

    @property
    def total(self) -> int:
        """Report how many headings the document held, placed or not."""
        return len(self.spans) + len(self.unanchored)

    @property
    def complete(self) -> bool:
        """Report whether every heading found a source line."""
        return not self.unanchored

    def why(self) -> str:
        """Return a one-line account naming the components of the verdict.

        ⚑ THE FAILING CASE NAMES THE FIRST HEADING IT COULD NOT PLACE. A message saying only that
        some headings were lost leaves the reader to re-derive which — and the whole point of
        reporting the failure is that it is locatable.
        """
        if self.complete:
            return f"{len(self.spans)} of {self.total} heading(s) anchored"
        first = self.unanchored[0][1]
        return (
            f"{len(self.spans)} of {self.total} heading(s) anchored — "
            f"{len(self.unanchored)} UNANCHORED, first: {first!r}"
        )


def anchor(headings: Sequence[tuple[int, str]], lines: Sequence[str]) -> Anchored:
    """Place each rendered heading against `lines`, reporting the ones that do not match.

    ⚑⚑ TAKES THE HEADINGS AND THE LINES RATHER THAN A PATH, which is what makes it testable
    without a document and without pandoc. The origin fused the AST read, the file read and the
    anchoring into one function, so its only test surface was a real file on disk.
    """
    placed: list[tuple[int, str, int]] = []
    missed: list[tuple[int, str]] = []
    cursor = 0
    for level, text in headings:
        want = heading_key.key(text)
        for i in range(cursor, len(lines)):
            line = lines[i].lstrip()
            if line.startswith("#") and heading_key.key(line.lstrip("#")) == want:
                placed.append((level, text, i + 1))
                cursor = i + 1
                break
        else:
            missed.append((level, text))
    return Anchored(_close(placed, len(lines)), missed)


def _close(placed: Sequence[tuple[int, str, int]], line_count: int) -> list[Span]:
    """Return spans, each closed by the next heading of the same-or-shallower level."""
    out: list[Span] = []
    for idx, (level, text, start) in enumerate(placed):
        end = line_count + 1
        for level2, _text2, start2 in placed[idx + 1 :]:
            if level2 <= level:
                end = start2
                break
        out.append(Span(level, text, start, end))
    return out
