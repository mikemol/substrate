#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.census_currency` — absent, stale, current and unmeasured.

⚑⚑⚑ THE THREE-WAY SPLIT IS THE ITEM. The origin returned `(ok, detail)`, so a caller branching
on the flag could not tell a census that has NEVER RUN from one that has GONE STALE — a census to
run versus a census to re-run, with the difference living only in prose the branch never reads.
The arms below pin each state as its own verdict.

⚑⚑ AND THE FOURTH STATE IS THE ONE THE ORIGIN COULD NOT EXPRESS AT ALL. If the tree cannot be
fingerprinted, the comparison did not happen — reporting that as STALE would blame the ledger for
a defect in the reader. Unmeasured is not stale, the same way unreachable is not zero.

⚑ THE FIXTURES ARE TEMP LEDGERS AND FAKE STAMPERS. A case reading the live ledger measures
today's build state: it is CURRENT right now, so a case pinning that would go red the moment
anyone touches a `.agda` file — reporting ordinary work as a defect in this reader.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import census_currency, corpus

# What a healthy ledger's first line looks like.
_STAMP = "3599:1787794131"
_HEADER = f"#stamp {_STAMP}\n"

# A stamp from a tree that has since moved.
_MOVED = "3600:1787799999"


class _Stamper:
    """A stamper returning the fingerprint the case chose."""

    def __init__(self, stamp: str) -> None:
        self._stamp = stamp
        self.asked: list[str] = []

    def tree_stamp(self, root: str = "agda") -> str:
        """Record the root asked about and return the fixture stamp."""
        self.asked.append(root)
        return self._stamp


def _with_ledger(where: str, text: str | None) -> None:
    """Point the reader at a temp root, optionally writing a ledger into it."""
    corpus.ROOT = Path(where)
    if text is None:
        return
    path = Path(where).joinpath(*census_currency.LEDGER)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _currency_with(text: str | None, stamp: str | None) -> census_currency.Currency:
    """Run the reader against a fixture ledger and stamper."""

    def _load() -> tuple[census_currency.Stamper | None, str]:
        if stamp is None:
            return None, "split_census will not load: no tool at scratch/split_census.py"
        return _Stamper(stamp), ""

    original_root = corpus.ROOT
    original_stamper = census_currency.stamper
    census_currency.stamper = _load
    try:
        with tempfile.TemporaryDirectory() as where:
            _with_ledger(where, text)
            return census_currency.currency()
    finally:
        corpus.ROOT = original_root
        census_currency.stamper = original_stamper


def a_missing_ledger_is_absent(out: list[str]) -> int:
    """Check no ledger reports ABSENT, not stale."""
    got = _currency_with(None, _STAMP)
    if got.state is not census_currency.State.ABSENT:
        out.append(f"selftest: a missing ledger read as {got.state!r}")
        return 1
    return 0


def a_missing_ledger_says_the_census_never_ran(out: list[str]) -> int:
    """Check the absent reason distinguishes it from a stale one.

    ⚑⚑ THE DISTINCTION THE BOOLEAN LOST. *"Run the census"* and *"re-run the census"* are
    different instructions, and a caller reading only a flag receives neither.
    """
    got = _currency_with(None, _STAMP)
    if "never run" not in got.why:
        out.append(f"selftest: the absent reason reads as {got.why!r}")
        return 1
    return 0


def a_ledger_with_no_stamp_is_absent(out: list[str]) -> int:
    """Check a ledger whose first line carries no stamp is not read as current.

    ⚑ A FILE ON DISK IS NOT A MEASUREMENT. A ledger without a stamp cannot say which tree it
    describes, so treating its presence as currency would license reading every figure in it.
    """
    got = _currency_with("module\tverdict\n", _STAMP)
    if got.state is not census_currency.State.ABSENT:
        out.append(f"selftest: an unstamped ledger read as {got.state!r}")
        return 1
    return 0


def a_matching_stamp_is_current(out: list[str]) -> int:
    """Check equal stamps report CURRENT."""
    got = _currency_with(_HEADER, _STAMP)
    if got.state is not census_currency.State.CURRENT or not got.readable:
        out.append(f"selftest: a matching stamp read as {got.state!r}")
        return 1
    return 0


def a_differing_stamp_is_stale(out: list[str]) -> int:
    """Check a moved tree reports STALE — the POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS, A READER CALLING EVERYTHING CURRENT passes the case above and licenses every
    downstream figure forever. The pair says the comparison actually discriminates.
    """
    got = _currency_with(_HEADER, _MOVED)
    if got.state is not census_currency.State.STALE or got.readable:
        out.append(f"selftest: a moved tree read as {got.state!r}")
        return 1
    return 0


