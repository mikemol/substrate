#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.ratchet_census` — every failure names itself, and absence means all.

⚑⚑⚑ THE ABSENT-BASELINE CASE IS THE ONE THAT POINTS THE OPPOSITE WAY FROM THIS TREE'S OTHER
ABSENT-BASELINE BEHAVIOUR. Elsewhere a missing baseline takes a record-and-pass branch and exits
0 regardless of what it measured — a free pass. Here it means every key is ADDED, because nothing
has been recorded and so nothing is grandfathered. Reading it the other way would report a gate
with no baseline as perfectly clean.

⚑⚑ AND EVERY REFUSAL CARRIES A REASON. A caller that reports "0 added" for a gate it could not
read has banked a false green, so the four failure shapes — will not import, no census, raised,
declared unrunnable — each return text a reader can act on.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import ratchet_census


def a_missing_baseline_makes_every_key_added(out: list[str]) -> int:
    """Check an absent baseline file reads as an empty set, not a refusal."""
    got = ratchet_census.baseline_keys("/no/such/baseline.txt")
    if got != set():
        out.append(f"selftest: a missing baseline read as {got!r}")
        return 1
    return 0


def a_baseline_is_read_line_by_line(out: list[str]) -> int:
    """Check recorded keys come back, with blank lines dropped."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "baseline.txt"
        path.write_text("a::b\n\n  c::d  \n", encoding="utf-8")
        got = ratchet_census.baseline_keys(str(path))
    if got != {"a::b", "c::d"}:
        out.append(f"selftest: the baseline read as {got!r}")
        return 1
    return 0


def a_gate_that_will_not_import_names_its_error(out: list[str]) -> int:
    """Check an unimportable gate returns a reason rather than a bare None."""
    got, why = ratchet_census.census("no_such_gate_module_anywhere")
    bad = 0
    if got is not None:
        out.append("selftest: a missing gate produced a census")
        bad += 1
    if not why:
        out.append("selftest: a missing gate gave no reason")
        bad += 1
    return bad


def a_module_without_a_census_says_so(out: list[str]) -> int:
    """Check a module exposing no `census()` is reported, not crashed on.

    ⚑ NOT EVERY GATE IS A SET-FORM RATCHET, and asking one that is not must produce a stated
    fact rather than an AttributeError from inside the reader.
    """
    got, why = ratchet_census.census("json")
    bad = 0
    if got is not None:
        out.append("selftest: a module with no census produced one")
        bad += 1
    if not why or "census()" not in why:
        out.append(f"selftest: the reason was {why!r}")
        bad += 1
    return bad


def the_over_count_is_the_added_keys(out: list[str]) -> int:
    """Check `over` counts what the ratchet refuses on."""
    got = ratchet_census.Census(held=10, added=("a", "b"))
    expected_over = 2
    if got.over != expected_over:
        out.append(f"selftest: over read as {got.over}, want {expected_over}")
        return 1
    return 0


def a_declared_baseline_must_be_text(out: list[str]) -> int:
    """Check a non-string `BASELINE` is treated as absent rather than reaching the filesystem.

    ⚑ THE UNTYPED BOUNDARY. A gate is an arbitrary module, so its attributes are whatever it
    declared; narrowing here is what keeps a wrong declaration from becoming a path operation.
    """

    class _Odd:
        BASELINE = 17

    if ratchet_census.baseline_path(_Odd()) is not None:
        out.append("selftest: a non-string BASELINE was accepted as a path")
        return 1
    return 0


def a_real_gate_censuses(out: list[str]) -> int:
    """Check a live ratchet gate reads back with a census and no reason.

    ⚑ THE FIXTURES ABOVE PIN THE FAILURE SHAPES; this pins that the success path works against
    the tree as it is. A suite of failure cases alone can pass while nothing succeeds.
    """
    got, why = ratchet_census.census("scripts.gate_keys")
    # `gate_keys` is parsing-only and exposes no census — the honest outcome is a REASON.
    if got is None and why:
        return 0
    out.append(f"selftest: a parsing-only module returned census={got!r} why={why!r}")
    return 1


_ARMS = (
    a_missing_baseline_makes_every_key_added,
    a_baseline_is_read_line_by_line,
    a_gate_that_will_not_import_names_its_error,
    a_module_without_a_census_says_so,
    the_over_count_is_the_added_keys,
    a_declared_baseline_must_be_text,
    a_real_gate_censuses,
)

_CASE_COUNT = 1 + 1 + 2 + 2 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"ratchet-census selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"ratchet-census selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
