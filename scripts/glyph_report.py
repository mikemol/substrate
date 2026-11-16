#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""glyph_report.py — the confusable characters the checker objects to in one file, by position.

⚑⚑⚑ THE ESCAPE SET IS THE CHECKER'S, AND THIS IS HOW A READER ASKS FOR IT (gate-G203). Moving
hand-authored mathematical records between files carries their lint debt: `RUF001`/`RUF002`/
`RUF003` flag every glyph resembling a Latin letter, and in this corpus those glyphs are the
content. The operator ruled for named escapes over a per-file ignore, which makes *which
characters* the first question — and a hand-written answer would be a second authority on a rule
ruff owns. Measured (gate-G205): an authored set held seven where the checker names nineteen.

⚑⚑⚑ AND *WHERE* IS THE SECOND QUESTION, WHICH A FIRST CUT COLLAPSED. A named escape denotes its
character only inside a STRING; in a COMMENT the same spelling becomes literal backslash-N text,
and the round-trip check cannot catch that because both sides decode identically. So this reports
the escapable set and the comment-only set separately, and the comment-only set BLOCKS.

⚑⚑ AND IT EXISTS BECAUSE THE ALTERNATIVE WAS AN INLINE SCRIPT. Asking this without a mode meant
piping the checker's output through a one-off inline program, which the chaining hook refused and
was right to: the judgement would have lived in the turn rather than in a program, and the next
reader would have re-derived it differently. A missing mode is work.

⚑ THE REPORT NAMES ITS COMPONENTS RATHER THAN COUNTING THEM (gate-G204). A bare total cannot
distinguish a clean file from a failed parse — both give zero — so this prints each character
with the Unicode name the checker used, and prints the UNCONFIRMED rows separately, because a row
whose printed name disagrees with the parsed character is a gap in this reader rather than a
finding about the file.

Usage: glyph_report.py <file> [--escapes]
       --escapes   also print the named-escape spelling each character would become
"""

from __future__ import annotations

import subprocess
import sys
import unicodedata
from pathlib import Path

from substrate import glyph_escape, glyph_flagged

ROOT = Path(__file__).resolve().parent.parent

#: The checker that owns the verdict about which characters are confusable.
CHECKER = ROOT / "scripts" / "pycheck_show.py"


def _render(chars: frozenset[str], *, escapes: bool) -> None:
    """Print one character per line with its codepoint, name, and optionally its escape."""
    for char in sorted(chars):
        line = f"  {char}  U+{ord(char):04X}  {unicodedata.name(char)}"
        if escapes:
            line += f"  ->  {glyph_escape.escape_name(char)}"
        print(line)  # noqa: T201


def main(argv: list[str]) -> int:
    """Report the characters the checker flags in one file, split by position."""
    names = [a for a in argv[1:] if not a.startswith("-")]
    if len(names) != 1:
        print(__doc__)  # noqa: T201
        return 2
    target = Path(names[0])
    if not target.exists():
        print(f"glyph_report: not a file: {target}")  # noqa: T201
        return 2

    ran = subprocess.run(  # noqa: S603 — a fixed argv, no shell, operands are repo paths
        [sys.executable, str(CHECKER), str(target)],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    found = glyph_flagged.flagged_in(ran.stdout + ran.stderr)
    escapes = "--escapes" in argv

    # ⚑ THE CHECKER'S OWN EXIT IS REPORTED BESIDE THE SET, because an empty set means two
    # different things — the file is clean, or it has findings of other kinds — and only the
    # exit code separates them.
    print(f"glyph_report: {target} — checker exit {ran.returncode}")  # noqa: T201
    if not found.escapable and not found.comment_only and not found.mismatched:
        print(
            "  no confusable-character findings "  # noqa: T201
            "(⚑ this says nothing about findings of OTHER kinds — see the exit code)"
        )
        return 0

    if found.escapable:
        print("  ESCAPABLE (in a string or docstring):")  # noqa: T201
        _render(found.escapable, escapes=escapes)

    if found.comment_only:
        # ⚑⚑ A COMMENT-FLAGGED CHARACTER BLOCKS. A named escape there is literal backslash-N
        # text, and the round-trip check cannot see the damage — both sides decode identically.
        print(
            "  ⚑ IN COMMENTS — NOT ESCAPABLE. A named escape here becomes literal text "  # noqa: T201
            "and the round-trip check CANNOT catch it:"
        )
        _render(found.comment_only, escapes=False)

    if found.mismatched:
        # ⚑⚑ AN UNCONFIRMED ROW IS A THIRD OUTCOME AND IT BLOCKS. This reader and the checker
        # disagree about what was said, so escaping on this set would apply the wrong
        # transformation to a record nobody re-reads.
        print(
            f"  ⚑ {len(found.mismatched)} row(s) UNCONFIRMED — the parsed character's own "  # noqa: T201
            "Unicode name differs from the one the checker printed:"
        )
        for char, claimed in found.mismatched:
            print(
                f"      parsed {char!r} ({unicodedata.name(char, '?')}) "  # noqa: T201
                f"but the checker said {claimed}"
            )

    print(f"  {found.why()}")  # noqa: T201
    return 0 if found.clearable else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
