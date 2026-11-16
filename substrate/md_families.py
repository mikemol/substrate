# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Discover candidate label families in a corpus — never match a known vocabulary.

⚑⚑⚑ THIS EXISTS BECAUSE THE LABEL GRAMMAR HAS BEEN WIDENED FOUR TIMES, EACH TIME TO THE FAMILY IN
FRONT OF THE AUTHOR, AND EACH WIDENING PASSED ON EVERYTHING EXCEPT THE NEXT CASE. All four are
recorded: circled glyphs invisible while a document was STRUCTURED by them; a "fix" that invented
`TL-1` labels the pattern also could not read; two enclosed-digit rows missing from a selector
table; and a new dingbat family reporting ZERO while the retired glyphs quoted in its own
retirement note still resolved.

⚑⚑ SO A FIFTH GUESSED VOCABULARY WOULD BE THE FIFTH INSTANCE, NOT A FIX. A label census answers
*where is label X* against a declared grammar; this answers the prior question the grammar cannot
ask: **what shapes in this corpus are BEING USED as labels, including ones no grammar knows.** It
reports candidates for judgement and deliberately does not decide.

⚑ THE METHOD IS POSITION, NOT SPELLING. A token is a candidate when it sits where a label sits —
leading a line, bracketed, or immediately before an em-dash or colon — and candidates are clustered
by SHAPE rather than by value. Shape is derived per character (upper, lower, digit, the punctuation
itself, or the UNICODE BLOCK NAME for anything non-ASCII), then runs are collapsed, so `T13` and
`R7b` share one shape while an unfamiliar glyph is reported by its block — which is how a family
nobody has seen becomes visible instead of invisible.

⚑⚑ AND `read` IS THE CONTROL, NOT THE FINDING. It marks which candidates the CURRENT grammar
already matches, so the output separates *seen and matched* from *seen and UNREADABLE*. The second
column is the finding; the first is what proves the scan works at all — without it, an empty
unreadable column cannot be told from a scan that found nothing.

