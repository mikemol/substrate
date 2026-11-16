#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.baseline_io` — baseline persistence and move-splitting.

⚑⚑ THE CASES LIVED INLINE IN `baseline_io.py` UNTIL ⟡n-split-the-tails. Operator: *"n-split
that crap. No more in-line/tail testing."* An inline suite is DEBT, not a convention: its cases
cannot run without importing the module under test, they inflate the file the per-file gate
measures, and a module too dirty to edit takes its own suite hostage — `toolmodes.py`, 615
inline lines inside 3,700 that no edit can touch, is where the shape ends.

⚑ WHAT THE ARMS PIN, in one line each: a baseline ROUND-TRIPS (a file that reads back
differently silently relabels debt, and a paydown-only ratchet banks the phantom permanently);
an EMPTY baseline reads as empty rather than absent (the zero-tolerance setting, not the
vacuous green); explicit intent beats the environment in `may_write`; and `split_moves` credits
only a ONE-TO-ONE relocation, so growth can never be laundered through the decomposition
channel.

⚑ `_ident` MOVED WITH THE ARMS BECAUSE IT WAS ONLY EVER THEIR GRAMMAR. Measured before the
split: 1 def, 3 refs, all three inside `selftest` — the key grammar a real gate supplies is its
own, and this is the test's stand-in for it.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate.baseline_io import may_write, read_baseline, split_moves, write_baseline


def _ident(key: str) -> str:
    """Return a `<path>::<name>` key's name half — the test grammar for a move."""
    return key.split("::")[1]


def selftest() -> int:
    """Pin the persistence and move-splitting properties."""
    cases: list[tuple[str, bool, str]] = []

    def equals(label: str, got: object, want: object) -> None:
        cases.append((label, got == want, f"{got!r} != {want!r}"))

    def holds(label: str, *, got: bool) -> None:
        cases.append((label, got is True, f"{got!r} is not True"))

    def denies(label: str, *, got: bool) -> None:
        cases.append((label, got is False, f"{got!r} is not False"))

    # ⚑ A ROUND-TRIP, because a baseline that reads back differently than it was written
    # silently relabels debt: the next run sees phantom additions AND phantom paydown,
    # and a paydown-only ratchet banks the phantom permanently.
    with tempfile.TemporaryDirectory() as d:
        p = str(Path(d) / "b.txt")
        write_baseline(p, {"c::3", "a::1", "b::2"})
        equals("a baseline round-trips", read_baseline(p), {"a::1", "b::2", "c::3"})
        # ⚑ AN EMPTY BASELINE IS THE ZERO-TOLERANCE SETTING, NOT AN ABSENT ONE. Reading
        # it as absent would take the record-and-pass branch — the vacuous green that
        # `BaselineState.ABSENT` exists to name.
        write_baseline(p, set())
        equals("...and an empty one reads as empty, not absent", read_baseline(p), set())

    # ⚑ EXPLICIT INTENT WINS OVER THE ENVIRONMENT, so a non-CLI caller is not at the
    # mercy of whatever the commit hook happened to export.
    holds("an explicit write is permitted", got=may_write(write=True))
    denies("an explicit refusal is honoured", got=may_write(write=False))

    # ⚑⚑ ONE-TO-ONE ONLY. Crediting a 1->N fan-out would launder real growth through the
    # decomposition channel — the swap-gaming the SET form exists to catch.
    moved, rest = split_moves({"b.agda::X"}, {"a.agda::X"}, _ident)
    equals("a 1:1 relocation is credited as a move", moved, {("a.agda::X", "b.agda::X")})
    equals("...and is not reported as an addition", rest, set())

    fan, rest = split_moves({"b::X", "c::X"}, {"a::X"}, _ident)
    equals("a 1->N fan-out is NOT a move", fan, set())
    equals("...and stays visible as growth", rest, {"b::X", "c::X"})

    # ⚑ THE TOTAL CANNOT RISE THROUGH THIS PATH: each move consumes exactly one removal.
    m2, a2 = split_moves({"b::X", "z::N"}, {"a::X"}, _ident)
    equals(
        "a move consumes its removal, so the count cannot grow",
        (len(m2), sorted(a2)),
        (1, ["z::N"]),
    )

    # ⚑ AND NO `key_move` MEANS NO CHANGE AT ALL — a gate that opts out is untouched.
    equals(
        "without a key_move nothing is credited",
        split_moves({"b::X"}, {"a::X"}, None),
        (set(), {"b::X"}),
    )

    failed = [(n, d) for n, good, d in cases if not good]
    for n, d in failed:
        sys.stderr.write(f"  FAIL {n}: {d}\n")
    sys.stdout.write(f"baseline_io selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


# ⚑⚑ THE FLAG IS NAMED SO `run_selftests.discover()` CAN SEE THIS SUITE (⟡selftest-discovery).
# Discovery requires an entry point AND the literal `--selftest` somewhere in the file — the
# closest static proxy for *"`python <path> --selftest` produces a result"*, which is what the
# runner actually invokes. This module ran the suite unconditionally and answered that
# invocation correctly, yet matched no proxy, so it was INVISIBLE to the runner while passing.
#
# ⚑ MEASURED: ten of eleven promoted modules were missing this way, and the ONE that was
# discovered (`proc_ancestry`) qualified BY ACCIDENT — the literal appears in its prose, not in
# its dispatch. A population that admits on a docstring is not measuring what it claims to.
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
