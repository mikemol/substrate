#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Normalise a heading so raw source and rendered text compare equal.

⚑⚑⚑ WHY THIS EXISTS, AND IT HAS COST A CENSUS LEG (Ⓑ0, gate-F78, gate-F82, gate-G8).
`mdstruct.spans` anchors each pandoc heading by matching its RENDERED text against the RAW
source lines through a normaliser, with a FORWARD CURSOR. When the two spellings do not
compare equal the heading never matches, the cursor does not advance, and **the previous
section's span silently swallows it**. Not an error — a predecessor that simply reads longer.

⚑⚑ THE ORIGIN NORMALISED MARKUP AND NOT PUNCTUATION, AND THAT IS THE WHOLE DEFECT. It strips
backticks, asterisks and underscores — written because a heading with inline markup was
unreachable, and it fixed the markup case only. **Pandoc also rewrites the ASCII apostrophe
U+0027 to the typographic U+2019**, so a heading containing one has two spellings that the
origin leaves untouched and therefore never reconciles. A normaliser written to reconcile two
spellings reconciled the spellings its author had seen.

⚑ THE MEASURED COST, TWICE OVER. On this repo's own plan file, `--headers` reported fewer
sections than `--budget` — a floor read as a roster. And filing a four-party census leg, a
heading containing an apostrophe vanished from `--headers` while `--budget` saw it, with the
preceding section's span extended over it. That item is the one the census brief names as
**the highest-value item in the whole census**.

⚑⚑⚑ SO THE CLASS IS WIDER THAN THE APOSTROPHE AND THE FIX IS NAMED ACCORDINGLY. Any character
pandoc rewrites during rendering reproduces it: the quotes, the dashes, the ellipsis. Fixing
only the apostrophe would be the origin's mistake at one character's remove — patching the
trigger rather than widening the class, which this repo has recorded as a defect shape in its
own right. So the table below is by TRANSFORMATION KIND, and each entry names what pandoc does.

⚑ THE TABLE USES `\N{...}` ESCAPES RATHER THAN LITERALS, AND THE GATE ASKED FOR THAT. `RUF001`
refuses a literal typographic quote as *ambiguous with ASCII* — correct in general, and
pointed here at the one file where that ambiguity IS the subject. A named escape carries
identical bytes while making the codepoint explicit, which a reader auditing this table needs
anyway. ⚑ The module docstring is a raw string so those escapes read as themselves here.

⚑ AND IT IS ITS OWN MODULE BECAUSE THE ORIGIN CANNOT BE EDITED. `pycodemod --types
scratch/mdstruct.py` reports nine mypy codes behind an all-or-nothing per-file gate, so a
five-line repair to the function cannot land there. Extract clean, then the origin's two call
sites become one import when that file can be written.
"""

from __future__ import annotations

# ⚑ WHAT PANDOC REWRITES WHEN IT RENDERS, as `rendered -> raw`. Each pair is a SMART-TYPOGRAPHY
# substitution: the left side is what the AST carries and the right is what an author types, so
# a comparison that does not fold them is comparing two spellings of one heading.
SMART: tuple[tuple[str, str], ...] = (
    ("\N{RIGHT SINGLE QUOTATION MARK}", "'"),  # <- the ASCII apostrophe. THE MEASURED ONE.
    ("\N{LEFT SINGLE QUOTATION MARK}", "'"),  # <- an opening single quote
    ("\N{LEFT DOUBLE QUOTATION MARK}", '"'),  # <- an opening double quote
    ("\N{RIGHT DOUBLE QUOTATION MARK}", '"'),  # <- a closing double quote
    ("\N{EM DASH}", "--"),  # <- two hyphens
    ("\N{EN DASH}", "-"),  # <- one hyphen
    ("\N{HORIZONTAL ELLIPSIS}", "..."),  # <- three dots
)

# ⚑ INLINE MARKUP THE RENDERER DROPS ENTIRELY. The origin normalised exactly these and nothing
# else, which is why it worked for code-span headings and failed for apostrophes.
MARKUP: tuple[str, ...] = ("`", "*", "_")


def hkey(text: str) -> str:
    """Return a heading's comparison key: smart typography folded, markup dropped, case folded.

    ⚑ THE ORDER MATTERS. Smart characters fold to their ASCII source FIRST, because an em dash
    folds to a pair of hyphens and a later markup strip must not then treat them as something
    to remove. Whitespace collapses last, so a fold that introduces a space cannot leave two.
    """
    out = text
    for rendered, raw in SMART:
        out = out.replace(rendered, raw)
    for mark in MARKUP:
        out = out.replace(mark, "")
    return " ".join(out.split()).strip().casefold()


def agree(raw: str, rendered: str) -> bool:
    """Whether a raw source heading and its rendered text are the same heading.

    ⚑ THE LEADING HASHES ARE THE CALLER'S TO STRIP, not this function's. A key that silently
    accepted a hash-prefixed line as equal to its own text would also accept a heading against
    a comment or a fenced line beginning with a hash, and the anchoring loop needs that
    distinction to stay the caller's explicit test.
    """
    return hkey(raw) == hkey(rendered)
