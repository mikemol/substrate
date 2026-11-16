# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Print the finding-key collision census, or check one ordinal before filing.

The CLI over `substrate.finding_keys`. ⚑ THE CHECK MODE IS THE POINT: a filer about to
register `family-F55` can ask whether that ordinal is free, which is the compare a
read-modify-write over the roster does not do. The census mode is the paydown view.
"""

from __future__ import annotations

import re
import sys

from substrate import finding_keys

_USAGE = """\
usage: finding_keys_show.py [<family>-<letter><number>]

With no argument, print every ordinal naming more than one finding.
With an ordinal, report whether it is free and what already holds it.

⚑ NO NEXT NUMBER IS OFFERED. A suggested ordinal goes stale between the read and the
  write, which is the read-modify-write defect this exists to catch.
"""

_ORDINAL = re.compile(r"^([a-z]+)-([A-Z])(\d+)$")


def main(argv: list[str]) -> int:
    """Print the census, or answer about one ordinal."""
    if "--help" in argv or "-h" in argv:
        sys.stdout.write(_USAGE)
        return 0
    if not argv:
        sys.stdout.write(finding_keys.render() + "\n")
        return 0

    match = _ORDINAL.match(argv[0])
    if match is None:
        sys.stderr.write(f"finding_keys_show: {argv[0]!r} is not <family>-<letter><n>\n")
        sys.stderr.write(_USAGE)
        return 2

    family, letter, number = match.group(1), match.group(2), int(match.group(3))
    held = [o for o in finding_keys.ordinals()
            if o.family == family and o.letter == letter and o.number == number]
    if not held:
        sys.stdout.write(f"{argv[0]}: FREE\n")
        return 0
    sys.stdout.write(f"{argv[0]}: TAKEN by {len(held[0].slugs)} finding(s)\n")
    for slug in held[0].slugs:
        sys.stdout.write(f"  {slug or '(no slug)'}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
