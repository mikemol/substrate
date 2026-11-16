#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin that an unusable invocation REFUSES, and never answers with a false absence.

⚑⚑⚑ THE LOAD-BEARING CASE IS THE ONE THAT DISTINGUISHES A REFUSAL FROM AN EMPTY RESULT. Before
gate-G102 this tool answered a mis-parsed invocation, and the answer was *no line matches* —
byte-identical to what it prints for a genuine absence. So a case asserting only *the clustered
spelling does not return hits* would PASS against the defect. Every refusal case here asserts
the exit code AND that the message names the offending token.

⚑⚑ AND THE ACCEPT DIRECTION IS ASSERTED FIRST. A parser that refused everything would satisfy
every refusal case below, which is the inversion a suite of only-negative cases cannot see.

⚑ THE DASH-LEADING PATTERN IS CASED IN BOTH DIRECTIONS, because it is the half of the defect
that was never measured — only implied. A pattern beginning with a dash was consumed as a flag
and never reached the search at all, and the `--` escape is what makes it reachable. Asserting
only that `--` is accepted would not show that the pattern actually SEARCHES.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import md_grep

Case = tuple[str, bool]

ROOT = Path(__file__).resolve().parent.parent

# A real tracked document, so the search cases exercise the live span machinery rather than a
# fixture whose shape I chose to match my own parser.
LIVE = ROOT / "CLAUDE.md"

# ⚑ A TOKEN KNOWN PRESENT IN `LIVE`, AND DASH-LEADING ON PURPOSE — it is the positive control
#   for the escape. A `--` case whose pattern is absent cannot tell "the escape works" from
#   "the escape silently ate the pattern too".
PRESENT_DASHED = "--jobs"


def _argv(*tokens: str) -> list[str]:
    """Build an argv list with the program name the parser skips."""
    return ["md_grep.py", *tokens]


def _accept_cases() -> list[Case]:
    """Return the cases pinning that a well-formed invocation parses."""
    plain = md_grep.parse(_argv("timing", str(LIVE)))
    both = md_grep.parse(_argv("-i", "-E", "a|b", str(LIVE)))
    return [
        # ⚑ ACCEPT FIRST — without it a parser refusing everything passes every case below.
        ("a bare pattern and file is usable", plain.usable),
        ("...carrying no refusal text", plain.refusal == ""),
        ("...and no flags", plain.flags == frozenset()),
        ("both known flags spelled separately are usable", both.usable),
        ("...and both are recorded", both.flags == frozenset({"-i", "-E"})),
        ("...with the pattern still first", both.args[0] == "a|b"),
    ]


def _refusal_cases() -> list[Case]:
    """Return the cases pinning that an unrecognised flag is REFUSED, not dropped."""
    clustered = md_grep.parse(_argv("-iE", "a|b", str(LIVE)))
    bogus = md_grep.parse(_argv("--nosuch", "x", str(LIVE)))
    short = md_grep.parse(_argv("timing"))
    return [
        # ⚑⚑⚑ THE DEFECT ITSELF. The clustered spelling silently dropped BOTH flags and searched
        #     literally, printing "no line matches" — indistinguishable from a true absence.
        ("a clustered flag is REFUSED, not dropped", not clustered.usable),
        ("...and the refusal names the offending token", "'-iE'" in clustered.refusal),
        ("...and names the known roster", "-i -E" in clustered.refusal),
        # ⚑ THE MESSAGE MUST SAY WHY, because the reader who hits this is mid-census and about
        #   to interpret a zero.
        (
            "...and warns that a dropped flag reads as an absence",
            "indistinguishable from a true absence" in clustered.refusal,
        ),
        ("...and names the escape", "-i -E" in clustered.refusal),
        ("an unknown long flag is refused", not bogus.usable),
        ("...naming it", "'--nosuch'" in bogus.refusal),
        # ⚑ ARITY IS A DIFFERENT REFUSAL AND KEEPS ITS OWN MESSAGE, so a caller who forgot the
        #   file is not told about flags.
        ("a missing operand is refused", not short.usable),
        ("...with the usage, not the flag complaint", "usage:" in short.refusal),
        ("...and does not claim an unrecognised flag", "unrecognised" not in short.refusal),
    ]


def _escape_cases() -> list[Case]:
    """Return the cases pinning that `--` makes a dash-leading pattern reachable."""
    escaped = md_grep.parse(_argv("--", PRESENT_DASHED, str(LIVE)))
    trailing = md_grep.parse(_argv("-i", "--", "-x", str(LIVE)))
    return [
        ("a dash-leading pattern after -- is usable", escaped.usable),
        # ⚑ THE PATTERN SURVIVES INTACT. Consuming `--` and then eating the pattern too would
        #   also "work" by the usable test alone.
        ("...and the pattern itself is preserved", escaped.args[0] == PRESENT_DASHED),
        ("...and the file is still second", escaped.args[1] == str(LIVE)),
        # ⚑ FLAGS BEFORE `--` STILL BIND, so the escape does not silently disarm them.
        ("a flag before -- still binds", trailing.flags == frozenset({"-i"})),
        ("...and the dash-leading pattern after it survives", trailing.args[0] == "-x"),
    ]


def _search_cases() -> list[Case]:
    """Return the cases pinning that the escape actually SEARCHES, against the live document."""
    found = md_grep.search(LIVE, PRESENT_DASHED)
    absent = md_grep.search(LIVE, "--no-such-flag-anywhere")
    regex = md_grep.search(LIVE, "timing|seconds", regex=True, ignore_case=True)
    literal = md_grep.search(LIVE, "timing|seconds")
    return [
        # ⚑⚑ THE POSITIVE CONTROL FOR THE ESCAPE. Without a known-present dashed pattern, an
        #    empty result cannot distinguish "the escape works and the text is absent" from
        #    "the escape ate the pattern".
        ("a dash-leading pattern FINDS its real occurrences", len(found) > 0),
        ("...and a dash-leading pattern that is absent finds none", len(absent) == 0),
        # ⚑⚑⚑ THE SEMANTIC DIFFERENCE THE DROPPED FLAG ERASED. An alternation matched as a regex
        #     finds lines; matched literally it finds none — which is exactly the false zero.
        ("an alternation as REGEX finds lines", len(regex) > 0),
        ("...and the same string LITERALLY finds none", len(literal) == 0),
        ("...so the two readings genuinely differ", len(regex) != len(literal)),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = _accept_cases() + _refusal_cases() + _escape_cases() + _search_cases()
    bad = [label for label, holds in cases if not holds]
    print(f"md_grep: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
