#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""glyph_rewrite_file.py — escape a file's checker-flagged characters, verifying the round trip.

⚑⚑⚑ THE TRANSFORMATION IS PERFORMED BY A PROGRAM, WHICH IS THE POINT. The records this moves are
dense hand-authored mathematical prose, and applying the substitutions by hand is the
reassembling-writer risk the whole arc guards against — a peer measured that class this week,
silently destroying three prose comments while their parse guard passed because the result was
still valid, merely shorter.

⚑⚑ THE SET COMES FROM THE CHECKER PER FILE, NEVER FROM A CALLER. `glyph_flagged` reads which
characters ruff objects to out of its own findings; an authored set was measured wrong in both
directions (gate-G205), holding seven where the checker names nineteen. Accepting a set on the
command line would reintroduce exactly that.

⚑⚑⚑ AND IT REFUSES ON A COMMENT-FLAGGED CHARACTER (gate-G206). A named escape denotes its
character only inside a STRING; in a comment the same spelling becomes literal backslash-N text,
and the round-trip check is structurally blind to that because both sides decode identically. So
`comment_only` being non-empty is a REFUSAL, not a warning — the one failure mode no verification
here can catch is the one it must not attempt.

⚑ THE ROUND TRIP IS VERIFIED BEFORE ANY WRITE, and the verdict carries its components
(gate-G204): a divergence names its index and both sides, a pass names the source it produced,
and a no-op change is reported as such rather than passing silently.

Usage: glyph_rewrite_file.py <file> [--apply]
       (dry by default — a mutating tool must not guess)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from substrate import glyph_flagged, glyph_rewrite

ROOT = Path(__file__).resolve().parent.parent

#: The checker that owns the verdict about which characters are confusable.
CHECKER = ROOT / "scripts" / "pycheck_show.py"


def flagged_for(target: Path) -> glyph_flagged.Flagged:
    """Return what the checker flags in `target`, split by position."""
    ran = subprocess.run(  # noqa: S603 — a fixed argv, no shell, operands are repo paths
        [sys.executable, str(CHECKER), str(target)],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    return glyph_flagged.flagged_in(ran.stdout + ran.stderr)


def escape(target: Path, *, apply: bool) -> int:
    """Escape `target`'s flagged characters and report, returning an exit code.

    ⚑ SEPARATE FROM ARGV HANDLING, AND THE GATE NAMED THAT SEAM (`PLR0911`). Validating operands
    and deciding whether an escape is admissible are two questions; the second never looks at
    argv, and folding them made one function carry both.
    """
    found = flagged_for(target)
    print(f"glyph_rewrite_file: {target} — {found.why()}")  # noqa: T201

    if not found.clearable:
        # ⚑⚑ REFUSED RATHER THAN PARTIALLY APPLIED. Escaping the string half while leaving the
        # comment half would clear some findings and leave the file refused for the rest, with
        # the caller unable to see why from the result.
        print(
            "  ⚑ REFUSING: escaping alone cannot clear this file. A comment-flagged "  # noqa: T201
            "character has no escape that denotes it, and an unconfirmed row means this "
            "reader and the checker disagree about what was said."
        )
        return 1
    if not found.escapable:
        print("  nothing to escape (⚑ this says nothing about findings of OTHER kinds)")  # noqa: T201
        return 0

    done = glyph_rewrite.rewrite_file(target, found.escapable, apply=apply)
    print(f"  {done.why()}")  # noqa: T201
    if not done.ok:
        # ⚑ A FAILING ROUND TRIP IS NEVER WRITTEN, and `rewrite_file` enforces that — this only
        # reports it. The escaped source is sound solely if it evaluates back to the original.
        return 1
    if not done.changed:
        print(
            "  ⚑ the rewrite changed NOTHING — a no-op round-trips perfectly and "  # noqa: T201
            "clears no finding, so this is reported rather than passing silently"
        )
        return 1
    if not apply:
        print("  (--apply to write)")  # noqa: T201
    return 0


def main(argv: list[str]) -> int:
    """Validate the operands and hand off to `escape`."""
    names = [a for a in argv[1:] if not a.startswith("-")]
    if len(names) != 1:
        print(__doc__)  # noqa: T201
        return 2
    target = Path(names[0])
    if not target.exists():
        print(f"glyph_rewrite_file: not a file: {target}")  # noqa: T201
        return 2
    return escape(target, apply="--apply" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
