#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""roster_span.py — report a module's roster literal by SPAN and by ELEMENT COUNT.

⚑⚑⚑ THE COUNT THIS PRINTS IS THE ONE A READER GOT WRONG (gate-G216). A hand transcription of
`scripts/worklist.py`'s roster produced 47 where the tree holds 60, and that figure was filed as
a correction to the two instruments that had been right. This makes the question answerable by a
program, so the next mover never has to read.

⚑⚑ THE ELEMENT COUNT IS COMPARABLE TO THE OTHER TWO INSTRUMENTS BY CONSTRUCTION, and that is the
point of printing it beside them: `worklist.py --check` partitions the same population by status
and `check_worklist_predicates.py` uses it as a denominator. Three readings of one set, so a
disagreement is a defect rather than a difference of question.

Usage: roster_span.py <file.py> [<NAME>]      (NAME defaults to ITEMS)
       roster_span.py <file.py> <NAME> --text  (print the span's source)
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import roster_extract

#: The roster name this repo's worklist module uses.
DEFAULT_NAME = "ITEMS"


def report(path: Path, name: str, *, text: bool) -> int:
    """Print the named roster's span and element count, returning an exit code."""
    source = path.read_text(encoding="utf-8")
    span = roster_extract.find_assignment(source, name)
    if span is None:
        # ⚑ A FACT ABOUT THE QUERY, SAID AS ONE. "No assignment named X" is not "the module has
        # no roster" — a differently-spelled name reads identically from here.
        print(f"roster_span: no top-level assignment named {name!r} in {path}")  # noqa: T201
        return 1

    count = roster_extract.count_elements(source, name)
    shape = "not a list/tuple literal" if count is None else f"{count} element(s)"
    print(f"roster_span: {path} — {span.why()}, {shape}")  # noqa: T201
    if text:
        print(span.text, end="")  # noqa: T201
    return 0


def main(argv: list[str]) -> int:
    """Validate the operands and hand off to `report`."""
    names = [a for a in argv[1:] if not a.startswith("-")]
    if not names:
        print(__doc__)  # noqa: T201
        return 2
    path = Path(names[0])
    if not path.exists():
        print(f"roster_span: not a file: {path}")  # noqa: T201
        return 2
    roster = names[1] if len(names) > 1 else DEFAULT_NAME
    return report(path, roster, text="--text" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
