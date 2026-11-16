# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Rewrite confusable characters in a Python string literal as NAMED escapes.

⚑⚑⚑ THE PROBLEM THIS SOLVES IS A CONFLICT, NOT A DEFECT (gate-G203). Moving hand-authored
mathematical records between files carries their lint debt with them: ruff's `RUF001`/`RUF002`
flag every glyph that RESEMBLES a Latin letter — the double-struck Z, the DIVIDES sign, a Greek
capital iota — and in a corpus whose subject is mathematics those glyphs ARE the content. So
"carry it verbatim" and "land it clean" cannot both hold, and the operator ruled for named
escapes over a per-file ignore: the roster stays clean by construction, with no exemption.

⚑⚑ A NAMED ESCAPE PRESERVES THE CHARACTER EXACTLY, which is why this is a transcription rather
than an edit. `\N{DOUBLE-STRUCK CAPITAL Z}` and the literal glyph it names are the same character
to every reader of the resulting string — the rendered output is byte-identical, only the SOURCE
spelling changes. That is the property `round_trip` checks, and it is what makes a mechanical
pass safe where hand-retyping dense records would not be.

⚑⚑⚑ AND THE CHECK ITSELF WAS WRONG UNTIL THE REAL CORPUS REFUTED IT (gate-G212). A first cut
verified by decoding the escaped source with `unicode_escape` — which decodes EVERY backslash
sequence, not only the ones this module writes. The live roster carries a pre-existing escaped
quote, so the decode turned it into a bare quote and the verdict reported a DIVERGENCE that was
entirely the verifier's. **And the suite read 22/22 against that verifier**, because every fixture
was backslash-free: a verification passing on inputs its author chose while failing on the corpus
it was built for. The check now INVERTS ONLY WHAT IT WROTE — each `\N{NAME}` this module emitted
is mapped back to its character — so a backslash it did not write is never touched.

⚑⚑⚑ AND THIS MODULE'S OWN DOCSTRING WAS REFUSED BY THE RULE IT EXISTS TO SATISFY, which is the
honest test of the remedy: a first draft quoted the glyph directly to explain itself and was
flagged for exactly that character. The explanation now names the character instead of showing
it — which is what the escape does, one layer up.

⚑⚑ ONLY THE FLAGGED CHARACTERS MOVE, AND THAT BOUND IS THE WHOLE SAFETY ARGUMENT. This does not
normalise, reflow, or re-emit; it replaces individual characters and leaves every other byte
untouched. A pass that rewrote whole literals would be the reassembling-writer class a peer
measured this week — their guard passed because the result was still valid, merely shorter.

⚑ THE ROSTER IS DERIVED FROM THE CHECKER'S OWN VERDICT, NOT GUESSED. `ruff` names the character
it objects to in each finding, so the set to escape is whatever it flags — a hand-written list of
"probably confusable" glyphs would be a second authority that drifts from the rule it serves, and
would escape characters nobody objects to while missing the ones that matter.

