#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Parse a markdown file into its document AST, and make headings comparable.

⚑⚑ A `#` INSIDE A FENCE IS NOT A HEADER, WHICH IS THE WHOLE REASON THIS TOOLKIT EXISTS. A
`grep '^#'` gets the section skeleton MOSTLY right and fails exactly where it matters: this
repo's plan holds Agda fences with `--` comments and shell fences with `#` comments, and a
setext header (`===` underline) is a header with no leading `#` at all. Every structural mode
reads the parsed document rather than the lines.

⚑⚑⚑ AND `anchor_key` EXISTS BECAUSE A HEADING WITH INLINE MARKUP WAS UNREACHABLE TO EVERY WRITE
MODE. Span anchoring matches each rendered heading against RAW source lines; pandoc strips
inline markup, so ``## Building the tree: `make -j` self-throttles`` renders without the
backticks and the raw line never compared equal. That heading — and, because the scan is a
forward cursor, EVERY SECTION AFTER IT — silently vanished from the span list.

⚑⚑ THE FAILURE WAS INVISIBLE IN THE WORST WAY: the header listing showed the section while the
write mode reported *"no section heading contains …"* for the same file — a message whose own
note calls it "a fact about the QUERY". It was not; it was a fact about the ANCHORING, and it
pointed the reader at their own spelling. Two modes disagreeing about one file is the
census-keyed-on-one-spelling shape, in the tool that owns markdown. MEASURED on this repo's
CLAUDE.md: 3 of 9 headings carry backticks, so a third of the document — and everything after
the first such heading — was unwritable.

⚑ EXTRACTED FROM `scratch/mdstruct.py` (⟡mdstruct-n-split), file-per-mode.
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

import panflute

from substrate import md_pandoc

if TYPE_CHECKING:
    from pathlib import Path

# The markup characters a heading may carry that pandoc's rendering strips. ⚑ A TUPLE, NOT A
# REGEX: the operation is a removal of literal characters, and a pattern here would invite
# someone to extend it into a grammar the renderer does not share.
_MARKUP = ("`", "*", "_")


def ast(path: Path) -> panflute.Doc:
    """Return the parsed document for one markdown file."""
    body = md_pandoc.convert(path.read_text(encoding="utf-8"), "json")
    return panflute.load(io.StringIO(body))


def headers(path: Path) -> list[tuple[int, str]]:
    """Return `[(level, text)]` — the section skeleton, structurally."""
    return [
        (element.level, panflute.stringify(element).strip())
        for element in ast(path).content
        if isinstance(element, panflute.Header)
    ]


def anchor_key(text: str) -> str:
    """Return a heading's ANCHOR KEY: raw source and rendered text, made comparable.

    ⚑ IT OVER-MATCHES ONLY WHERE TWO HEADINGS DIFFER SOLELY BY MARKUP, and the section finder
    REFUSES ambiguity rather than picking one — so the over-match surfaces as a refusal naming
    both candidates, never as a write to the wrong section.
    """
    stripped = text
    for mark in _MARKUP:
        stripped = stripped.replace(mark, "")
    return " ".join(stripped.split()).strip().casefold()
