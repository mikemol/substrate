#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Measured numbers written into a python STRING LITERAL — prose sitting in a data position.

⚑⚑⚑ THIS IS `prose_numbers`' DECLARED BLIND SPOT, AND THE INSTANCE THAT MOTIVATED THAT READER
LIVED INSIDE IT. `code_lines` calls a data string CODE — correctly, because it IS code — so a
count written into a table's `why=` field is invisible there. The measured case: an entry in
`suite_declared.py` claimed a case count its own suite contradicted, and `prose_numbers` found
that file's drifted counts in its COMMENTS while staying silent on the one in its DATA. The
reader was pointed at a file and reported everything about it except the thing it was built for.

⚑⚑ SO THE NEW JUDGEMENT IS NOT *is this number a measurement* — that is `prose_numbers`'
question and it is answered there, once, with its exemptions and its cases. Re-deriving it here
would mint a second authority for one predicate, which is the `agda_files()`-had-four-bodies
shape this toolkit has already paid for. What is NEW is *is this STRING prose*, and that is the
whole deliverable.

⚑⚑⚑ AND THAT DISCRIMINATOR IS HARDER THAN THE PROSE ONE, because a string literal may be data
the program USES. A `why=` field, an explanatory message, a docstring-like note — prose in a
data position, in scope. A format string, a SQL fragment, a regex, a test fixture's expected
output — the number is the program's BUSINESS, out of scope, and flagging it would be worse than
useless: a reader that reports a fixture's expected value trains its reader to skim, and it
would fire on the very suites that keep this tree honest.

⚑⚑ THE MENTION/USE DISTINCTION IS GENUINELY CLEANER HERE THAN IN PROSE, which is the one place
this reader can do better than its sibling. `prose_numbers` reports an UPPER BOUND because a
quoted specimen and a claim are both just a number beside a noun. A `why=` field is different in
kind: it is a CLAIM the table makes about the world, in a named field, addressed to a reader —
never a specimen the program manipulates. So a hit in a KEYWORD-NAMED explanatory field is a
claim by construction, and this reader says so rather than hedging uniformly.

⚑ IT IS STILL AN UPPER BOUND OUTSIDE THAT, and the census marks which is which rather than
averaging them. An explanatory string that happens to quote a tool's output is a mention, and
nothing structural separates it from an assertion.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from substrate import corpus, prose_numbers

#: ⚑⚑⚑ THE KEYWORDS WHOSE VALUE IS AN EXPLANATION ADDRESSED TO A READER. A number here is a
#: CLAIM, not a specimen: the field's whole purpose is to say something true about the world,
#: and nothing in the program consumes the number.
#:
#: ⚑ THIS IS WHERE THE MOTIVATING INSTANCE LIVES. `suite_declared.Declared.why` is exactly this
#: shape, and it carried a case count its own suite contradicted.
#:
#: ⚑⚑ A CONSTANT A CALLER CAN WIDEN, for the reason the struct-tools rule records: a hardcoded
#: vocabulary rots, and this tooling is read by repos whose fields have other names. A miss is
#: "no entry carries that spelling", never "no measured number exists".
PROSE_KEYWORDS: frozenset[str] = frozenset(
    {
        "why",
        "reason",
        "rationale",
        "note",
        "notes",
        "explanation",
        "detail",
        "description",
        "desc",
        "comment",
        "doc",
        "docs",
        "help",
        "summary",
        "message",
        "msg",
        "gloss",
        "because",
        "caveat",
        "warning",
    }
)

#: ⚑⚑⚑ ASSIGNMENT TARGETS WHOSE VALUE IS PROSE. The same judgement one syntactic step over: a
#: module-level `_WHY = "..."` or a `self.reason = "..."` is the same act as the keyword form,
#: and keying only on keywords would report the shape as absent wherever the author used a
#: variable — the census-keyed-on-one-spelling defect this repo has already banked twice.
PROSE_NAMES: frozenset[str] = frozenset(
    {name.upper() for name in PROSE_KEYWORDS}
    | PROSE_KEYWORDS
    | {f"_{name}" for name in PROSE_KEYWORDS}
)

#: ⚑⚑⚑ THE OUT-OF-SCOPE SHAPES. Each is a string whose NUMBER IS THE PROGRAM'S BUSINESS, and
#: each was chosen because flagging it would make this reader useless. A format string's number
#: is a width; a SQL fragment's is a limit; a regex's is a repetition count; a fixture's is the
#: value under test. None of them drifts against a tool, because none of them is a claim.
_FORMAT_MARKS = ("{", "%s", "%d", "%r", "%(")

