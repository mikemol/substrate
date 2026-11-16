# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Make a heading's RENDERED text and its RAW source line comparable.

⚑⚑⚑ THIS IS THE ANCHORING PROBLEM, AND IT IS WHY WHOLE DOCUMENTS READ AS EMPTY. A markdown reader
that walks the pandoc AST gets each heading's rendered text, then locates it in the source by
matching that text against raw lines. Pandoc REWRITES as it renders, so the two spellings differ
and the match fails — the heading is dropped, and because the scan is a forward cursor, every
section after it goes with it.

⚑⚑ TWO REWRITE CLASSES, AND THE ORIGIN COVERED ONLY THE FIRST. Inline markup was found first:
`` ## Building the tree: `make -j` self-throttles `` renders without the backticks, so a third of
this repo's own CLAUDE.md was unreachable to every write mode. SMART PUNCTUATION is the second and
was never covered — pandoc turns `'` into a curly apostrophe, `--` into an en dash, `---` into an
em dash, and `...` into an ellipsis, and none of those characters were in the table.

⚑⚑⚑ THE SECOND CLASS WAS MEASURED ON A REAL DOCUMENT, NOT IMAGINED. A peer's 14-heading file read
as ZERO headings: thirteen of its H2s carry `---` and its H1 carries an apostrophe, so every
single heading missed its anchor. The per-heading nature was proved by INSERTING one clean heading
among the triggered ones — it survives, which a wholesale walk failure could not have allowed.

⚑⚑ AND THE FIX IS TO NORMALISE BOTH SIDES TOWARD THE RENDERED FORM, never to undo the rendering.
Mapping the raw source's `---` to an em dash makes the two meet at what pandoc produces; mapping
the em dash back to `---` would have to guess whether the author wrote three hyphens or the
character. The transform is many-to-one in one direction and ambiguous in the other, so the
direction is forced.

⚑ ONE MEASURED EXCEPTION, RECORDED RATHER THAN SMOOTHED. Double quotes survive today even though
pandoc's smart extension does transform them, so this account is right about four inputs and does
not explain the fifth. The quote entries are included because the transform is real; if a heading
carrying double quotes ever drops, that exception is where to look and the surprise is that it
worked before, not that it broke.

⚑ THE KEY IS LOSSY BY DESIGN, WHICH BOUNDS WHAT IT CAN PROMISE. Folding case and whitespace and
markup means two headings differing only in those respects produce one key. That is acceptable
only because the caller REFUSES an ambiguous match rather than picking one — a resolver that
guessed would turn this normalisation into silent misdirection.
"""

from __future__ import annotations

#: Inline markup pandoc strips when rendering — the first class, found via backticked headings.
MARKUP = ("`", "*", "_")

#: Smart-punctuation rewrites, RAW source spelling to the character pandoc renders.
#: ⚑ ORDER MATTERS: `---` must be replaced before `--`, or the em dash is consumed as an en dash
#: followed by a stray hyphen. A dict preserves insertion order, and the longest source spelling
#: is listed first for exactly that reason.
SMART = {
    "---": "\N{EM DASH}",
    "--": "\N{EN DASH}",
    "...": "\N{HORIZONTAL ELLIPSIS}",
    "'": "\N{RIGHT SINGLE QUOTATION MARK}",
}


def fold_smart(text: str) -> str:
    """Return `text` with each raw smart-punctuation spelling replaced by its rendered character.

    ⚑ THIS RUNS ON BOTH SIDES OF THE COMPARISON, and that is what makes it safe. Applied to raw
    source it converts `---` to an em dash; applied to already-rendered text it finds nothing to
    change, because the source spellings are gone. So one function normalises both inputs and no
    caller has to know which side it holds.
    """
    out = text
    for raw, rendered in SMART.items():
        out = out.replace(raw, rendered)
    return out


def strip_markup(text: str) -> str:
    """Return `text` with the inline-markup characters pandoc drops when rendering removed."""
    out = text
    for mark in MARKUP:
        out = out.replace(mark, "")
    return out


def key(text: str) -> str:
    """Return a heading's anchor key — comparable whether it came from source or from the AST.

    ⚑ THE ORDER IS SMART-PUNCTUATION THEN MARKUP THEN WHITESPACE THEN CASE, and only the first
    pairing matters: stripping backticks cannot create or destroy a `---`, so markup and smart
    punctuation commute. Whitespace folding must come after both, because removing markup can
    leave adjacent spaces that were separated by a character.
    """
    return " ".join(strip_markup(fold_smart(text)).split()).strip().casefold()


def unmatched(rendered: str, sources: list[str]) -> bool:
    """Report whether `rendered` fails to key-match any line in `sources`.

    ⚑ THE CALLER NEEDS TO ASK BEFORE IT SCANS, because a forward cursor that fails to anchor loses
    every section after the failure rather than just the one. A reader that can name the heading it
    could not place reports a locatable defect where a silent drop reports an empty document.
    """
    want = key(rendered)
    return all(key(line.lstrip("#")) != want for line in sources)
