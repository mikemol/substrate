#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Decide which lines of a python source are CODE — not blank, not comment, not docstring.

⚑ TOKENIZE, DO NOT GUESS. A `#` inside a string is not a comment and a triple-quote inside a
comment is not a docstring. `tokenize` already knows both; re-deriving it with a regex is how
the `-->`-is-a-name class got into `agda_lex` — a stripper that was right about the common
case, which is the shape of every stripper that is wrong.

⚑⚑ THE ORIGIN HELD TWO BODIES FOR THIS ONE QUESTION, IN ONE FILE. `_code_lines` tokenized;
`module_size_all`, ninety lines further down, counted with `line.strip() and not
line.lstrip().startswith("#")`. The second reads every line of a docstring as code, so the
most heavily documented modules — the ones whose ⚑ commentary IS the incident log this repo
protects — score worst on the size census built to find bulk. That is the `agda_files()`
four-bodies-one-name defect reproduced inside a single module, and it is why this is promoted
as ONE authority rather than moved twice.

⚑⚑ AND THE ORIGIN'S OWN STRIPPER WAS WRONG IN EXACTLY THAT WAY — measured here, by this
module's own suite, on the first run. It judged a string line by deleting the DELIMITERS with a
regex and testing what remained, so `\"\"\"Summary line.` left the prose behind and counted as
code. Every module docstring's first line was bulk. The fix is not a better regex: `tokenize`
already reports each string token's exact start and end, so a line is non-code when a token
COVERS it. The residue test was a re-derivation of something the tokenizer had already decided.

⚑ A LINE WITH CODE AND A TRAILING COMMENT IS CODE. Dropping it would hide a defect that
happens to carry an explanation — precisely inverting what the commentary is for.

⚑ AN UNTOKENIZABLE FILE GETS THE PERMISSIVE ANSWER: every line counts as code. Refusing to
report would make a syntax error look like a clean scan, which is the absence-as-finding shape
this repo keeps catching. The caller sees a number, never a silent zero.
"""

from __future__ import annotations

import io
import tokenize


def _every_line(source: str) -> set[int]:
    """Return every 1-based line number in `source` — the permissive fallback."""
    return set(range(1, source.count("\n") + 2))


def _spans(source: str) -> tuple[set[int], set[int]]:
    """Return `(comment lines, wholly-string lines)` — the lines a string token fully covers.

    ⚑ THE INTERIOR OF A MULTI-LINE STRING IS THE CASE A DELIMITER-STRIPPING REGEX MISSES, and
    it is the common one: a module docstring's first line is `\"\"\"Summary…`, whose residue
    after removing the quotes is prose, not emptiness. Reporting only the lines a token
    *encloses* — every line strictly between its start and end, plus a start or end line with
    nothing outside the token — answers the question without re-parsing what tokenize knows.
    """
    comment: set[int] = set()
    strings: set[int] = set()
    lines = source.splitlines()
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type == tokenize.COMMENT:
            comment.add(tok.start[0])
        elif tok.type == tokenize.STRING:
            first, last = tok.start[0], tok.end[0]
            strings.update(range(first + 1, last))
            before = lines[first - 1][: tok.start[1]].strip() if first <= len(lines) else ""
            after = lines[last - 1][tok.end[1] :].strip() if last <= len(lines) else ""
            # ⚑ A SINGLE-LINE TOKEN NEEDS BOTH SIDES CLEAR. `"""doc"""; x = 1` is code, and
            # testing the two ends independently would drop it on the strength of either half.
            if first == last:
                if not before and not after:
                    strings.add(first)
                continue
            if not before:
                strings.add(first)
            if not after:
                strings.add(last)
    return comment, strings


def code_lines(source: str) -> set[int]:
    """Return the 1-based line numbers of `source` that carry code.

    ⚑ TOKENIZATION FAILURE IS NOT EMPTINESS. `SyntaxError`, `IndentationError` and
    `tokenize.TokenError` are caught by NAME rather than as a blind `Exception`: a blind catch
    would swallow an `OSError` or a `MemoryError` and report the permissive answer for a
    failure that has nothing to do with the source being malformed.
    """
    try:
        comment, strings = _spans(source)
    except (tokenize.TokenError, SyntaxError, IndentationError, ValueError):
        return _every_line(source)
    out: set[int] = set()
    for i, line in enumerate(source.splitlines(), 1):
        text = line.strip()
        if not text:
            continue
        if i in comment and text.startswith("#"):
            continue
        if i in strings:
            continue
        out.add(i)
    return out


def code_count(source: str) -> int:
    """Return how many lines of `source` are code — the size census's numerator."""
    return len(code_lines(source))


def physical_count(source: str) -> int:
    """Return how many lines `source` has at all, the number a reader actually scrolls past.

    ⚑ REPORTED BESIDE `code_count`, NEVER INSTEAD OF IT. Measured on `sppf_db.py`: it read
    `1060 code — OK, 140 under its cap` while being ~1800 physical lines. Both were true and
    only one was printed, so the file passed a metric while being well past the point the rule
    names. A reader does not scroll past code lines; they scroll past LINES.
    """
    return len(source.splitlines())
