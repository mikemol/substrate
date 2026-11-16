#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""heading_probe.py — read a document's headings through the drained reader, reporting losses.

⚑⚑⚑ THIS IS THE ACCEPTANCE CRITERION MADE RUNNABLE, and it exists because the origin could not
state its own failure. `mdstruct --headers` returns a short list in silence, so a document whose
headings all fail to anchor is indistinguishable from a document with no sections — two sessions
independently read that emptiness as a fact about the markdown. This prints placed AND unplaced
with a denominator, so the same document reads as a locatable defect.

⚑⚑ THE CRITERION WAS AGREED WITH THE PEER WHO ISOLATED THE TRIGGER, and it is a range rather than
a target: the natural case must move from ZERO anchored to ALL anchored. Anything strictly between
means a second effect exists that the smart-punctuation account does not explain, and the
difference matters — a partial pass would let the repair look complete while a class stayed broken.

⚑ IT IS A PROBE, NOT A MODE OF THE ORIGIN. Wiring the drained reader into `mdstruct` is an edit to
a file the per-file gate refuses, so this reaches the same answer through the package and leaves
the origin alone. It retires when the swap lands.

Usage: heading_probe.py <file.md> [<file.md> …]
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import heading_spans, pandoc_read


def probe(path: Path) -> int:
    """Report one document's anchoring, returning an exit code."""
    try:
        found = pandoc_read.headings(path)
    except pandoc_read.PandocError as exc:
        # ⚑ A CONVERSION FAILURE IS NOT AN EMPTY DOCUMENT, and saying so is the whole point.
        print(f"{path}: UNREADABLE — pandoc refused: {exc}")  # noqa: T201
        return 2

    lines = path.read_text(encoding="utf-8").split("\n")
    anchored = heading_spans.anchor(found, lines)
    print(f"{path}: {anchored.why()}")  # noqa: T201
    for level, text in anchored.unanchored:
        print(f"    UNANCHORED  {'#' * level} {text}")  # noqa: T201
    return 0 if anchored.complete else 1


def main(argv: list[str]) -> int:
    """Probe each named document, returning the worst exit code seen."""
    names = [a for a in argv[1:] if not a.startswith("-")]
    if not names:
        print(__doc__)  # noqa: T201
        return 2
    worst = 0
    for name in names:
        path = Path(name)
        if not path.exists():
            print(f"heading_probe: not a file: {path}")  # noqa: T201
            worst = max(worst, 2)
            continue
        worst = max(worst, probe(path))
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv))
