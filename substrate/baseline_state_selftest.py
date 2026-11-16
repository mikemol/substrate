#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.baseline_state` — the four-state baseline vocabulary.

⚑⚑ THE CASES LIVED INLINE IN `baseline_state.py` UNTIL ⟡n-split-the-tails. Operator: *"n-split
that crap. No more in-line/tail testing."* An inline suite is DEBT, not a convention: its cases
cannot run without importing the module under test, they inflate the file the per-file gate
measures, and a module too dirty to edit takes its own suite hostage.

⚑ WHAT THE ARMS PIN, in one line each: the lift is ADDITIVE (a state equals, formats and hashes
as its bare name, so six readers migrate one at a time instead of in one flag-day edit); it is
ORDERED, because the first cut made `sorted()` a TypeError and a lift that breaks ordering has
MOVED the breakage rather than removed it; the two properties are INDEPENDENT, so no single
`!= "ok"` can flatten the 2-bit space in the direction that reads the strongest setting as debt;
the roster IS the definition, so nothing can be omitted the way a hand-typed tuple omitted
UNREAD; and an unknown name REFUSES rather than defaulting to `ok`.
"""

from __future__ import annotations

import sys

from substrate.baseline_state import BaselineState


def selftest() -> int:
    """Pin the vocabulary's properties."""
    cases: list[tuple[str, bool, str]] = []

    def equals(label: str, got: object, want: object) -> None:
        cases.append((label, got == want, f"{got!r} != {want!r}"))

    def holds(label: str, *, got: bool) -> None:
        cases.append((label, got is True, f"{got!r} is not True"))

    def denies(label: str, *, got: bool) -> None:
        cases.append((label, got is False, f"{got!r} is not False"))

    # ⚑ THE ADDITIVE PROPERTY: a bare-string call site must keep working, which is what
    # lets six readers migrate one at a time rather than in one flag-day edit.
    holds("a state equals its own name", got=BaselineState.EMPTY == "EMPTY")
    holds("...and formats as it", got=f"{BaselineState.ABSENT}" == "ABSENT")
    equals("...and hashes with it", len({BaselineState.OK, "ok"}), 1)

    # ⚑ SORTABLE, because the first cut made `sorted()` a TypeError. A lift that keeps
    # `==` working and breaks ordering has MOVED the breakage, not removed it.
    equals(
        "a mixed set of states and strings sorts",
        [str(s) for s in sorted({BaselineState.OK, BaselineState.EMPTY})],
        ["EMPTY", "ok"],
    )

    # ⚑⚑ THE TWO PROPERTIES ARE INDEPENDENT, AND THIS IS THE ARM THAT PROVES IT. Any
    # single `!= "ok"` predicate flattens the 2-bit space to 1 bit, always in the
    # direction that reads the STRONGEST setting as debt — which is how EMPTY rows came
    # to be marked as degraded two lines beneath a legend calling them the strong setting.
    denies("EMPTY is not a defect", got=BaselineState.EMPTY.is_defect)
    denies("...and deserves no mark", got=BaselineState.EMPTY.deserves_mark)
    holds("ABSENT is a defect", got=BaselineState.ABSENT.is_defect)
    denies("UNREAD is NOT a defect", got=BaselineState.UNREAD.is_defect)
    holds("...but still deserves a mark", got=BaselineState.UNREAD.deserves_mark)

    # ⚑ THE ROSTER IS THE DEFINITION. A hand-typed tuple omitted UNREAD and would have
    # failed a suite on a genuine UNREAD row, claiming the state was wrong.
    equals("every declared state is in the roster", len(BaselineState.all()), 4)
    holds(
        "...including the one a hand-typed roster omitted",
        got=BaselineState.UNREAD in BaselineState.all(),
    )

    # ⚑ AND AN UNKNOWN NAME RAISES RATHER THAN DEFAULTING. Falling back to `ok` would
    # re-create the exact false-green this vocabulary exists to prevent.
    equals("a known name resolves", BaselineState.of("ABSENT"), BaselineState.ABSENT)
    try:
        BaselineState.of("nonesuch")
        cases.append(("an unknown name REFUSES rather than defaulting", False, "no raise"))
    except KeyError as e:
        holds("an unknown name REFUSES rather than defaulting", got="known:" in str(e))

    failed = [(n, d) for n, good, d in cases if not good]
    for n, d in failed:
        sys.stderr.write(f"  FAIL {n}: {d}\n")
    sys.stdout.write(f"baseline_state selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE — see
# `baseline_io_selftest`'s note (⟡selftest-discovery): ten promoted modules ran correctly and
# were invisible to the runner, because discovery keys on the literal `--selftest` appearing in
# the file.
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
