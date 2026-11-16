#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Print a ratchet gate's census — the CLI over `substrate.ratchet_census`.

⚑ THE CLI IS ITS OWN MODULE, the split the rest of this toolkit uses: the reader returns data,
this decides how to render it.

    ratchet_census_show.py <gate-module> [<gate-module> ...]

⚑⚑ AN UNMEASURABLE GATE IS PRINTED AS SUCH, never omitted. A report that lists only the gates it
could read reports its own reach as the tree's state — the false-green shape this repo keeps
filing. A gate that would not import is a row here, with the reason.
"""

from __future__ import annotations

import sys

from substrate import ratchet_census


def render(name: str, got: ratchet_census.Census | None, why: str | None) -> str:
    """Render one gate's row: its census, or why there is none."""
    if got is None:
        return f"  UNMEASURABLE  {name:<34} {why}"
    if got.over:
        return (
            f"  OVER          {name:<34} {got.over} added of {got.held} held  e.g. {got.added[0]}"
        )
    return f"  at baseline   {name:<34} {got.held} held"


def main(argv: list[str]) -> int:
    """Census every gate named on the command line."""
    names = [a for a in argv[1:] if not a.startswith("-")]
    if not names:
        sys.stderr.write("usage: ratchet_census_show.py <gate-module> [<gate-module> ...]\n")
        return 2

    rows, unmeasurable, over = [], 0, 0
    for name in names:
        got, why = ratchet_census.census(name)
        rows.append(render(name, got, why))
        if got is None:
            unmeasurable += 1
        elif got.over:
            over += 1

    sys.stdout.write("\n".join(rows) + "\n")
    sys.stdout.write(f"  {len(names)} gate(s): {over} over baseline, {unmeasurable} UNMEASURABLE\n")
    # ⚑ UNMEASURABLE IS COUNTED SEPARATELY FROM CLEAN, because they need different actions and
    # collapsing them reports a gate nobody could read as a gate with nothing to report.
    return 1 if over or unmeasurable else 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS MODULE, and it DELEGATES rather than
# exiting 0 — a no-op guard reports nothing, which the outcome classifier calls `silent`.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import ratchet_census_selftest

        sys.exit(ratchet_census_selftest.selftest())
    sys.exit(main(sys.argv))
