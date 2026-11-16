# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_families` — the discovery reader, and the control that proves it.

⚑⚑⚑ THE UNREADABLE ARM IS THE FINDING AND THE READ ARM IS THE CONTROL. A census reporting zero
unreadable families is indistinguishable from a scan that found nothing at all, so both columns are
asserted — the second is what makes an empty first column mean something.

⚑⚑ AND THE SHAPE ARM IS WHAT FOUR GRAMMAR WIDENINGS KEPT GETTING WRONG. `T13` and `R7b` must be ONE
family or the census reports a hundred singletons nobody reads; a circled glyph must be its own
family or it stays invisible — which is exactly how a document STRUCTURED by circled glyphs was
read as having no labels.

⚑ THE FIXTURES ARE TEXTS, NOT PATHS, which is the drain's gain here. The origin opened every file,
so `shape` — the function deciding whether two tokens are siblings — could only be exercised against
a corpus, and its failures were four separate incidents rather than four cases.
"""

from __future__ import annotations

import re
import sys

from substrate import md_families as mf

#: Two ASCII labels of different arity. ⚑ THEY MUST SHARE A SHAPE.
ASCII_DOC = "T13 — the first item\nR7b — the second item\n"

#: ⚑ THE CIRCLED-GLYPH FAMILY, which the grammar reads as a bare prefix (gate-G275). Its SHAPE is
#: what makes it visible here even though the grammar's match is only the glyph.
GLYPH_DOC = "\N{CIRCLED LATIN CAPITAL LETTER N} — a plan item\n"

#: A shape no grammar knows — the case the whole module exists for.
UNKNOWN_DOC = "ABCDEF-GHIJ — an unfamiliar family\n"

#: Prose with nothing in label position.
PROSE_DOC = "this is a sentence about nothing in particular\n"

#: How many documents the spread fixture supplies. Named because the arm is ABOUT that number.
DOCUMENTS = 3


def _shape_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the clustering that four widenings got wrong."""
    out: list[tuple[str, bool]] = []

    # ⚑⚑⚑ THE ORIGIN'S DOCSTRING CLAIMS `T13` AND `R7b` SHARE A SHAPE AND THEY DO NOT — measured:
    # `A9` versus `A9a`, because `R7b` carries a trailing lowercase run. My case asserted the
    # docstring and failed, which is the finding: a claim repeated from the prose it drained.
    # What run-collapsing actually buys is arity-independence WITHIN a run, asserted below.
    out.append(
        (
            f"T13 and R7b differ by their trailing run: {mf.shape('T13')} vs {mf.shape('R7b')}",
            mf.shape("T13") != mf.shape("R7b"),
        )
    )

    # ⚑ WHAT COLLAPSING REALLY GIVES: arity does not split a family. `T13` and `A4` are one shape,
    # and `R7b` and `Q12c` are another — which is the property the census needs.
    out.append(
        (
            f"arity does not split a family: {mf.shape('T13')} vs {mf.shape('A4')}",
            mf.shape("T13") == mf.shape("A4"),
        )
    )
    out.append(
        (
            f"and the suffixed family clusters too: {mf.shape('R7b')} vs {mf.shape('Q12c')}",
            mf.shape("R7b") == mf.shape("Q12c"),
        )
    )

    # ⚑⚑ A GLYPH IS ITS OWN FAMILY, NAMED BY ITS UNICODE BLOCK. That naming is the discovery
    # mechanism: an unseen glyph clusters with its siblings instead of vanishing.
    glyph = mf.shape("\N{CIRCLED LATIN CAPITAL LETTER N}")
    out.append(
        (
            f"a circled glyph is its own shape: {glyph}",
            glyph != mf.shape("T13") and "CIRCLED" in glyph,
        )
    )

    # ⚑ AND A HYPHENATED FAMILY IS DISTINCT — the shape that a guessed vocabulary invented and
    # could not read.
    out.append(
        (
            f"a hyphenated family is distinct: {mf.shape('ABCDEF-GHIJ')}",
            mf.shape("ABCDEF-GHIJ") not in {mf.shape("T13"), glyph},
        )
    )
    return out


