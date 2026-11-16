#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report which modules have no suite — the CLI for `substrate.suite_gap`.

⚑ THE READER IS SEPARATE FROM THE COMPUTATION for the reason every census here is: a gate wanting
the population must not have to parse printed text, and a printer must not re-derive predicates.

    suite_gap_report.py                 # the whole package
    suite_gap_report.py <name> [...]    # only these modules — the batch question
"""

from __future__ import annotations

import sys

from substrate import corpus, suite_gap


def main(argv: list[str]) -> int:
    """Print the coverage split, for the whole package or for a named batch."""
    base = corpus.ROOT / "substrate"
    names = [arg for arg in argv if not arg.startswith("-")]
    if names:
        found = suite_gap.uncovered_among(names, directory=base)
        sys.stdout.write(
            f"{len(names) - len(found)}/{len(names)} named module(s) have a suite; "
            f"{len(found)} do not\n"
        )
        sys.stdout.writelines(f"   {name}\n" for name in found)
        # ⚑⚑ THE BOUNDS REACH THIS BRANCH TOO. It built its own summary and returned, so asking
        # about a named batch emitted no caveat at all (gate-G343) — and this is the branch a
        # reader uses when weighing a change they just made, which is when it matters most.
        sys.stdout.writelines(f"{line}\n" for line in suite_gap.bounds())
        return 0
    sys.stdout.write(suite_gap.render(suite_gap.coverage(base)) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
