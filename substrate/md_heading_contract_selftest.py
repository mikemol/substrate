#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_heading_contract` — the line reader, and the contract itself.

⚑⚑ THE LIVE CASE IS SUMMIT'S REDUCTION: a heading carrying an ASCII apostrophe. The arm plants
it beside an ordinary heading, a fenced `#` line, and a setext header, and asserts the contract
HOLDS — which is the assertion summit asked for, and the one that reddens the day any reader
drops a heading again. A second arm runs the contract over this repo's own CLAUDE.md, the
richest markdown the tree carries, and asserts nothing is lost.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import corpus
from substrate import md_heading_contract as hc

_LONG = "Filing into floor/inbox/: four conventions, each learned so far by violating it"
_FIXTURE = (
    "# Title\n"
    "\n"
    f"## {_LONG}\n"
    "\n"
    "prose\n"
    "\n"
    "## The rule's layer that can refuse\n"
    "\n"
    "```sh\n"
    "# not a heading\n"
    "```\n"
    "\n"
    "~~~\n"
    "## nor this one\n"
    "~~~\n"
    "\n"
    "### `code` in a heading\n"
    "\n"
    "Setext one\n"
    "==========\n"
)


def _plant(text: str) -> Path:
    """Write a fixture and return its path."""
    target = Path(tempfile.mkdtemp(prefix="md-contract-")) / "f.md"
    target.write_text(text, encoding="utf-8")
    return target


def the_line_reader_skips_fences_and_keeps_levels(out: list[str]) -> int:
    """Check raw headings are found outside both fence kinds, with level and line."""
    raw = hc.raw_headings(_FIXTURE)
    got = [(r.lineno, r.level, r.text) for r in raw]
    want = [
        (1, 1, "Title"),
        (3, 2, _LONG),
        (7, 2, "The rule's layer that can refuse"),
        (17, 3, "`code` in a heading"),
    ]
    if got != want:
        out.append(f"selftest: raw headings read {got}")
        return 1
    return 0


def the_contract_holds_on_the_apostrophe_reduction(out: list[str]) -> int:
    """Check every raw heading — the apostrophe one included — is a parsed section."""
    found = hc.verdict(_plant(_FIXTURE))
    bad = 0
    if not found.holds:
        out.append("selftest: the contract does not hold on the reduction:")
        out += [f"    {line}" for line in hc.render(Path("f.md"), found)]
        bad += 1
    if [text for _l, text in found.unseen] != ["Setext one"]:
        out.append(f"selftest: the setext header was not the one unseen row: {found.unseen!r}")
        bad += 1
    return bad


def the_contract_holds_on_this_repos_claude_md(out: list[str]) -> int:
    """Check the tree's own richest markdown loses no heading to the parser."""
    path = corpus.ROOT / "CLAUDE.md"
    if not path.is_file():
        out.append("selftest: CLAUDE.md is absent — the live case cannot run")
        return 1
    found = hc.verdict(path)
    if not found.holds:
        out.append("selftest: CLAUDE.md loses headings:")
        out += [f"    {line}" for line in hc.render(path, found)]
        return 1
    return 0


_ARMS = (
    the_line_reader_skips_fences_and_keeps_levels,
    the_contract_holds_on_the_apostrophe_reduction,
    the_contract_holds_on_this_repos_claude_md,
)

_CASE_COUNT = 1 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"md-heading-contract selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"md-heading-contract selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