⚑⚑⚑ IT TAKES TEXTS, NOT PATHS. The origin opened every file, so the shape function — the part that
decides whether two tokens are one family — could only be exercised against a corpus. A case can
now state `T13` and `R7b` share a shape and a circled glyph does not, which is exactly the
distinction four widenings kept getting wrong.
"""

from __future__ import annotations

import re
import unicodedata
from typing import TYPE_CHECKING, NamedTuple

from mikemol.mdstruct import labels as md_labels

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

#: The closing bracket a label may sit before, in its fullwidth spelling. Named because the literal
#: is confusable with the ASCII form and this repo's own linter flags it as such.
FULLWIDTH_CLOSE = "\N{FULLWIDTH RIGHT PARENTHESIS}"

#: A token in LABEL POSITION: leading a line, bracketed, or before an em-dash or colon.
POSITION = re.compile(
    r"(?:^\s*[-*|]?\s*|\(|\[|\|\s*)(\S{1,24}?)"
    r"(?=\s*(?:[—:" + FULLWIDTH_CLOSE + r"\]|]|\s+—|\s*$))",
    re.MULTILINE,
)

#: Decoration a label may be wrapped in, stripped before the shape is taken.
#:
#: ⚑⚑ THE BRACKETS ARE HERE BECAUSE THE ORIGIN OMITTED THEM AND A CASE CAUGHT IT. The position
#: pattern admits a bracketed token, and the origin then stripped `*`_.,;` only — so `[T13]` became
#: the token `[T13`, whose shape carries a leading `[` and lands in a family of its own. A reader
#: bracketing its labels would see every one of them clustered away from the same labels written
#: bare, which is the opposite of what a discovery census is for.
DECORATION = "*`_.,;[]()"

#: The top of the ASCII range. A codepoint above it is non-ASCII and therefore possibly a glyph
#: family the grammar has never seen.
ASCII_TOP = 127

#: The longest a label candidate may be. Beyond this it is prose that happened to sit in position.
MAX_LENGTH = 24

#: How many distinct examples a family carries. Enough to recognise the shape, few enough to read.
EXAMPLES = 6


class Family(NamedTuple):
    """One candidate label shape, its examples, and whether the grammar reads it.

    ⚑ `read` AND `uses` ANSWER DIFFERENT QUESTIONS. A shape seen four hundred times and unread is
    a grammar gap; a shape seen twice and read is noise the grammar already handles. Collapsing
    them to one number loses exactly the distinction the census exists to draw.

    ⚑⚑ AND THE FIELD IS `uses`, NOT `count`, BECAUSE `NamedTuple` INHERITS `tuple.count`. Naming it
    `count` shadows a method and mypy refuses the assignment — the identical collision that made
    `table_read.Table` name its first field `position`.
    """

    shape: str
    examples: tuple[str, ...]
    uses: int
    files: int
    read: bool

    def why(self) -> str:
        """Return a one-line account naming the shape, its reach and its readability."""
        state = "READ by the grammar" if self.read else "UNREADABLE — no grammar matches it"
        return (
            f"{self.shape}: {self.uses} use(s) in {self.files} file(s), "
            f"e.g. {list(self.examples)} — {state}"
        )


def _char_shape(ch: str) -> str:
    """Return one character's shape class.

    ⚑ A NON-ASCII CHARACTER IS REPORTED BY ITS UNICODE BLOCK, which is the whole discovery
    mechanism: an unfamiliar glyph becomes a NAMED shape rather than an unmatched byte, so a family
    nobody has seen still clusters with its siblings.
    """
    if ch.isascii():
        if ch.isupper():
            return "A"
        if ch.islower():
            return "a"
        if ch.isdigit():
            return "9"
        return ch
    try:
        block = unicodedata.name(ch).split()[0]
    except ValueError:
        return f"<U{ord(ch):04X}>"
    return f"<{block}>"


def shape(token: str) -> str:
    """Return `token`'s shape, with runs collapsed so siblings share one key.

    ⚑ COLLAPSING RUNS IS WHAT MAKES `T13` AND `R7b` ONE FAMILY. Without it every arity is its own
    shape and the census reports a hundred singletons, which is a census nobody reads.
    """
    out: list[str] = []
    for ch in token:
        cls = _char_shape(ch)
        if not out or cls != out[-1]:
            out.append(cls)
    return "".join(out)


def _candidate(token: str) -> str | None:
    """Return the cleaned token when it could be a label, or None.

    ⚑ BARE NUMERALS AND LOWERCASE WORDS ARE NOT LABELS, and excluding them is what keeps a prose
    corpus from reporting every sentence-leading word as a family.
    """
    cleaned = token.strip(DECORATION)
    if not cleaned or len(cleaned) > MAX_LENGTH:
        return None
    if cleaned in md_labels.NON_LABELS:
        return None
    if not any(c.isalnum() or ord(c) > ASCII_TOP for c in cleaned):
        return None
    if cleaned.isdigit() or (cleaned.isascii() and cleaned.islower()):
        return None
    return cleaned


def candidates(text: str) -> list[str]:
    """Return every token in `text` that sits in label position and could be a label."""
    out: list[str] = []
    for match in POSITION.finditer(text):
        token: str = match.group(1)
        cleaned = _candidate(token)
        if cleaned is not None:
            out.append(cleaned)
    return out


def _order(family: Family) -> tuple[int, int, str]:
    """Return the sort key — widest spread first, then most used, then the shape."""
    return (-family.files, -family.uses, family.shape)


def families(texts: Iterable[str], known: re.Pattern[str] | None = None) -> list[Family]:
    """Return every candidate family across `texts`, widest spread first.

    ⚑⚑ `files` COUNTS DOCUMENTS, NOT USES, and the two are different evidence. A shape appearing
    four hundred times in ONE file is one author's local notation; the same shape across a dozen
    files is a vocabulary — and a label is a SHARED thing, so spread is the stronger signal.
    """
    grammar = known if known is not None else md_labels.ITEM_RE
    seen: dict[str, list[str]] = {}
    uses: dict[str, int] = {}
    spread: dict[str, int] = {}
    readable: dict[str, bool] = {}

    for text in texts:
        here: set[str] = set()
        for token in candidates(text):
            key = shape(token)
            uses[key] = uses.get(key, 0) + 1
            readable.setdefault(key, bool(grammar.search(token)))
            examples = seen.setdefault(key, [])
            if token not in examples and len(examples) < EXAMPLES:
                examples.append(token)
            if key not in here:
                spread[key] = spread.get(key, 0) + 1
                here.add(key)

    rows = [Family(key, tuple(seen[key]), uses[key], spread[key], readable[key]) for key in uses]
    return sorted(rows, key=_order)


def unreadable(rows: Sequence[Family]) -> list[Family]:
    """Return only the families the current grammar does not match — the finding.

    ⚑ AN EMPTY RESULT HERE IS ONLY MEANINGFUL BESIDE A NON-EMPTY `rows`. Zero unreadable families
    from a scan that found nothing at all is a fact about the scan, which is why the caller keeps
    both.
    """
    return [row for row in rows if not row.read]
