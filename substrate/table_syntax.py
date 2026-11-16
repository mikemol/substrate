# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Classify a markdown document's table SYNTAX from its raw lines.

⚑⚑⚑ THIS READS BYTES ON PURPOSE, WHICH IS THE OPPOSITE OF EVERY OTHER READER IN THIS DRAIN. Table
syntax is a property of the source text that the AST has already erased: pandoc parses a pipe
table and a multiline table into the same `Table` node, so a reader that walks the AST cannot tell
them apart. The question is which SPELLING is on disk, and only the lines answer it.

⚑⚑ AND THE QUESTION MATTERS BECAUSE `--columns` SILENTLY CHANGES IT. Enabling the pipe extension
does not FORCE pipe output — pandoc falls back to a multiline table whenever one exceeds the column
budget. So narrowing the width rewrites table syntax, and a linter then reports the dashed rules as
horizontal-rule-style violations and the header row as a setext heading. Measured on this repo:
normalising at one width drove the pipe-spacing class to zero and three other classes appeared in
its place.

⚑⚑⚑ THE MULTILINE COUNT IS AN ESTIMATE AND THE ORIGIN PRESENTED IT AS A COUNT. It counts dashed
RULES and divides by three, because a multiline table opens with one, separates its header with a
second and closes with a third. That is a sound heuristic and it is not a count: a headerless
multiline table has two rules, a stray dashed line in prose adds one, and both shift the quotient.
So `rules` travels beside `tables` here — the derived figure and the thing it was derived from —
and a caller that needs certainty can see the remainder rather than trusting a rounded number.

⚑ THE STYLE SCAN REPORTS A POPULATION, NEVER A TALLY. Each offending line is named, because the
repair is per-line and a bare count cannot be acted on. And the class it detects is one a
normalizer's fixpoint makes UNREPRESENTABLE rather than merely fixed — pandoc emits canonical pipe
spacing by construction, so a document at the fixpoint cannot violate the rule at all.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

#: How many dashed rules a complete multiline table carries: open, header separator, close.
RULES_PER_MULTILINE = 3

#: A dashed rule must be at least this long to be a table rule rather than prose punctuation.
MIN_RULE = 8

#: The characters a grid table's rule may contain.
GRID_CHARS = frozenset("+-=")

#: The characters a pipe table's delimiter row may contain.
PIPE_CHARS = frozenset("|-: ")

#: A pipe row needs at least this many pipes to be a row rather than a line mentioning one.
MIN_PIPES = 2


class Forms(NamedTuple):
    """How many tables of each syntax the document holds.

    ⚑ `rules` IS CARRIED BESIDE `multiline` BECAUSE THE LATTER IS DERIVED FROM IT BY DIVISION. A
    record holding only the quotient hides that the figure is an estimate, and the remainder is
    exactly the signal that the assumption broke.
    """

    pipe: int
    multiline: int
    grid: int
    rules: int

    @property
    def remainder(self) -> int:
        """Report dashed rules left over after grouping them into complete multiline tables.

        ⚑ A NON-ZERO REMAINDER MEANS THE THREE-RULES ASSUMPTION DID NOT HOLD on this document —
        a headerless table, a stray dashed line, or a truncated one. It does not say which, and
        it does say that `multiline` is a floor rather than a count.
        """
        return self.rules % RULES_PER_MULTILINE

    def why(self) -> str:
        """Return a one-line account naming every component, including the estimate's basis."""
        base = f"pipe {self.pipe}, multiline {self.multiline}, grid {self.grid}"
        if self.remainder:
            return (
                f"{base} — ⚑ multiline is an ESTIMATE from {self.rules} dashed rule(s) "
                f"with {self.remainder} left over, so the grouping assumption did not hold"
            )
        return f"{base} (multiline derived from {self.rules} dashed rule(s), none left over)"


class StyleHit(NamedTuple):
    """One line whose pipe spacing is non-canonical."""

    line: int
    kind: str


def is_grid_rule(line: str) -> bool:
    """Report whether `line` is a grid table's rule."""
    s = line.strip()
    return s.startswith("+-") and set(s) <= GRID_CHARS


def is_multiline_rule(line: str) -> bool:
    """Report whether `line` is a multiline table's dashed rule.

    ⚑ THE NO-PIPE CONDITION IS WHAT SEPARATES IT FROM A PIPE DELIMITER ROW, which is also dashes.
    A rule carrying a pipe belongs to a pipe table, and counting it here would inflate the
    multiline estimate by exactly the documents that have no multiline tables at all.
    """
    s = line.strip()
    return bool(s) and set(s) <= set("- ") and s.count("-") > MIN_RULE and "|" not in line


def is_pipe_delimiter(line: str) -> bool:
    """Report whether `line` is a pipe table's delimiter row."""
    s = line.strip()
    return s.startswith("|") and set(s) <= PIPE_CHARS


def forms(lines: Iterable[str]) -> Forms:
    """Return the syntax census, carrying the rule count the multiline figure derives from."""
    pipe = grid = rules = 0
    for line in lines:
        if is_grid_rule(line):
            grid += 1
        elif is_multiline_rule(line):
            rules += 1
        elif is_pipe_delimiter(line):
            pipe += 1
    return Forms(pipe, rules // RULES_PER_MULTILINE, grid, rules)


def style(lines: Sequence[str]) -> list[StyleHit]:
    """Return every line whose pipe spacing departs from the canonical `| a | b |`.

    ⚑ ONE HIT PER LINE, NOT PER PIPE. A row with three cramped pipes is one repair, and reporting
    it three times would make the population read as three times the work.
    """
    out: list[StyleHit] = []
    for i, raw in enumerate(lines, 1):
        s = raw.rstrip("\n")
        if not s.strip().startswith("|") or s.count("|") < MIN_PIPES:
            continue
        # ⚑⚑⚑ A DELIMITER ROW IS EXEMPT, AND THE ORIGIN DID NOT EXEMPT IT (gate-G241). `|---|---|`
        # is canonical markdown — the spacing rule governs CONTENT rows — but it trips a scan
        # looking for a space beside every interior pipe. Measured on the live plan: the origin
        # reported four hits, every one a delimiter row, so its entire population was false.
        if is_pipe_delimiter(s):
            continue
        body = s.strip()
        for match in re.finditer(r"\|", body):
            j = match.start()
            if j in (0, len(body) - 1):
                continue
            if body[j - 1] != " ":
                out.append(StyleHit(i, "missing space LEFT of pipe"))
                break
            if j + 1 < len(body) and body[j + 1] != " ":
                out.append(StyleHit(i, "missing space RIGHT of pipe"))
                break
    return out
