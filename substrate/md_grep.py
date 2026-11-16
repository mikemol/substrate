#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Structural grep over markdown: where a string is, AS A SPAN you can read or replace.

⚑⚑⚑ FILED BY A CONSUMER WHO CAUGHT THEMSELVES ROUTING AROUND THE RULE (cassian-observability,
2026-08-31). The structural-query hook refuses textual `grep` over `.md` — correctly, since a
`#` inside a fence is not a header — and this toolkit had header/table/item/section modes but no
*"find this text and tell me where it is"* mode. Sweeping a plan document for a now-stale phrase
is a legitimately textual question, and the filer reports nearly renaming the file to a
non-`.md` extension to dodge the hook before filing this instead. The operator's ruling, quoted
in the request: *"If the tool doesn't readily answer the question you have, improve the tool."*

⚑⚑ THE ANSWER IS A JOIN OVER MACHINERY THAT ALREADY EXISTS, NOT A NEW PARSER. `md_spans` owns
the header grammar including the subtlety a line-regex gets wrong — a span ends at the next
SAME-OR-SHALLOWER header, so a `###` containing a `####` does not end at the child — and
`enclosing()` already returns the container chain for a line. Re-deriving either here would be a
second grammar for one document shape, which is the defect this toolkit exists to retire.

⚑⚑ WHY A PAIR AND NOT EITHER HALF (the filer's reasoning, kept because it is the design):
`grep -n` gives a line and no structure, so you then work out which section it is in before you
can edit safely; a bare structural container gives structure and no coordinates, so you then
hunt for the lines. The pair is what makes it one-shot — the query-side analogue of
`--replace-section` on the write side: address by structure, act on a precise range.

⚑⚑⚑ TABLES ARE NOT ADDRESSED, AND THAT IS REPORTED RATHER THAN FAKED. The request asks for
`table 2 (row 3)` containers too. Pandoc carries NO SOURCE POSITIONS: `md_spans` recovers line
numbers for headers only, by matching each rendered heading against raw lines in order, and no
equivalent anchoring exists for table syntax. Emitting a table coordinate would put a number in
the output that nothing measured. A match inside a table still reports its enclosing SECTION
span, which is the editable unit — and that is stated in the output, not left to the reader.

⚑⚑⚑ AN UNRECOGNISED FLAG IS REFUSED, AND THE DEFECT THAT FORCED THIS WAS A FALSE ABSENCE IN A
CENSUS (gate-G102, 2026-09-06). The argv split kept every dash-leading token as a flag and then
tested the flag set by EXACT MEMBERSHIP, so a clustered spelling like `-iE` was neither member,
BOTH flags were silently discarded, and the search ran case-sensitive and LITERAL against what
the caller wrote as an alternation. It matched nothing and printed *no line matches* — a result
indistinguishable from a true absence. It was caught one step before a census leg was reported
clean on a broken search, and only because a positive control returned hits that were obviously
false.

⚑⚑ SO THE FAILURE DIRECTION IS WHAT MAKES THIS WORTH A REFUSAL RATHER THAN A CONVENIENCE. A
reader that mis-parses its own invocation and answers anyway MANUFACTURES ABSENCES, and an
absence is precisely what this tool is used to establish. Every other unrecognised-input guard
in this tree refuses and names the token; this one accepted and answered, which is the same
class with the opposite safety profile.

⚑ CLUSTERING IS NOT SUPPORTED, AND SAYING SO IS THE POINT. Accepting `-iE` by splitting it would
also be defensible, but it would make the roster implicit again — the refusal states the closed
set, so a future flag is added in one place and an old typo can never silently mean nothing. A
pattern that must begin with a dash is reachable via `--`, which is stated in the usage rather
than left for a caller to discover by getting a wrong answer.

⚑⚑⚑ `Hit` / `container_of` / `search` / `PREAMBLE` NOW COME FROM `mikemol.mdstruct.grep` (W9,
structural cross-census against mtools). Confirmed a partial twin: the library half is
byte-equivalent (only names and container types differ — `NamedTuple` there, a frozen dataclass
here, both structurally the same); `Argv`/`parse`/`render`/`main` are the CLI/driver layer and
mtools does not carry a CLI, matching the same boundary mtools drew for pycodemod's DO-NOT-PORT
letter. ⚑ mtools' copy has ALSO grown `regex_tell` (a literal-vs-regex disambiguator for a silent
zero-match defect) that this CLI does not yet call — noted as a candidate improvement, not wired
here; wiring it is a behaviour CHANGE, not a repoint, and stays out of this unit.

    md_grep.py <pattern> FILE.md [-i] [-E]
    md_grep.py -- <pattern-beginning-with-dash> FILE.md
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from mikemol.mdstruct.grep import Hit, search

