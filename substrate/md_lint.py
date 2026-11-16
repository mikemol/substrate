# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The markdownlint classes, measured on a document rather than assumed about it.

⚑⚑⚑ IT EXISTS BECAUSE FOUR RULES WERE ABOUT TO BE DISABLED WITHOUT ANY OF THEM BEING MEASURED
(operator, 2026-08-03: *"See, this I don't want to do … The question is, how can we make things
not incompatible with them?"*). Turning a rule off is the allow-list move: it rots, and it hides
the population instead of retiring it. The honest move is to ask what each rule actually finds
here — which nothing could answer, because the linter is an IDE extension and not something a
tool call can invoke.

⚑⚑ AND MOST OF THESE ARE SATISFIABLE RATHER THAN INCOMPATIBLE. `MD013` wants a width the document
already has; it needs only to be TOLD the width the writer emits, which makes the rule AGREE with
the writer instead of being suppressed by it. `MD041` is the one genuine mismatch — it wants an H1
title, and a memory's title lives in its `name:` field, so duplicating it as a heading would be
two spellings of one fact.

⚑ THE CODE-SPAN GUARD IS THE PART THAT WAS MEASURED WRONG FIRST, and the witness line caught it.
The origin's `MD033` check counted backticks around the match under a condition that admitted
`<n> bytes allocated` — text plainly INSIDE code — and the document was nearly "fixed" to satisfy
a false positive. Masking code spans before looking is the same read-the-structure move that
`mask_comments` makes for Agda, and printing the offending line is what made the error visible
where a count would have sent a reader editing correct prose.

⚑⚑ THIS TAKES LINES, NOT A PATH, WHICH IS WHY IT IS TESTABLE. The origin opened the file itself,
so every case needed a real document and no case could state a rule precisely. The caller reads;
this measures.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

#: The width the writer emits. A rule told this AGREES with the writer rather than being suppressed.
WIDTH = 120

#: A fence opens or closes a code block; its content is exempt from every rule here.
FENCE = "```"

#: A list item needs a predecessor to be judged against, so line one can never carry MD032.
_FIRST_JUDGEABLE = 2

#: An inline code span, masked before the HTML scan so code never reads as markup.
_SPAN = re.compile(r"`[^`]*`")

#: Raw inline HTML — a tag name, optional attributes, outside code.
_HTML = re.compile(r"<(/?[A-Za-z][A-Za-z0-9-]*)(\s[^>]*)?>")

#: A list item: a bullet or an ordered marker at up to three spaces of indent.
_ITEM = re.compile(r"^\s{0,3}([-*+]|\d+[.)])\s")


class Finding(NamedTuple):
    """One rule firing on one line, with the detail a reader needs to act.

    ⚑ THE DETAIL IS NOT DECORATION. `MD013` without the measured width says only that some line is
    too long, and the repair depends on by how much; `MD033` without the tag name sends a reader
    hunting the line for markup that may be in code.
    """

    line: int
    rule: str
    detail: str


def _blank(match: re.Match[str]) -> str:
    """Return spaces of the matched span's width, so masking preserves every column."""
    return " " * len(match.group(0))


def _uncoded(text: str) -> str:
    """Return `text` with inline code spans blanked, preserving every column.

    ⚑ LENGTH-PRESERVING, so a column reported against the masked line is true of the real one. A
    mask that shortened the line would move every offset after the first code span.
    """
    return _SPAN.sub(_blank, text)


def _body_lines(lines: Sequence[str]) -> Iterator[tuple[int, str]]:
    """Yield `(1-indexed line number, text)` for every line outside a fenced block."""
    in_fence = False
    for i, text in enumerate(lines, 1):
        if text.lstrip().startswith(FENCE):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield i, text


def _order(finding: Finding) -> tuple[int, str]:
    """Return the sort key — line then rule, so a reader can walk the report.

    ⚑ NAMED RATHER THAN A LAMBDA, because an unannotated sort key is `Any` and one `Any` makes
    every expression downstream of it unverifiable. The identical leak refused
    `borrowed_root_census` earlier in this arc, in the identical position.
    """
    return (finding.line, finding.rule)


def long_lines(lines: Sequence[str], width: int = WIDTH) -> list[Finding]:
    """Return every MD013 finding — a body line wider than `width`."""
    return [
        Finding(i, "MD013", f"line is {len(text)} > {width}")
        for i, text in _body_lines(lines)
        if len(text) > width
    ]


def inline_html(lines: Sequence[str]) -> list[Finding]:
    """Return every MD033 finding — raw inline HTML outside code spans."""
    return [
        Finding(i, "MD033", f"inline HTML <{m.group(1)}>")
        for i, text in _body_lines(lines)
        for m in _HTML.finditer(_uncoded(text))
    ]


def loose_lists(lines: Sequence[str]) -> list[Finding]:
    """Return every MD032 finding — a list item whose predecessor is prose.

    ⚑ A CONTINUATION LINE IS NOT PROSE. An indented predecessor belongs to the item above, so
    treating it as prose would report every multi-line list entry as a defect.
    """
    out: list[Finding] = []
    for i, text in _body_lines(lines):
        if i < _FIRST_JUDGEABLE or not _ITEM.match(text):
            continue
        prev = lines[i - _FIRST_JUDGEABLE]
        if prev.strip() and not _ITEM.match(prev) and not prev.startswith("  "):
            out.append(Finding(i, "MD032", "list not preceded by a blank line"))
    return out


def opens_with_heading(lines: Sequence[str]) -> list[Finding]:
    """Return the MD041 finding when the body's first non-blank line is not a heading.

    ⚑ IT IS A PROPERTY OF THE BODY, NEVER OF THE FILE. Frontmatter is excluded by the caller, so a
    `name:` value must not read as the opening prose — which is exactly what made this rule look
    incompatible rather than satisfiable.
    """
    first = next((text for text in lines if text.strip()), "")
    if first and not first.startswith("#"):
        return [Finding(1, "MD041", "body does not open with a heading")]
    return []


def findings(lines: Sequence[str], width: int = WIDTH, offset: int = 0) -> list[Finding]:
    """Return every finding across the four rules, in line order.

    ⚑ `offset` IS THE FRONTMATTER'S LINE COUNT, AND IT IS THE CALLER'S TO SUPPLY. This module
    measures a body; only the reader that split the document knows where the body began, and
    re-deriving the split here would be a second authority on it.
    """
    every = (
        long_lines(lines, width)
        + inline_html(lines)
        + loose_lists(lines)
        + opens_with_heading(lines)
    )
    return sorted((Finding(f.line + offset, f.rule, f.detail) for f in every), key=_order)
