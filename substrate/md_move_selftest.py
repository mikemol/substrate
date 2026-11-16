#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `substrate.md_move` — the span move and its conservation refusal.

⚑ EVERY ARM IS A DISCRIMINATOR, not a happy path restated. The move's dangerous half is the
EXCISION, which fails silently, so the arms that matter are the ones that would still pass if
the excision took the wrong lines: line-ending preservation, off-by-one at both bounds, and the
absent-from-origin half of conservation. An arm asserting only "the text arrived" passes on a
copy, and a copy is the defect.

⚑⚑ CASES ARE DATA, following `drain_leverage_selftest`'s precedent: a `check(label, got, want)`
helper makes every boolean expectation a positional bool (`FBT003`), while tuple elements carry
the same expectations as values.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import md_move

_DOC = "# Title\n\n## Residue\n\n* alpha\n* beta\n* gamma\n"
_DEST = "# Other\n\n## Residue\n\n* existing\n"

Case = tuple[str, object, object]


def _tmp(text: str, name: str, root: Path) -> Path:
    """Return a path under `root` holding `text`."""
    path = root / name
    path.write_text(text, encoding="utf-8")
    return path


def _cases_span() -> list[Case]:
    """Return the operand-parsing arms."""
    out: list[Case] = [
        ("span parses", md_move.parse_span("5-7"), (5, 7)),
        ("single line", md_move.parse_span("5-5"), (5, 5)),
    ]
    for bad in ("7-5", "0-3", "5", "a-b", "5-"):
        try:
            md_move.parse_span(bad)
            got: object = "accepted"
        except ValueError:
            got = "refused"
        # ⚑ A REVERSED SPAN IS REFUSED, NOT SORTED. Normalising it would move a region the
        # caller did not name, which on a write is a guess at intent.
        out.append((f"refuses {bad!r}", got, "refused"))
    return out


def _cases_excise() -> list[Case]:
    """Return the excision arms, including both boundary lines."""
    text = "a\nb\nc\nd\n"
    remaining, removed = md_move.excise(text, 2, 3)
    out: list[Case] = [
        ("excise removes the span", removed, "b\nc\n"),
        ("excise keeps the rest", remaining, "a\nd\n"),
        # ⚑ BOTH BOUNDS ARE INCLUSIVE, pinned separately — an off-by-one at the START and at
        # the END are different defects, and one mid-document arm catches neither reliably.
        ("first line addressable", md_move.excise(text, 1, 1)[1], "a\n"),
        ("last line addressable", md_move.excise(text, 4, 4)[1], "d\n"),
        # ⚑ NO TRAILING NEWLINE IS THE REAL SHAPE OF A FINAL ENTRY, and a keepends-blind
        # implementation invents one here.
        ("preserves a missing final newline", md_move.excise("a\nb", 2, 2)[1], "b"),
    ]
    try:
        md_move.excise(text, 3, 99)
        got: object = "accepted"
    except ValueError:
        got = "refused"
    out.append(("refuses a span past the end", got, "refused"))
    return out


def _cases_move(root: Path) -> list[Case]:
    """Return the end-to-end move arms against real files."""
    src = _tmp(_DOC, "src.md", root)
    dst = _tmp(_DEST, "dst.md", root)
    origin_after, dest_after, moved = md_move.move(src, dst, "Residue", (6, 6))
    return [
        ("the named line moves", moved, "* beta\n"),
        ("destination gains it", "* beta" in dest_after, True),
        # ⚑ THE ABSENT-FROM-ORIGIN ARM IS WHAT SEPARATES A MOVE FROM A COPY. Without it every
        # other arm here passes on an implementation that only appends.
        ("origin loses it", "* beta" in origin_after, False),
        (
            "origin keeps its siblings",
            "* alpha" in origin_after and "* gamma" in origin_after,
            True,
        ),
        ("destination keeps its own", "* existing" in dest_after, True),
        # ⚑ NOTHING IS WRITTEN BY `move`, so a dry run cannot mutate. Asserted rather than
        # assumed, because the whole both-or-neither contract rests on it.
        ("move writes nothing", src.read_text(encoding="utf-8"), _DOC),
    ]


