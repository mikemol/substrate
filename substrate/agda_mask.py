# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Blank every Agda comment character, preserving length and line structure.

⚑⚑⚑ THIS IS THE AUTHORITY A LONG CHAIN OF GATES RESTS ON, AND IT HAS NO PACKAGED HOME.
`scratch/agda_lex.mask_comments` is reached from 91 BARE import sites across 63 files with ZERO
dotted ones (`module_importers agda_lex`) — four pre-commit gates and eight tests among them. A
bare site resolves only under a `sys.path` insert, which this tree forbids, so the single most
shared reader in the corpus is unimportable from any packaged consumer. That is what blocks the
`law_motif_apex` drain two levels up (gate-F66, gate-F67).

⚑⚑ THE CORRECTNESS HALF IS SEPARABLE FROM THE CACHING HALF, AND ONLY THIS HALF IS PORTABLE. The
origin carries an `lru_cache` L1 and a shared-store L2 with measured call counts — real
engineering that belongs to a process that masks tens of thousands of times. What a CONSUMER
needs is the mask itself: pure `str -> str`, no imports, no network, no state. Lifting the pure
function leaves the caching where it was measured rather than re-deriving a cache nobody asked
this module for.

⚑⚑⚑ AND THE ALGORITHM IS A REPAIRED DEFECT, WHICH IS WHY IT MUST NOT BE REWRITTEN FROM MEMORY.
The origin records that a codemod once consolidated fifteen copies onto the WEAKER stripper, and
nineteen importers inherited both its bugs — three of them pre-commit gates:

  * `\{-.*?-\}` is NON-GREEDY, so it stops at the FIRST `-}`. Agda block comments NEST, so
    `{- x {- y -} z -}` left `z -}` as live text and every consumer censused commented-out code
    as real.
  * `--[^\n]*` fires anywhere, but Agda's lexer reads `-->` as a NAME, so an operator containing
    `--` was silently eaten.

Both are cased. A reimplementation that looked right would reintroduce exactly these.

⚑ LENGTH PRESERVATION IS LOAD-BEARING, NOT COSMETIC. Callers index by line and some by column,
so a length-preserving mask is a drop-in for `src` everywhere. A masker that DELETED comments
would shift every offset after the first one — the measured shape that erased 533 comment lines
from a live bib in a different tool.

⚑ STRING LITERALS ARE NOT MASKED, and that is declared rather than assumed. Agda strings cannot
span lines and the corpus has no `"…"` containing `--`; stating it keeps the bound visible
instead of leaving a reader to discover it.
"""

from __future__ import annotations

# ⚑ THE OPENER IS CONSERVATIVE BY DESIGN. `--` opens a comment only at line start or after
# whitespace, and only when what follows cannot make it a name. Erring toward KEEPING text means
# a false negative (a comment read as code), which is the safe direction for every consumer here:
# a kept dead import is visible, a silently eaten operator is not.
_BEFORE = " \t\n"

#: What may follow `--` and still open a comment. A further `-` keeps it a comment (`---`),
#: anything else (`>` in `-->`) makes the token a NAME.
_AFTER = " \t\n-"

_TWO = 2


def _block(src: str, out: list[str], i: int, depth: int) -> tuple[int, int]:
    """Advance through one character of a block-comment region: `(index, depth)`.

    ⚑⚑ NESTING IS THE WHOLE POINT. Agda block comments nest, so the depth counter is what
    separates this from the non-greedy regex that shipped for nineteen importers: a nested
    opener must consume to the LAST closer, not the first.
    """
    if src.startswith("{-", i):
        out[i] = out[i + 1] = " "
        return i + _TWO, depth + 1
    if src.startswith("-}", i):
        out[i] = out[i + 1] = " "
        return i + _TWO, depth - 1
    if src[i] != "\n":
        out[i] = " "
    return i + 1, depth


def _line_comment_end(src: str, i: int) -> int:
    """Return where a line comment at `i` ends, or `i` when none opens there.

    ⚑ AN ARROW OPERATOR IS A NAME, NOT A COMMENT. The origin's regex fired on any double hyphen
    and silently ate every operator containing one. The guard is two-sided: what PRECEDES must
    be whitespace or the line start, and what FOLLOWS must not turn the token into a name.
    """
    if not src.startswith("--", i):
        return i
    if i != 0 and src[i - 1] not in _BEFORE:
        return i
    end = src.find("\n", i)
    end = len(src) if end < 0 else end
    if end != i + _TWO and src[i + _TWO] not in _AFTER:
        return i
    return end


def mask_comments(src: str) -> str:
    """Return `src` with every comment character blanked, same length, same line structure.

    ⚑ PURE, SO IT IS SAFE TO CACHE AND SAFE NOT TO. The origin memoises this behind an
    `lru_cache` plus a shared store because one run masked tens of thousands of times; a
    consumer importing it for a handful of files needs neither. Same input, same output, no
    staleness window — which is what makes the origin's caching sound and this copy's absence of
    it harmless.
    """
    out = list(src)
    i = 0
    n = len(src)
    depth = 0
    while i < n:
        if depth == 0 and src.startswith("{-", i):
            out[i] = out[i + 1] = " "
            i += _TWO
            depth = 1
            continue
        if depth:
            i, depth = _block(src, out, i, depth)
            continue
        end = _line_comment_end(src, i)
        if end != i:
            for k in range(i, end):
                out[k] = " "
            i = end
            continue
        i += 1
    return "".join(out)
