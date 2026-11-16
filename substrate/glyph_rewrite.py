# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Rewrite a file's checker-flagged characters as named escapes, verifying the round trip.

⚑⚑⚑ THE TRANSFORMATION MUST BE PERFORMED BY A PROGRAM, WHICH IS THE WHOLE POINT. The content
this moves is dense hand-authored mathematical prose, and applying nineteen substitutions across
it by hand is precisely the reassembling-writer risk the tooling exists to remove — a peer
measured that class this week, silently destroying three prose comments while their parse guard
passed because the result was still valid, merely shorter.

⚑⚑ AND THE SET COMES FROM THE CHECKER, NOT THE CALLER. `glyph_flagged` reads which characters
ruff objects to out of its own findings; an authored set was measured wrong in both directions
(gate-G205), holding seven where the checker names nineteen — missing the multiplication sign,
the minus sign, the en dash and logical or, none of which look like Latin letters but all of
which ruff flags as confusable.

⚑⚑⚑ THE ROUND TRIP IS VERIFIED BEFORE ANYTHING IS WRITTEN, and the verdict carries its
components (gate-G204). What must be preserved is what the escaped SOURCE evaluates to, so the
check decodes the rewritten text through the interpreter's own escape reading and compares. A
divergence names its index and both sides; a pass names how much source it produced. A rewrite
that could only report success would be a complaint generator, not a proof.

⚑ AND ONLY STRING LITERALS ARE ELIGIBLE, WHICH IS A BOUND THIS MODULE DOES NOT ENFORCE AND MUST
SAY SO. A named escape means the character only inside a string; the same spelling in a COMMENT
is literal backslash-N text and would corrupt the comment into noise. This module rewrites what
it is given, so the caller owes it a region that is entirely string content — and the round-trip
check cannot catch that error, because both sides decode identically.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from substrate import glyph_escape

if TYPE_CHECKING:
    from pathlib import Path


class Rewrite(NamedTuple):
    """The outcome of one file rewrite, carrying what decided it.

    ⚑ `ok` IS DERIVED, NEVER STORED. A record holding both a verdict and its evidence lets the
    two disagree, which is how a green flag outlives the fact it summarised.
    """

    text: str
    rewritten: str
    trip: glyph_escape.Trip
    chars: frozenset[str]

    @property
    def ok(self) -> bool:
        """Report whether the rewrite round-trips to the original text."""
        return self.trip.ok

    @property
    def changed(self) -> bool:
        """Report whether the rewrite actually altered the source.

        ⚑ AN UNCHANGED REWRITE ROUND-TRIPS PERFECTLY AND CLEARS NOTHING, so a caller asserting
        only `ok` would accept a no-op. This is the component that separates them.
        """
        return self.rewritten != self.text

    def why(self) -> str:
        """Return a one-line account naming the components rather than a bare verdict."""
        moved = sorted(c for c in self.chars if c in self.text)
        return (
            f"{len(moved)} of {len(self.chars)} flagged char(s) present; "
            f"{len(self.text)} -> {len(self.rewritten)} chars; "
            f"changed={self.changed}; {self.trip.why()}"
        )


def rewrite(text: str, chars: frozenset[str]) -> Rewrite:
    """Return `text` with `chars` escaped, plus the round-trip verdict for that rewrite.

    ⚑ THE VERDICT IS COMPUTED ON THE SAME TEXT THAT IS RETURNED. Escaping once for the caller
    and again for the check would let the two diverge under any future non-determinism, and the
    check would then be verifying something nobody ships.
    """
    escaped = glyph_escape.escape_chars(text, chars)
    return Rewrite(text, escaped, glyph_escape.round_trip(text, chars), chars)


def rewrite_file(path: Path, chars: frozenset[str], *, apply: bool = False) -> Rewrite:
    """Rewrite `path` in place under `apply`, refusing to write a rewrite that does not verify.

    ⚑⚑ A FAILING ROUND TRIP IS NEVER WRITTEN. That is the one hard rule here: the escaped source
    is only sound if it evaluates back to the original, and writing an unverified rewrite over a
    hand-authored record is the unrecoverable direction.

    ⚑ AND `apply` IS EXPLICIT WITH NO DEFAULT. A mutating tool must not guess — default-dry
    silently does nothing when you meant to write, default-apply silently writes when you meant
    to look.
    """
    found = rewrite(path.read_text(encoding="utf-8"), chars)
    if apply and found.ok:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(found.rewritten, encoding="utf-8")
        tmp.replace(path)
    return found
