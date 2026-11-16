#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The heading contract: every `^#{1,6}` line outside a fence appears as a parsed section.

⚑⚑⚑ THE SELF-ASSERTING CONTRACT SUMMIT ASKED FOR (ask-mdstruct-heading-contract, open since
2026-09-06): `mdstruct --headers` read 20 of 21 headings on summit's CLAUDE.md, dropping the
apostrophe-bearing one and absorbing its lines into its parent — silently, so summit's `routes`
slice read 38 of 39 on that single cause. A header listing that can lose a section without
saying so is the census-green shape in the tool that owns markdown; this module is the reader
that says so.

⚑⚑ TWO READERS, DELIBERATELY DECORRELATED. `md_ast.headers` reads pandoc's AST — right about
fences and setext underlines, and whatever else pandoc's grammar knows. `raw_headings` reads
the LINES, with the one thing a line reader must know (a fence is not prose) and nothing else.
Their disagreement is the finding: a raw heading with no parsed counterpart is one the AST path
lost; a parsed heading with no raw counterpart is a setext header the line reader cannot see,
and is reported, not counted against the contract.

⚑ MATCHED BY ANCHOR KEY, so inline markup pandoc strips (backticks, emphasis) does not read as
a loss — `md_ast.anchor_key` is the comparison every write mode already uses.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import md_ast

if TYPE_CHECKING:
    from pathlib import Path

# An ATX heading line: one to six `#`, a space, the text (a trailing `#` run is decoration).
_ATX = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
# A fence opener/closer: three or more backticks or tildes at the line start.
_FENCE = re.compile(r"^\s*(`{3,}|~{3,})")

_UNSEEN_NOTE = "(setext, or a heading the line reader cannot spell)"


@dataclass(frozen=True, slots=True)
class Raw:
    """One ATX heading as the source spells it."""

    lineno: int
    level: int
    text: str


@dataclass(frozen=True, slots=True)
class Verdict:
    """The contract's reading of one file."""

    raw: tuple[Raw, ...]
    parsed: tuple[tuple[int, str], ...]
    lost: tuple[Raw, ...]
    unseen: tuple[tuple[int, str], ...]

    @property
    def holds(self) -> bool:
        """Report whether every raw heading has a parsed counterpart."""
        return not self.lost


def raw_headings(text: str) -> list[Raw]:
    """Return every ATX heading line outside a fence, in source order."""
    out: list[Raw] = []
    fence: str | None = None
    for lineno, line in enumerate(text.splitlines(), start=1):
        opener = _FENCE.match(line)
        if opener:
            mark = str(opener.group(1))
            if fence is None:
                fence = mark[0]
            elif mark[0] == fence:
                fence = None
            continue
        if fence is not None:
            continue
        found = _ATX.match(line)
        if found:
            out.append(Raw(lineno, len(found.group(1)), str(found.group(2))))
    return out


def verdict(path: Path) -> Verdict:
    """Read a file both ways and return which headings each reader cannot see."""
    raw = tuple(raw_headings(path.read_text(encoding="utf-8")))
    parsed = tuple(md_ast.headers(path))
    keys = {md_ast.anchor_key(text) for _level, text in parsed}
    raw_keys = {md_ast.anchor_key(r.text) for r in raw}
    lost = tuple(r for r in raw if md_ast.anchor_key(r.text) not in keys)
    unseen = tuple(p for p in parsed if md_ast.anchor_key(p[1]) not in raw_keys)
    return Verdict(raw, parsed, lost, unseen)


def render(path: Path, found: Verdict) -> list[str]:
    """Render the contract's verdict, naming every heading a reader could not see."""
    head = (
        f"{path}: {len(found.raw)} raw heading(s), {len(found.parsed)} parsed, "
        f"{len(found.lost)} LOST by the parser, {len(found.unseen)} unseen by the line reader"
    )
    lines = [head]
    lines += [f"  LOST    :{r.lineno:<5} {'#' * r.level} {r.text}" for r in found.lost]
    lines += [f"  unseen  {'#' * level} {text}   {_UNSEEN_NOTE}" for level, text in found.unseen]
    return lines


def main(argv: list[str]) -> int:
    """Check every named file; exit 1 if any loses a heading, 2 with no operands."""
    import sys  # noqa: PLC0415 - the only place output happens
    from pathlib import Path as _Path  # noqa: PLC0415 - runtime use, not just annotation

    paths = [a for a in argv if not a.startswith("-")]
    if not paths:
        sys.stderr.write("usage: md_heading_contract.py <file.md>…\n")
        return 2
    lost = 0
    for name in paths:
        path = _Path(name)
        found = verdict(path)
        sys.stdout.write("\n".join(render(path, found)) + "\n")
        lost += len(found.lost)
    return 1 if lost else 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv[1:]))