#: A SQL fragment — the number is a limit, an offset or a column width the query needs.
_SQL_MARKS = (
    "SELECT ",
    "INSERT ",
    "UPDATE ",
    "DELETE ",
    "CREATE ",
    "ALTER ",
    " FROM ",
    " WHERE ",
    " JOIN ",
    "LIMIT ",
    "OFFSET ",
)

#: A regex — the number is a repetition count or a character class bound.
_REGEX_MARKS = ("\\d", "\\w", "\\s", "[0-9]", "(?:", "(?<", "(?=", ".*", ".+")


@dataclass(frozen=True, slots=True)
class Finding:
    """One measured number written into a string literal the program does not consume."""

    path: str
    line: int
    number: str
    unit: str
    text: str
    #: Which position made this string prose: `keyword` (a `why=`-shaped field), `name` (an
    #: explanatory assignment target), or `docstring-like` (a bare explanatory string).
    position: str
    #: ⚑ WHETHER THIS IS A CLAIM OR ONLY A MENTION — the distinction `prose_numbers` cannot
    #: draw. A named explanatory FIELD is addressed to a reader and asserts; anything else is
    #: reported as an upper-bound mention.
    claim: bool


@dataclass(frozen=True, slots=True)
class Skipped:
    """One string literal the discriminator REFUSED, and the rule that refused it.

    ⚑ THE REFUSALS ARE RETURNED, NEVER DISCARDED. A discriminator reporting only its hits
    cannot be audited: an over-eager rule looks exactly like a clean tree, and over-refusal is
    invisible in the census by construction.
    """

    path: str
    line: int
    text: str
    why: str


#: ⚑⚑⚑ WHAT THIS READER CANNOT SEE. Declared as DATA so it prints with every census.
BOUNDARIES: tuple[str, ...] = (
    (
        "⚑ A STRING BUILT AT RUNTIME is invisible — a concatenation, an f-string's computed part, "
        "a value read from a file. This reads LITERALS in the AST, so a claim assembled from "
        "pieces is outside it by construction"
    ),
    (
        "⚑ AN EXPLANATORY STRING IN A POSITION NOBODY NAMED reads as out of scope. A miss is 'no "
        "entry carries that spelling', never 'no measured number' — widen `PROSE_KEYWORDS` or "
        "`PROSE_NAMES` rather than reading a small census as a clean tree"
    ),
    (
        "⚑ A CLAIM THAT IS STILL TRUE is indistinguishable from a drifted one. This reports that a "
        "measurement was WRITTEN INTO DATA, never whether it has drifted; only re-running the tool "
        "that owns the figure can say, and no reader here does that"
    ),
    (
        "a number inside a string this reader calls prose but the program actually PARSES — a "
        "config default, a schema hint. The position says who the string is addressed to, not what "
        "downstream code does with it"
    ),
    (
        "⚑ OUTSIDE A NAMED EXPLANATORY FIELD this is an UPPER BOUND, exactly as `prose_numbers` "
        "reports. A bare explanatory string quoting a tool's output is a MENTION, and nothing "
        "structural separates it from an assertion. Inside such a field it IS a claim — a `why=` "
        "is addressed to a reader and asserts, which is the one place the mention/use line is "
        "cleaner in data than in prose"
    ),
    (
        "the measurement judgement itself is `prose_numbers`' and inherits ALL of its boundaries — "
        "a count spelled in words, a unit noun outside its lexicon, a stale-but-correct figure"
    ),
    (
        "prose in any artifact but `.py` — a TSV ledger or a JSON fixture carries claims in data "
        "positions too, and no corpus here extracts them"
    ),
)


def refusal_for(text: str) -> str | None:
    """Return the rule refusing this string, or None when its number could be a claim.

    ⚑⚑⚑ THE NEGATIVE HALF IS THE DELIVERABLE, and each rule names a shape whose number the
    PROGRAM owns. A reader flagging a format width, a SQL limit or a regex repetition is
    reporting the program's own arithmetic back at its author — and it would fire hardest on the
    suites and query builders that are most correct, which is the anti-signal.

    ⚑⚑ THE ORDER IS LOAD-BEARING AND A CASE CAUGHT IT WRONG. A regex repetition like a braced
    count also contains a brace, so a format-first walk attributed every regex to the FORMAT
    rule. Both refuse, so the census TOTAL was right while the per-rule tally — the thing a
    reader consults to spot an over-broad rule — was wrong. The most specific rule is tested
    first, the same first-match-wins discipline `prose_numbers._refusals` records for its own
    overlaps, and for the same reason: double-attribution makes the shares unreadable.
    """
    if any(mark in text for mark in _REGEX_MARKS):
        return "a regex — the number is a repetition count or a class bound"
    upper = text.upper()
    if any(mark in upper for mark in _SQL_MARKS):
        return "a SQL fragment — the number is a limit, an offset or a bound"
    if any(mark in text for mark in _FORMAT_MARKS):
        return "a format string — the number is a width or a placeholder's operand"
    return None