def a_stale_verdict_carries_both_stamps(out: list[str]) -> int:
    """Check the staleness names what was recorded and what the tree is now.

    ⚑ A BARE *"STALE"* IS NOT ACTIONABLE. The two stamps are what let a reader see whether the
    tree moved by one file or by a thousand.
    """
    got = _currency_with(_HEADER, _MOVED)
    if got.recorded != _STAMP or got.tree != _MOVED:
        out.append(f"selftest: the stale verdict carries {got.recorded!r}, {got.tree!r}")
        return 1
    if _STAMP not in got.why or _MOVED not in got.why:
        out.append(f"selftest: the stale reason omits a stamp: {got.why!r}")
        return 1
    return 0


def a_stale_verdict_says_the_figures_are_fiction(out: list[str]) -> int:
    """Check the consequence is stated, not left to the reader.

    ⚑ THE ITEM EXISTS BECAUSE DOWNSTREAM FIGURES INHERIT THIS. A verdict that reports staleness
    without saying what it invalidates gets read as a warning rather than a stop.
    """
    got = _currency_with(_HEADER, _MOVED)
    if "fiction" not in got.why:
        out.append(f"selftest: the stale reason does not name the consequence: {got.why!r}")
        return 1
    return 0


def an_unloadable_stamper_is_unmeasured(out: list[str]) -> int:
    """Check a tree that cannot be fingerprinted reports UNMEASURED, not stale.

    ⚑⚑⚑ THE STATE THE ORIGIN COULD NOT EXPRESS. Blaming the ledger for the reader's inability to
    measure is the same shape as reading an unreachable store as an empty one.
    """
    got = _currency_with(_HEADER, None)
    if got.state is not census_currency.State.UNMEASURED:
        out.append(f"selftest: an unloadable stamper read as {got.state!r}")
        return 1
    if got.readable:
        out.append("selftest: an unmeasured ledger was reported readable")
        return 1
    return 0


def an_unmeasured_verdict_keeps_the_recorded_stamp(out: list[str]) -> int:
    """Check what WAS read is still reported when the comparison fails.

    ⚑ THE HALF THAT SUCCEEDED IS STILL A FACT. Discarding the recorded stamp because the other
    half failed throws away the only evidence the reader actually has.
    """
    got = _currency_with(_HEADER, None)
    if got.recorded != _STAMP:
        out.append(f"selftest: the unmeasured verdict lost the recorded stamp: {got.recorded!r}")
        return 1
    if got.tree is not None:
        out.append(f"selftest: the unmeasured verdict invented a tree stamp: {got.tree!r}")
        return 1
    return 0


def the_stamper_is_asked_about_the_declared_tree(out: list[str]) -> int:
    """Check the fingerprint is taken of the tree this module names.

    ⚑ A ROOT TYPED AT THE CALL SITE is how a reader starts comparing a ledger against a tree its
    own constant does not name.
    """
    probe = _Stamper(_STAMP)

    def _load() -> tuple[census_currency.Stamper | None, str]:
        return probe, ""

    original_root = corpus.ROOT
    original_stamper = census_currency.stamper
    census_currency.stamper = _load
    try:
        with tempfile.TemporaryDirectory() as where:
            _with_ledger(where, _HEADER)
            census_currency.currency()
    finally:
        corpus.ROOT = original_root
        census_currency.stamper = original_stamper

    if probe.asked != [census_currency.TREE]:
        out.append(f"selftest: the stamper was asked about {probe.asked!r}")
        return 1
    return 0


def the_ledger_path_is_named_once(out: list[str]) -> int:
    """Check the path is derived from the declared parts."""
    if not census_currency.ledger_path().endswith("/".join(census_currency.LEDGER)):
        out.append(f"selftest: the ledger path is {census_currency.ledger_path()!r}")
        return 1
    return 0


def every_state_renders_distinguishably(out: list[str]) -> int:
    """Check the four verdicts do not render as the same line.

    ⚑ A RENDER THAT COLLAPSES TWO STATES undoes the split at the last step, where the reader
    actually looks.
    """
    seen = {
        census_currency.render(
            census_currency.Currency(state=state, recorded=None, tree=None, why="x")
        )
        for state in census_currency.State
    }
    if len(seen) != len(census_currency.State):
        out.append(f"selftest: the states render to {len(seen)} distinct line(s)")
        return 1
    return 0


_ARMS = (
    a_missing_ledger_is_absent,
    a_missing_ledger_says_the_census_never_ran,
    a_ledger_with_no_stamp_is_absent,
    a_matching_stamp_is_current,
    a_differing_stamp_is_stale,
    a_stale_verdict_carries_both_stamps,
    a_stale_verdict_says_the_figures_are_fiction,
    an_unloadable_stamper_is_unmeasured,
    an_unmeasured_verdict_keeps_the_recorded_stamp,
    the_stamper_is_asked_about_the_declared_tree,
    the_ledger_path_is_named_once,
    every_state_renders_distinguishably,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 2 + 1 + 2 + 2 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"census-currency selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"census-currency selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
