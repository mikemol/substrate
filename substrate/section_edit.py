# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Resolve one named section and splice its body — the bounded form of `cat >>`.

⚑⚑⚑ AMBIGUITY IS A REFUSAL, NOT A FIRST MATCH, AND THE TARGET IS A WRITE. A substring naming two
headings cannot be resolved by taking the earlier one: that is the silent-wrong-target class, and a
rewrite that edits the wrong section is not recoverable by re-running. Both candidates are named in
the refusal so the caller can disambiguate.

⚑⚑ A SPLICE, NOT AN AST RENDER, AND THE REASON IS BLAST RADIUS RATHER THAN CORRECTNESS. Rendering
through pandoc is admissible — a tuned writer reaches a fixpoint on this repo's own documents — but
it rewrites the whole file, so a five-line edit arrives as a whole-file diff no reviewer can read
and any not-yet-converged file gets its migration silently bundled into an unrelated change. The
AST answers WHERE the section is; raw lines carry WHAT replaces it.

⚑ THE HEADING LINE IS NEVER TOUCHED. It is the anchor every other reader resolves against, so
replacing it would silently orphan the references pointing at it. Body only — a rename is a
different verb.

⚑⚑ AND THIS TAKES SPANS AND LINES RATHER THAN A PATH, WHICH IS THE DRAIN'S POINT. The origin's
three verbs each took a path, each called a resolver that re-ran pandoc, and each re-read the file
— three reads and three conversions for one edit, and no way to test any of it without a document
on disk and pandoc installed. Here the caller reads once and converts once.

⚑ TRAILING BLANK LINES INSIDE A SECTION SURVIVE BENEATH AN INSERTION. Markdown block separation is
load-bearing, and an append that eats the blank line before the next heading produces a document
that renders differently from the one its author reviewed.

⚑⚑ AND THE GATE REFUSED BOTH REFUSAL MESSAGES BEFORE THIS FILE LANDED (`EM102`, `TRY003`). An
f-string built at the `raise` cannot be reused, compared, or asserted on by a caller; hoisting it
to a named value makes the message a value the suite can drive. The rule reads as style and is not
— a refusal nobody can test is the shape this whole module exists to avoid.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Sequence

    from substrate.heading_spans import Span

#: How many headings a not-found refusal samples, so a reader can tell a bad needle from a
#: reader that lost its rows.
SAMPLE = 5


class SectionError(LookupError):
    """No section matched, or several did.

    ⚑ ONE TYPE FOR BOTH DIRECTIONS, because a caller's recovery is the same — narrow the needle —
    and the message carries which case fired. Two exception types would invite a handler that
    catches one and lets the other escape into a write path.
    """


class Edit(NamedTuple):
    """A spliced document and the section it targeted.

    ⚑ THE TARGET TRAVELS WITH THE RESULT so a caller can report WHAT it edited rather than what it
    asked for. Those differ exactly when a needle matched something unexpected, which is the case a
    reader most needs to see.
    """

    text: str
    section: Span

    def why(self) -> str:
        """Return a one-line account naming the section and the span that was replaced."""
        head = "#" * self.section.level
        return f"{head} {self.section.text!r} at lines {self.section.start}-{self.section.end - 1}"


def _missing(needle: str, spans: Sequence[Span]) -> str:
    """Return the refusal text for a needle that matched nothing.

    ⚑⚑ THE ORIGIN'S MESSAGE ASSERTED A FACT ABOUT THE QUERY AND WAS SOMETIMES WRONG. It said the
    needle names nothing and pointed the reader at a listing mode that was itself dropping
    headings, so a reader whose heading had been LOST was told their spelling was at fault. This
    samples what the reader actually saw, which lets the two cases be told apart.
    """
    seen = ", ".join(repr(s.text) for s in spans[:SAMPLE]) or "none"
    more = "…" if len(spans) > SAMPLE else ""
    return (
        f"no section heading contains {needle!r}. Headings seen: {seen}{more} — if the "
        "expected heading is absent from that list, the READER lost it, which is a "
        "different repair from a wrong needle."
    )


def _ambiguous(needle: str, hits: Sequence[Span]) -> str:
    """Return the refusal text for a needle that matched several sections."""
    names = "; ".join(f"{'#' * h.level} {h.text!r}" for h in hits)
    return (
        f"{needle!r} names {len(hits)} sections: {names}. "
        "⚑ REFUSING rather than picking one — this is a write target."
    )


def find(spans: Sequence[Span], needle: str) -> Span:
    """Return the ONE span whose heading contains `needle`, refusing zero or many."""
    hits = [s for s in spans if needle.lower() in s.text.lower()]
    if not hits:
        raise SectionError(_missing(needle, spans))
    if len(hits) > 1:
        raise SectionError(_ambiguous(needle, hits))
    return hits[0]


def replace(lines: Sequence[str], target: Span, body: str) -> Edit:
    """Return the document with `target`'s BODY replaced, heading kept."""
    new = [*lines[: target.start], *body.rstrip("\n").split("\n"), *lines[target.end - 1 :]]
    return Edit("\n".join(new), target)


def append(lines: Sequence[str], target: Span, body: str) -> Edit:
    """Return the document with `body` appended inside `target`, before the next heading.

    ⚑ THE TRAILING BLANKS ARE SPLIT OFF AND RE-ATTACHED BENEATH, so the separation before the next
    heading survives. Appending after them would place the new text past the blank line, which
    reads as belonging to the following section even though its line number says otherwise.
    """
    body_lines = list(lines[target.start : target.end - 1])
    tail = 0
    while tail < len(body_lines) and not body_lines[len(body_lines) - 1 - tail].strip():
        tail += 1
    keep = body_lines[: len(body_lines) - tail] if tail else body_lines
    blanks = body_lines[len(body_lines) - tail :] if tail else []
    new = [
        *lines[: target.start],
        *keep,
        "",
        *body.rstrip("\n").split("\n"),
        *blanks,
        *lines[target.end - 1 :],
    ]
    return Edit("\n".join(new), target)