def position_of(node: ast.Constant, parents: dict[int, ast.AST]) -> str | None:
    """Return the position that makes this string prose, or None when it is not in one.

    ⚑⚑ THE POSITION IS THE DISCRIMINATOR, and it answers *who is this string addressed to*. A
    keyword argument named `why` is written for a reader; a positional argument to `format` is
    written for the machine. Nothing about the string's TEXT separates those — only where it
    sits, which is why this is a syntactic question rather than a lexical one.

    ⚑ A KEYWORD BEATS A NAME BEATS A BARE STRING, because the more specific position is the
    stronger evidence about the audience, and a string in two positions at once cannot exist.
    """
    parent = parents.get(id(node))
    if isinstance(parent, ast.keyword) and parent.arg in PROSE_KEYWORDS:
        return "keyword"
    if isinstance(parent, ast.Assign):
        names = [t.id for t in parent.targets if isinstance(t, ast.Name)]
        names += [t.attr for t in parent.targets if isinstance(t, ast.Attribute)]
        if any(n in PROSE_NAMES for n in names):
            return "name"
    if isinstance(parent, ast.AnnAssign):
        target = parent.target
        if isinstance(target, ast.Name) and target.id in PROSE_NAMES:
            return "name"
    return None


def _parents(tree: ast.AST) -> dict[int, ast.AST]:
    """Return a child-id to parent map — the edge a bare `ast.walk` discards.

    ⚑ THE FACT IS AN EDGE, NOT A PROPERTY. Whether a string is prose is not readable from the
    string node alone; it is a fact about the node's RELATION to its parent. A per-node walk
    reports its own boundary as the subject's, which is why the map is built rather than
    approximated by re-scanning text.
    """
    out: dict[int, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            out[id(child)] = parent
    return out


def scan(path: Path) -> tuple[list[Finding], list[Skipped]]:
    """Return the measured numbers in prose-bearing string literals of ONE file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError, ValueError):
        return [], []
    name = str(path)
    parents = _parents(tree)
    found: list[Finding] = []
    refused: list[Skipped] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        text = node.value
        position = position_of(node, parents)
        if position is None:
            continue
        why = refusal_for(text)
        if why is not None:
            refused.append(Skipped(name, node.lineno, text[:120], why))
            continue
        # ⚑ THE MEASUREMENT JUDGEMENT IS `prose_numbers`', CALLED NOT COPIED. One authority for
        # "is this number a measurement", with its exemptions and its cases; this module owns
        # only the question of whether the STRING is prose.
        hits, _exempt = prose_numbers.scan_line(name, node.lineno, text)
        if not hits:
            refused.append(
                Skipped(
                    name, node.lineno, text[:120], "no measured number (prose_numbers found none)"
                )
            )
            continue
        found.extend(
            Finding(
                name, node.lineno, h.number, h.unit, text[:200], position, position == "keyword"
            )
            for h in hits
        )
    return found, refused


def census(*requested: str, root: Path) -> tuple[list[Finding], list[Skipped], int]:
    """Return `(findings, skipped, files_read)` over the `.py` under `requested` in the tree `root`.

    ⚑ `root` IS REQUIRED (2026-09-24, no-ROOT rule); it defaulted to `corpus.ROOT`.

    ⚑ `files_read` IS RETURNED BECAUSE A BARE LIST CANNOT DISTINGUISH *no matches* FROM *no file
    read* — the house rule every reader in this tree prints.
    """
    found: list[Finding] = []
    refused: list[Skipped] = []
    seen = 0
    for name in corpus.py_files(*requested, root=root):
        seen += 1
        f, s = scan(Path(name))
        found.extend(f)
        refused.extend(s)
    return found, refused, seen


def by_holder(found: list[Finding]) -> list[tuple[str, int]]:
    """Return `(path, n)` per file, largest holder first."""
    counts: dict[str, int] = {}
    for f in found:
        counts[f.path] = counts.get(f.path, 0) + 1

    def rank(kv: tuple[str, int]) -> tuple[int, str]:
        """Order by descending count, then by path so ties are canonical."""
        return (-kv[1], kv[0])

    return sorted(counts.items(), key=rank)