# `<pattern> FILE.md` — the positionals every invocation supplies.
_MIN_ARGS = 2

# ⚑ THE CLOSED ROSTER. A flag outside this set is refused rather than dropped, which is the whole
#   of gate-G102's repair: membership testing against an implicit roster silently ignores what it
#   does not recognise, and this tool's answers are absence claims.
FLAGS = ("-i", "-E")

# The end-of-flags marker, so a pattern may begin with a dash.
END_OF_FLAGS = "--"

USAGE = (
    "usage: md_grep.py <pattern> FILE.md [-i] [-E]\n"
    "       md_grep.py -- <pattern-beginning-with-dash> FILE.md\n"
)


@dataclass(frozen=True, slots=True)
class Argv:
    """One parsed invocation, or the refusal that says why it is not one.

    ⚑ THE REFUSAL IS A VALUE, NOT AN EXCEPTION OR A BARE None. A caller must be able to
    distinguish *this invocation is unusable* from *this search found nothing*, and those were
    the two states gate-G102 collapsed.
    """

    args: tuple[str, ...]
    flags: frozenset[str]
    refusal: str

    @property
    def usable(self) -> bool:
        """Report whether this invocation names a pattern and a file with only known flags."""
        return not self.refusal


def _unknown_flag_refusal(unknown: list[str]) -> str:
    """Build the refusal naming every unrecognised flag and both escapes from it."""
    named = ", ".join(repr(u) for u in unknown)
    known = " ".join(FLAGS)
    return (
        f"md-grep: unrecognised flag(s): {named}\n"
        f"  known flags are: {known}\n"
        "  ⚑ REFUSING rather than ignoring. A dropped flag would run the search with the\n"
        "    wrong semantics — a regex matched literally, a case-fold not applied — and\n"
        "    report NO MATCHES, which is indistinguishable from a true absence.\n"
        "  ⚑ clustering is not supported: spell '-i -E', not '-iE'.\n"
        "  ⚑ for a pattern that begins with '-', use: md_grep.py -- <pattern> FILE.md\n"
    )


def parse(argv: list[str]) -> Argv:
    """Split argv into positionals and flags, REFUSING any flag not in the closed roster.

    ⚑ EVERYTHING AFTER `--` IS A POSITIONAL, so a pattern may begin with a dash. Without this,
    a dash-leading pattern is consumed as a flag and the search runs against the filename or
    refuses on arity — the operand-ownership half of the same defect.
    """
    args: list[str] = []
    flags: set[str] = set()
    unknown: list[str] = []
    literal = False

    for token in argv[1:]:
        if literal or not token.startswith("-"):
            args.append(token)
        elif token == END_OF_FLAGS:
            literal = True
        elif token in FLAGS:
            flags.add(token)
        else:
            unknown.append(token)

    if unknown:
        return Argv((), frozenset(), _unknown_flag_refusal(unknown))
    if len(args) < _MIN_ARGS:
        return Argv((), frozenset(), USAGE)
    return Argv(tuple(args), frozenset(flags), "")


def render(hits: list[Hit]) -> list[str]:
    """Render each hit as its container, its span, and the matching line."""
    out = []
    for hit in hits:
        out.append(f"  {hit.container}")
        out.append(f"    L{hit.start}-{hit.end}  :  L{hit.line_no}  {hit.line}")
    return out


def main(argv: list[str]) -> int:
    """Search one markdown file and print the structural span of every match."""
    parsed = parse(argv)
    if not parsed.usable:
        sys.stderr.write(parsed.refusal)
        return 2

    pattern, path = parsed.args[0], Path(parsed.args[1])
    if not path.exists():
        sys.stderr.write(f"md-grep: no such file: {path}\n")
        return 2

    hits = search(path, pattern, regex="-E" in parsed.flags, ignore_case="-i" in parsed.flags)
    if not hits:
        # ⚑ AN EMPTY RESULT IS A FACT ABOUT THIS FILE AND THIS PATTERN, and it says so. A bare
        # silence reads as a tool that did nothing — the absence/failure collapse. It is only
        # trustworthy because `parse` has already refused an invocation it could not honour.
        sys.stdout.write(f"md-grep: no line in {path} matches {pattern!r}\n")
        return 1

    sys.stdout.write("\n".join(render(hits)) + "\n")
    sys.stdout.write(f"  {len(hits)} match(es) in {path}\n")
    # ⚑ THE LIMIT IS PRINTED WITH THE RESULT, not left in a docstring. A reader who asked for
    # table coordinates must see that they got section spans instead, at the moment they read
    # the output rather than when they next open the source.
    sys.stdout.write(
        "    ⚑ containers are SECTIONS. Pandoc carries no source positions for\n"
        "      tables, so a match inside one reports its enclosing section —\n"
        "      which is the editable unit — never a table/row coordinate.\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