def _cases_refusal(root: Path) -> list[Case]:
    """Return the arms where the move must refuse rather than write."""
    src = _tmp(_DOC, "src2.md", root)
    dst = _tmp(_DEST, "dst2.md", root)
    try:
        md_move.move(src, dst, "Nonexistent", (6, 6))
        got: object = "accepted"
    except LookupError:
        got = "refused"
    # ⚑ THE CONSERVATION CHECK IS EXERCISED DIRECTLY, because no ordinary move reaches it —
    # a predicate with no case is a promise. The duplication arm is the dangerous direction.
    # ⚑⚑ THE TRAILING-BLANK ARM IS A REGRESSION PIN FOR A LIVE DEFECT. The first cut compared
    # bytes, so a span ending on a blank line — the ordinary shape of an entry followed by a
    # separator — was reported as LOST after a successful move, because the destination
    # normalises its tail. It refused correct moves and would have been read as data loss.
    src2 = _tmp(_DOC, "src4.md", root)
    dst2 = _tmp(_DEST, "dst4.md", root)
    blanked = md_move.move(src2, dst2, "Residue", (5, 7))
    # ⚑⚑⚑ THE ALREADY-THERE ARM PINS A HOLE THE POST-CHECK STRUCTURALLY CANNOT SEE. A block the
    # destination already held passes "present afterwards" without the append contributing
    # anything, so a re-run or a `doc_split --part` copy DUPLICATED the entry and reported
    # success. Measured live during Ⓝ133a, not hypothesised.
    src3 = _tmp(_DOC, "src5.md", root)
    dst3 = _tmp(_DEST + "* beta\n", "dst5.md", root)
    try:
        md_move.move(src3, dst3, "Residue", (6, 6))
        dup: object = "accepted"
    except ValueError:
        dup = "refused"
    return [
        ("absent heading refuses", got, "refused"),
        ("a duplicate destination refuses", dup, "refused"),
        ("and the origin is untouched", src3.read_text(encoding="utf-8"), _DOC),
        ("conserved when clean", md_move.unconserved("a\n", "b\n", "b\n"), ""),
        ("catches a failed append", bool(md_move.unconserved("a\n", "x\n", "b\n")), True),
        ("catches a duplication", bool(md_move.unconserved("b\n", "b\n", "b\n")), True),
        (
            "a trailing blank does not read as loss",
            md_move.unconserved("", "* alpha\n* beta\n", "* alpha\n* beta\n\n"),
            "",
        ),
        # ⚑ AND THE COMPLEMENT, so the tolerance did not become blindness: interior content
        # still has to arrive, or the strip would have turned the check off entirely.
        (
            "interior loss still caught",
            bool(md_move.unconserved("", "* alpha\n", "* alpha\n* beta\n")),
            True,
        ),
        ("a span ending on a blank moves", "* gamma" in blanked[1], True),
    ]


def _cases_main(root: Path) -> list[Case]:
    """Return the dispatch arms, exercised through `main` with exit codes."""
    src = _tmp(_DOC, "src3.md", root)
    dst = _tmp(_DEST, "dst3.md", root)
    args = [str(src), str(dst), "Residue"]
    # ⚑ THE REGRESSION PIN GOES THROUGH `main`, not through `move` — `check_dep_addressing`
    # shipped a dropped operand past a green suite whose every case called the reader directly.
    return [
        ("dry run exits 0", md_move.main([*args, "--span", "6-6", "--dry-run"]), 0),
        ("dry run wrote nothing", src.read_text(encoding="utf-8"), _DOC),
        ("neither mode refuses", md_move.main([*args, "--span", "6-6"]), 2),
        ("both modes refuse", md_move.main([*args, "--span", "6-6", "--apply", "--dry-run"]), 2),
        ("missing span refuses", md_move.main([*args, "--dry-run"]), 2),
        ("apply exits 0", md_move.main([*args, "--span", "6-6", "--apply"]), 0),
        ("apply moved it out", "* beta" in src.read_text(encoding="utf-8"), False),
        ("apply moved it in", "* beta" in dst.read_text(encoding="utf-8"), True),
    ]


def _cases_drop(root: Path) -> list[Case]:
    """Return the `--drop` arms — a deletion that requires a witness."""
    src = _tmp(_DOC, "src6.md", root)
    held = _tmp(_DEST + "* beta\n", "dst6.md", root)
    absent = _tmp(_DEST, "dst7.md", root)
    origin_after, dropped = md_move.drop(src, held, (6, 6))
    try:
        # ⚑ THE REFUSAL IS THE WHOLE SAFETY ARGUMENT. Without it `--drop` is an unguarded
        # delete wearing a two-operand signature, and the second operand would be decoration.
        md_move.drop(src, absent, (6, 6))
        lone: object = "accepted"
    except ValueError:
        lone = "refused"
    return [
        ("drop removes the span", dropped, "* beta\n"),
        ("drop keeps the rest", "* beta" in origin_after, False),
        ("drop refuses without a witness", lone, "refused"),
        ("drop writes nothing", src.read_text(encoding="utf-8"), _DOC),
        (
            "drop dispatch exits 0",
            md_move.main(["--drop", str(src), str(held), "--span", "6-6", "--dry-run"]),
            0,
        ),
        (
            "drop dispatch refuses without a witness",
            md_move.main(["--drop", str(src), str(absent), "--span", "6-6", "--dry-run"]),
            2,
        ),
    ]


def selftest() -> int:
    """Run every case and return the number that failed."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        cases = (
            _cases_span()
            + _cases_excise()
            + _cases_move(root)
            + _cases_refusal(root)
            + _cases_main(root)
            + _cases_drop(root)
        )
    bad = 0
    for label, got, want in cases:
        if got != want:
            bad += 1
            sys.stdout.write(f"FAIL {label}: got {got!r}, want {want!r}\n")
    sys.stdout.write(f"{len(cases) - bad}/{len(cases)} md_move case(s) passed\n")
    return bad


if __name__ == "__main__":
    sys.exit(1 if selftest() else 0)
