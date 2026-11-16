#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.ledger_show` — flag parsing and age rendering.

⚑ THE UNSTAMPED CASE IS THE ONE THAT MATTERS. `label_ledger` uses epoch-0 as the sentinel for
a row written before the timestamp column existed, and a renderer that turned that into a
number would present an absence of measurement as a measurement — the same false-confidence
shape as a stampless row admitted into a freshness window.
"""

from __future__ import annotations

import sys

from substrate import ledger_show

# A pinned "now" so age rendering never depends on when the case runs.
_NOW = 1_000_000

# Offsets from `_NOW` for each rendering band.
_MINUTES, _HOURS, _DAYS = 600, 7200, 200_000


def flag_takes_both_spellings(out: list[str]) -> int:
    """Check `--x v` and `--x=v` both bind, and an absent flag binds nothing."""
    bad = 0
    if ledger_show.flag(["--since", "2h"], "--since") != "2h":
        out.append("selftest: '--since 2h' did not bind")
        bad += 1
    if ledger_show.flag(["--since=2h"], "--since") != "2h":
        out.append("selftest: '--since=2h' did not bind")
        bad += 1
    if ledger_show.flag(["--other", "x"], "--since") is not None:
        out.append("selftest: an absent flag bound anyway")
        bad += 1
    return bad


def trailing_flag_without_value_is_none(out: list[str]) -> int:
    """Check a value-bearing flag at the end of argv does not read past it."""
    if ledger_show.flag(["--since"], "--since") is not None:
        out.append("selftest: a trailing '--since' bound a value")
        return 1
    return 0


def age_renders_each_band(out: list[str]) -> int:
    """Check minutes, hours and days each render in their own unit."""
    bad = 0
    if ledger_show.age(_NOW - _MINUTES, _NOW) != "10m":
        out.append("selftest: a 600s age did not render as minutes")
        bad += 1
    if ledger_show.age(_NOW - _HOURS, _NOW) != "2h":
        out.append("selftest: a 7200s age did not render as hours")
        bad += 1
    if ledger_show.age(_NOW - _DAYS, _NOW) != "2d":
        out.append("selftest: a 200000s age did not render as days")
        bad += 1
    return bad


def unstamped_age_says_so(out: list[str]) -> int:
    """Check a stampless run renders as unstamped, not as an enormous age.

    ⚑ EPOCH-0 IS HOW `label_ledger` KEEPS AN UNSTAMPED ROW OUT OF EVERY WINDOW, so this
    renderer must not turn that sentinel into a number. `20000d` reads as a measurement; the
    truth is that nothing was measured.
    """
    if ledger_show.age(0, _NOW) != "unstamped":
        out.append("selftest: a stampless run rendered as an age")
        return 1
    return 0


_ARMS = (
    flag_takes_both_spellings,
    trailing_flag_without_value_is_none,
    age_renders_each_band,
    unstamped_age_says_so,
)

_CASE_COUNT = 3 + 1 + 3 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"ledger-show selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"ledger-show selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
