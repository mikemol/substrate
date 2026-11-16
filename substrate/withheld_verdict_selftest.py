#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.withheld_verdict` — the refusal-to-answer any instrument can need.

⚑ THE CASES LIVED INLINE IN `withheld_verdict.py` UNTIL ⟡n-split-the-tails. Operator: *"n-split
that crap. No more in-line/tail testing."* Inline cases cannot run without importing the module
under test, they inflate the file the per-file gate measures, and a module too dirty to edit
takes its own suite hostage.

⚑ WHAT THE ARMS PIN: the observed half is always present (cheap and always true), a MISSING cause
is stated as missing rather than left as an invitation to supply one, and a stated cause REPLACES
the not-measured notice rather than joining it — a message carrying both would contradict itself.
"""

from __future__ import annotations

import sys

from substrate.withheld_verdict import withheld


def selftest() -> int:
    """Pin the properties."""
    cases: list[tuple[str, bool, str]] = []

    def holds(label: str, *, got: bool) -> None:
        cases.append((label, got is True, f"{got!r} is not True"))

    # ⚑ THE OBSERVED HALF IS ALWAYS PRESENT — it is the part that is cheap and true.
    plain = withheld("probe", "is the store reachable", "connect() raised ECONNREFUSED")
    holds("the verdict names the instrument", got="probe" in plain)
    holds("...and the question asked", got="is the store reachable" in plain)
    holds("...and what was actually observed", got="ECONNREFUSED" in plain)
    holds("...and says WITHHELD, not failed", got="WITHHELD" in plain)

    # ⚑⚑ THE ABSENT-CAUSE ARM IS THE ONE THAT MATTERS, and it is a POSITIVE assertion
    # rather than the absence of a string. Three measured instruments withheld correctly
    # and then explained the gap with something they never saw; the cure is that a
    # missing cause is STATED as missing, so the next reader cannot read incompleteness
    # as an invitation to supply one.
    holds("a missing cause is named as NOT MEASURED", got="NOT MEASURED" in plain)
    holds("...and says why a guess would be worse", got="fabrication" in plain)

    # ⚑ AND A STATED CAUSE REPLACES IT RATHER THAN JOINING IT. Printing both would let a
    # checkable cause sit beside the disclaimer that no cause was measured — a message
    # contradicting itself, which is worse than either half alone.
    caused = withheld("probe", "q", "m", cause="the role lacks pg_read_all_settings")
    holds("a stated cause is shown", got="pg_read_all_settings" in caused)
    cases.append(("...and REPLACES the not-measured notice", "NOT MEASURED" not in caused, caused))

    failed = [(n, d) for n, good, d in cases if not good]
    for n, d in failed:
        sys.stderr.write(f"  FAIL {n}: {d}\n")
    sys.stdout.write(f"withheld_verdict selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery):
# discovery keys on the literal `--selftest` appearing in the file, and ten promoted modules once
# ran correctly while being invisible to the runner.
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