⚑⚑⚑ AND THE VERDICT CARRIES ITS COMPONENTS, WHICH IS AN OPERATOR RULING RATHER THAN A STYLE:
*anywhere you assert an expression, you must print the expression's components — that makes it a
[dis]proof-carrying artifact.* A first cut of `round_trip` returned a bare boolean, so a caller
asserting on it learned only NOT EQUAL and nothing about where or how. `Trip` therefore carries
the escaped source, the decoded text, and the first differing position — a failure that can be
read is a disproof; a failure that cannot is only a complaint.
"""

from __future__ import annotations

import unicodedata
from typing import NamedTuple


class Trip(NamedTuple):
    """A round-trip verdict WITH the components that decide it.

    ⚑ `ok` IS DERIVED FROM THE OTHER FIELDS, NEVER STORED SEPARATELY. A record carrying both a
    verdict and its evidence lets the two disagree, which is the shape where a green flag outlives
    the fact it summarised.
    """

    text: str
    escaped: str
    decoded: str | None
    at: int | None

    @property
    def ok(self) -> bool:
        """Report whether the escaped source decodes back to the original text."""
        return self.decoded == self.text

    def why(self) -> str:
        """Return a one-line account of the verdict, naming the components.

        ⚑ THE FAILING CASE PRINTS THE DIVERGENCE POINT AND BOTH SIDES OF IT. A message that said
        only *did not round-trip* would leave the reader to re-derive the comparison this
        function already made.
        """
        if self.decoded is None:
            return f"UNDECODABLE — the escaped source is not valid: {self.escaped[:60]!r}"
        if self.ok:
            return (
                f"round-trips — {len(self.text)} char(s) in, "
                f"{len(self.escaped)} char(s) of source, decoded equal"
            )
        at = self.at if self.at is not None else 0
        return (
            f"DIVERGES at index {at}: original {self.text[at : at + 20]!r} "
            f"vs decoded {self.decoded[at : at + 20]!r}"
        )


def escape_name(char: str) -> str | None:
    r"""Return the `\N{...}` spelling of `char`, or None when it has no Unicode name.

    ⚑ A CHARACTER WITHOUT A NAME CANNOT BE ESCAPED THIS WAY, and returning None rather than a
    fallback is what stops a silent corruption: `unicodedata.name` raises for unnamed codepoints,
    and a caller that swallowed that would emit an empty escape that does not parse.
    """
    try:
        return f"\\N{{{unicodedata.name(char)}}}"
    except ValueError:
        return None


def escape_chars(text: str, chars: frozenset[str]) -> str:
    """Return `text` with every character in `chars` replaced by its named escape.

    ⚑⚑ EVERY OTHER BYTE IS UNTOUCHED. This walks the string once and substitutes individual
    characters, so whitespace, quoting, line structure and every unflagged glyph survive exactly.
    A character whose name cannot be resolved is LEFT AS IT IS rather than dropped — an
    unescapable glyph is a finding for the caller, never a licence to lose it.
    """
    return "".join(escape_name(c) or c if c in chars else c for c in text)


def unescape_chars(source: str, chars: frozenset[str]) -> str:
    r"""Return `source` with the escapes for `chars` mapped back to their characters.

    ⚑⚑⚑ THE INVERSE OF `escape_chars`, AND DELIBERATELY NOTHING MORE (gate-G212). A general
    decoder — `unicode_escape` — resolves EVERY backslash sequence, including ones this module
    never wrote, so an input carrying a pre-existing escaped quote came back with that quote
    unescaped and the round trip reported a divergence that was the verifier's own. Mapping only
    the escapes this module emits makes the check blind to backslashes it did not write, which is
    exactly the property a verifier of a targeted transformation needs.

    ⚑ AND IT IS NOT A PARSER. It performs the same substitution table in reverse, so it is correct
    precisely to the extent `escape_chars` is — which is the honest bound: this verifies the
    transformation against itself, and what makes that non-vacuous is that the two directions are
    written separately and a fixture carries a backslash the escaper never produces.
    """
    out = source
    for char in chars:
        escaped = escape_name(char)
        if escaped is not None:
            out = out.replace(escaped, char)
    return out


def unescapable(chars: frozenset[str]) -> frozenset[str]:
    """Return the members of `chars` this module cannot name.

    ⚑ THE CALLER MUST BE ABLE TO ASK BEFORE WRITING. A pass that discovered mid-transformation
    that one glyph is unnameable would have already rewritten the rest, so the honest shape is a
    question answerable up front — and a non-empty answer means the escape route does not close
    the findings and the caller needs the other remedy.
    """
    return frozenset(c for c in chars if escape_name(c) is None)


def first_difference(left: str, right: str) -> int | None:
    """Return the first index at which two strings differ, or None when they are equal.

    ⚑ THIS IS THE COMPONENT A VERDICT NEEDS TO BE READABLE. Equal-length inequality says nothing
    about where; the index turns a refusal into a location a reader can open.
    """
    for i, (a, b) in enumerate(zip(left, right, strict=False)):
        if a != b:
            return i
    return None if left == right else min(len(left), len(right))


def round_trip(text: str, chars: frozenset[str]) -> Trip:
    r"""Return the round-trip verdict for `text` under `chars`, carrying its components.

    ⚑⚑⚑ THIS IS THE PROPERTY THE WHOLE MODULE RESTS ON, so it is exposed as a function a caller
    can run on real content rather than left as a claim in a docstring. The escaped form is
    SOURCE; what must be preserved is what that source EVALUATES to. Checking the two are equal
    is the only thing that distinguishes a faithful transcription from a plausible one.

    ⚑⚑ AND IT INVERTS ONLY THIS MODULE'S OWN ESCAPES (gate-G212). Decoding the whole string with
    a general escape decoder resolved backslashes the escaper never wrote, so the real corpus —
    which carries a pre-existing escaped quote — reported a divergence that was entirely the
    verifier's. A targeted transformation needs a targeted inverse.
    """
    escaped = escape_chars(text, chars)
    decoded = unescape_chars(escaped, chars)
    return Trip(text, escaped, decoded, first_difference(text, decoded))