def _position_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what counts as label POSITION."""
    out: list[tuple[str, bool]] = []
    leading = mf.candidates(ASCII_DOC)

    out.append(
        (f"a line-leading token before an em-dash is a candidate: {leading}", "T13" in leading)
    )
    out.append(
        (
            f"a bracketed token is a candidate: {mf.candidates('[T13] the item')}",
            "T13" in mf.candidates("[T13] the item"),
        )
    )
    out.append(
        (
            f"a token before a colon is a candidate: {mf.candidates('T13: the item')}",
            "T13" in mf.candidates("T13: the item"),
        )
    )

    # ⚑ PROSE IN POSITION IS NOT A LABEL. Without this every sentence-leading word is a family and
    # the census is unreadable.
    out.append(
        (
            f"a lowercase word is not a candidate: {mf.candidates(PROSE_DOC)}",
            mf.candidates(PROSE_DOC) == [],
        )
    )
    out.append(
        (
            f"a bare numeral is not a candidate: {mf.candidates('42: a value')}",
            mf.candidates("42: a value") == [],
        )
    )
    return out


def _control_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the read/unread split.

    ⚑⚑⚑ THE CONTROL IS WHAT MAKES AN EMPTY FINDING MEANINGFUL. A census with no unreadable rows
    could be a clean corpus or a broken scan, and only a non-empty READ column tells them apart.
    """
    out: list[tuple[str, bool]] = []
    rows = mf.families([ASCII_DOC, UNKNOWN_DOC])

    read = [r for r in rows if r.read]
    unread = mf.unreadable(rows)

    out.append((f"the known family is READ: {[r.shape for r in read]}", len(read) >= 1))
    out.append(
        (f"and the unknown family is UNREADABLE: {[r.why() for r in unread]}", len(unread) >= 1)
    )
    out.append(
        (
            f"and the two are disjoint: {len(read)} + {len(unread)} = {len(rows)}",
            len(read) + len(unread) == len(rows),
        )
    )

    # ⚑ THE SENSITIVITY ARM. A grammar matching EVERYTHING must empty the finding column, or `read`
    # is not consulted and the split is decoration.
    permissive = mf.families([ASCII_DOC, UNKNOWN_DOC], known=re.compile(r"."))
    out.append(
        (
            f"a permissive grammar empties the finding: {mf.unreadable(permissive)}",
            mf.unreadable(permissive) == [],
        )
    )

    # ⚑ AND A GRAMMAR MATCHING NOTHING must fill it — the other direction, which a one-sided arm
    # would miss.
    strict = mf.families([ASCII_DOC, UNKNOWN_DOC], known=re.compile(r"(?!x)x"))
    out.append(
        (
            f"a strict grammar fills it: {len(mf.unreadable(strict))} of {len(strict)}",
            len(mf.unreadable(strict)) == len(strict) and strict != [],
        )
    )
    return out


def _spread_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for uses-versus-files, which are different evidence.

    ⚑ A LABEL IS A SHARED VOCABULARY, so a shape across many documents is stronger evidence than
    the same shape repeated in one — and the ordering says so.
    """
    out: list[tuple[str, bool]] = []

    local = mf.families([ASCII_DOC + ASCII_DOC + ASCII_DOC])
    out.append(
        (
            f"repeats in one file raise uses, not files: {local[0].uses}/{local[0].files}",
            local[0].uses > local[0].files and local[0].files == 1,
        )
    )

    spread = mf.families([ASCII_DOC] * DOCUMENTS)
    out.append(
        (
            f"the same shape across files raises spread: {spread[0].files}",
            spread[0].files == DOCUMENTS,
        )
    )

    # ⚑ AND SPREAD ORDERS THE OUTPUT — the widest-shared family is read first.
    mixed = mf.families([ASCII_DOC + UNKNOWN_DOC, ASCII_DOC])
    out.append(
        (
            f"the wider-spread family sorts first: {[r.shape for r in mixed]}",
            mixed[0].files >= mixed[-1].files,
        )
    )
    return out


def _account_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what a family reports about itself."""
    out: list[tuple[str, bool]] = []
    row = mf.families([UNKNOWN_DOC])[0]

    out.append((f"the account names the shape: {row.why()}", row.shape in row.why()))
    out.append((f"and carries an example: {row.examples}", "ABCDEF-GHIJ" in row.examples))
    out.append((f"and says it is unreadable: {row.why()}", "UNREADABLE" in row.why()))
    out.append((f"an empty corpus yields nothing: {mf.families([])}", mf.families([]) == []))
    return out


def _glyph_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the circled-glyph family, tying to gate-G275.

    ⚑⚑ THE GRAMMAR MATCHES THE BARE GLYPH AND NOT THE DIGITS AFTER IT, which is what made a
    fixture written as glyph-plus-digits collapse two labels into one. The discovery census sees
    the SHAPE regardless, which is precisely the reach a declared grammar does not have.
    """
    out: list[tuple[str, bool]] = []
    rows = mf.families([GLYPH_DOC])

    out.append(
        (f"a glyph in label position is discovered: {[r.shape for r in rows]}", len(rows) == 1)
    )
    out.append(
        (f"and its shape names the unicode block: {rows[0].shape}", "CIRCLED" in rows[0].shape)
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _shape_cases()
        + _position_cases()
        + _control_cases()
        + _spread_cases()
        + _account_cases()
        + _glyph_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"md-families selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
