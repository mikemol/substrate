# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report meaning-changing edits that a convergence check cannot see.

⚑⚑⚑ A FIXPOINT IS NOT A LOSSLESS TRANSFORM, AND THE TOOLING CONFLATED THEM. A fixpoint check asks
*does normalization converge*; it never asks *does the converged text still mean the same thing*.
The round-trip report measured the drift and then told the reader to disregard it — *"pandoc
NORMALIZES by design — this is expected, not a failure"* — deferring the whole verdict to
convergence. **So both gates passed a write that damaged the document.**

⚑⚑ MEASURED ON A MEMORY FILE (2026-08-03), and every item here is from that one run. The converged
output escaped the pipe character inside inline code, making a PSI selector wrong as written;
escaped every wikilink, which is the memory mesh's edge structure; escaped the tilde; replaced
straight quotes with typographic ones; and **DROPPED THE YAML FRONTMATTER ENTIRELY** — `name:`,
`type:`, `originSessionId:`, a memory's identity. It reported zero rounds and a clean fixpoint.
Converged, idempotent, and wrong.

⚑ THE CLASS IT BELONGS TO. `libcst` round-trips the Python corpus BYTE-FOR-BYTE, so *is it
lossless* is the right precondition there; pandoc is a NORMALIZING converter, so the right
precondition is idempotence PLUS a preservation check. Asking only the first question of a
normalizer is what put a prose writer over a corpus of inline code and link structure.

⚑⚑ EVERY CHECK IS ON THE DELTA, NEVER ON THE OUTPUT ALONE. A document that already contained an
escape is not flagged — only text the transform ITSELF changed. Checking the output alone would
report the corpus's own notation as damage on every run, which is the census-that-cries-wolf shape
that teaches a reader to skim.

⚑⚑⚑ AND THE FRONTMATTER QUESTION IS `md_frontmatter`'s, NOT RE-DERIVED HERE. The origin carried a
local predicate testing for an opening fence and a later closing one; that reading calls an
unterminated fence frontmatter, where the owner correctly reads it as a document whose first line
is a rule. A second spelling of the rule would make this reader disagree with the writer about
what a body is.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, NamedTuple

from mikemol.mdstruct import frontmatter as md_frontmatter

if TYPE_CHECKING:
    from collections.abc import Sequence

#: Inline code spans — the content a transform must not rewrite.
CODE = re.compile(r"`([^`\n]+)`")

#: An unescaped wikilink opener. These are mesh EDGES, not text.
WIKILINK = re.compile(r"(?<!\\)\[\[")

#: The typographic quotes a prose writer substitutes for straight ones.
SMART = ("\N{RIGHT SINGLE QUOTATION MARK}", "\N{LEFT DOUBLE QUOTATION MARK}")

#: The straight quotes they replace.
STRAIGHT = ("'", '"')


class Damage(NamedTuple):
    """One meaning-changing edit, named by kind with the detail a reader needs.

    ⚑ THE KIND AND THE DETAIL ARE BOTH LOAD-BEARING. The kind says which preservation property
    broke — they have different repairs, from a writer flag to abandoning the transform — and the
    detail carries the instance, because `escape-in-code` without the affected span sends a reader
    hunting a whole document.
    """

    kind: str
    detail: str


def _codes(text: str) -> set[str]:
    """Return the content of every inline code span.

    ⚑ `finditer` WITH AN EXPLICIT NARROWING, NEVER `findall`. `findall` is typed `list[Any]`, and
    one `Any` makes every expression downstream unverifiable — the same leak family as an
    unannotated sort key, which refused three writes earlier in this arc.
    """
    out: set[str] = set()
    for match in CODE.finditer(text):
        span: str = match.group(1)
        out.add(span)
    return out


def _wikilinks(text: str) -> int:
    """Return how many unescaped wikilink openers the text holds."""
    return sum(1 for _ in WIKILINK.finditer(text))


def frontmatter_dropped(before: str, after: str) -> list[Damage]:
    """Return the damage when frontmatter present before is absent after.

    ⚑ FOR A MEMORY THIS IS ITS IDENTITY — `name:`, `type:`, provenance. A body-only writer emits
    valid markdown and silently discards what the file IS.
    """
    had, _ = md_frontmatter.split(before)
    has, _ = md_frontmatter.split(after)
    if had and not has:
        return [
            Damage(
                "frontmatter-dropped",
                "YAML frontmatter present before, absent after — for a memory this is "
                "its name, type and provenance",
            )
        ]
    return []


def escaped_code(before: str, after: str) -> list[Damage]:
    """Return the damage when a transform introduced backslashes INSIDE inline code.

    ⚑⚑ THE TEST IS THAT UNESCAPING RECOVERS A SPAN THE INPUT HELD. That is what distinguishes an
    escape the transform ADDED from a span the document always wrote with a backslash — and it is
    why the check is on the delta rather than on the presence of a backslash.
    """
    was, now = _codes(before), _codes(after)
    added = sorted(span for span in now - was if "\\" in span and span.replace("\\", "") in was)
    if added:
        return [
            Damage(
                "escape-in-code",
                f"backslashes introduced inside inline code (e.g. {added[0]}) — the code "
                f"no longer reads as written",
            )
        ]
    return []


def escaped_wikilinks(before: str, after: str) -> list[Damage]:
    """Return the damage when unescaped wikilinks were lost.

    ⚑ A COUNT DROP IS THE SIGNAL BECAUSE THE ESCAPE IS INVISIBLE OTHERWISE. An escaped link still
    reads as a link to a human and resolves to nothing in the mesh.
    """
    had = _wikilinks(before)
    has = _wikilinks(after)
    if had and has < had:
        return [
            Damage(
                "wikilink-escaped",
                f"{had - has} of {had} [[links]] escaped — these are mesh edges, not text",
            )
        ]
    return []


def smart_quotes(before: str, after: str) -> list[Damage]:
    """Return the damage when straight quotes became typographic ones.

    ⚑ ONLY WHEN THE INPUT HELD NONE. A document already written with typographic quotes is not
    damaged by a transform that preserves them, and flagging it would make the check fire forever
    on a corpus that made its choice deliberately.
    """
    if not any(q in before for q in STRAIGHT):
        return []
    if any(q in before for q in SMART):
        return []
    if any(q in after for q in SMART):
        return [
            Damage(
                "smart-quotes",
                "straight quotes converted to typographic quotes — literal text changed",
            )
        ]
    return []


def damage(before: str, after: str) -> list[Damage]:
    """Return every preservation failure the transform introduced, in a stable order.

    ⚑ THE CHECKS ARE INDEPENDENT AND ALL ARE RUN. Returning at the first failure would report one
    damaged property of a write that broke four, and the repair for each is different — so a
    reader needs the whole set rather than the first item.
    """
    checks = (frontmatter_dropped, escaped_code, escaped_wikilinks, smart_quotes)
    return [row for check in checks for row in check(before, after)]


def kinds(rows: Sequence[Damage]) -> tuple[str, ...]:
    """Return the kinds present, for a caller that needs the shape rather than the detail."""
    return tuple(row.kind for row in rows)
