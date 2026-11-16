#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.reach_ratchet` — and the keyword-only call that motivated it.

⚑⚑⚑ THE ABSENT-SUITE ARM IS THE ONE THAT MATTERS. A suite that aborted reports nothing, and
recording that as `reached = 0` would BANK the abort as the new reading — the ratchet
laundering exactly the defect it exists to catch, permanently, on the first run after the
incident. Every other arm here would pass against an implementation that zeroed absent rows.

⚑ THE `may_write` ARM PINS THE REGRESSION THIS MODULE WAS EXTRACTED TO FIX. ⟡gate-island-promote
left a positional call into a keyword-only function, crashing `run_selftests --selftest` with
`TypeError`. The case does not test the spelling — it tests that a read is READ-ONLY, which is
the property the spelling protects.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

from substrate.reach_baseline import Reading, read_reach, write_reach
from substrate.reach_ratchet import reach_ratchet

_PASS = 0
_REGRESSED = 1

# A recorded census: one counted suite, one whose source could not be counted.
_BASE: dict[str, Reading] = {"a.py": (50, 48), "b.py": (10, None)}


def _fixture(d: str) -> str:
    """Write `_BASE` to a fresh baseline and return its path."""
    path = str(Path(d) / "reach.tsv")
    write_reach(path, _BASE)
    return path


def absent_suite_survives(out: list[str]) -> int:
    """Check a suite missing from `observed` keeps its recorded row.

    ⚑ THE SINGLE MOST IMPORTANT PROPERTY, and the opposite of what a naive implementation
    does. `b.py` reported nothing this run; its row must be carried forward UNTOUCHED rather
    than recorded as zero.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        path = _fixture(d)
        os.environ["SUBSTRATE_RATCHET_WRITE"] = "1"
        try:
            rc = reach_ratchet({"a.py": (55, 48)}, path, quiet=True)
        finally:
            os.environ.pop("SUBSTRATE_RATCHET_WRITE", None)
        after = read_reach(path)
    if rc != _PASS:
        out.append(f"selftest: growth was refused (rc={rc})")
        bad += 1
    if after.get("b.py") != (10, None):
        out.append(f"selftest: an absent suite's row was not carried forward: {after!r}")
        bad += 1
    if after.get("a.py") != (55, 48):
        out.append(f"selftest: the reporting suite's row did not advance: {after!r}")
        bad += 1
    return bad


def regression_refuses(out: list[str]) -> int:
    """Check fewer cases reached, with the call sites still present, REFUSES."""
    with tempfile.TemporaryDirectory() as d:
        path = _fixture(d)
        rc = reach_ratchet({"a.py": (40, 48)}, path, quiet=True)
    if rc != _REGRESSED:
        out.append(f"selftest: a shrunken census returned {rc}, not {_REGRESSED}")
        return 1
    return 0


def regression_does_not_record(out: list[str]) -> int:
    """Check a run with any regression banks NOTHING, including its growth.

    ⚑ RECORDING A MIXED RUN WOULD BANK THE GROWTH and leave the regression un-refusable next
    time — the same rule as `set_ratchet`'s "paydown cannot record while a new key is present".
    """
    with tempfile.TemporaryDirectory() as d:
        path = _fixture(d)
        before = Path(path).read_text(encoding="utf-8")
        os.environ["SUBSTRATE_RATCHET_WRITE"] = "1"
        try:
            reach_ratchet({"a.py": (40, 48), "c.py": (9, 9)}, path, quiet=True)
        finally:
            os.environ.pop("SUBSTRATE_RATCHET_WRITE", None)
        after = Path(path).read_text(encoding="utf-8")
    if after != before:
        out.append("selftest: a run with a regression rewrote the baseline")
        return 1
    return 0


def read_is_read_only(out: list[str]) -> int:
    """Check a run without write permission records nothing.

    ⚑⚑ THIS IS THE PROPERTY THE `may_write` SPELLING PROTECTS, and the reason this module
    exists. The read-mutates-state defect was MEASURED TWICE — a plain `--quiet` run rewrote a
    baseline 48 -> 45, once during an audit explicitly forbidden to write. The extraction was
    forced because the positional call into a keyword-only resolver crashed the caller; the
    case pins the guarantee rather than the syntax.
    """
    with tempfile.TemporaryDirectory() as d:
        path = _fixture(d)
        before = Path(path).read_text(encoding="utf-8")
        saved = os.environ.pop("SUBSTRATE_RATCHET_WRITE", None)
        try:
            reach_ratchet({"a.py": (55, 48)}, path, quiet=True)
        finally:
            if saved is not None:
                os.environ["SUBSTRATE_RATCHET_WRITE"] = saved
        after = Path(path).read_text(encoding="utf-8")
    if after != before:
        out.append("selftest: a read without write permission rewrote the baseline")
        return 1
    return 0


def explicit_refusal_beats_environment(out: list[str]) -> int:
    """Check `write=False` refuses even when the environment permits.

    ⚑ EXPLICIT INTENT WINS, so a non-CLI caller is not at the mercy of whatever the commit
    hook happened to export.
    """
    with tempfile.TemporaryDirectory() as d:
        path = _fixture(d)
        before = Path(path).read_text(encoding="utf-8")
        os.environ["SUBSTRATE_RATCHET_WRITE"] = "1"
        try:
            reach_ratchet({"a.py": (55, 48)}, path, quiet=True, write=False)
        finally:
            os.environ.pop("SUBSTRATE_RATCHET_WRITE", None)
        after = Path(path).read_text(encoding="utf-8")
    if after != before:
        out.append("selftest: an explicit write=False was overridden by the environment")
        return 1
    return 0


def uncountable_drop_refuses(out: list[str]) -> int:
    """Check a drop whose source cannot be counted refuses as UNKNOWN.

    ⚑ A DROP NOBODY CAN CLASSIFY IS THE CASE THIS GATE EXISTS FOR. Passing it would make the
    gate's green a fact about the instrument.
    """
    with tempfile.TemporaryDirectory() as d:
        path = _fixture(d)
        rc = reach_ratchet({"b.py": (5, None)}, path, quiet=True)
    if rc != _REGRESSED:
        out.append(f"selftest: an unclassifiable drop returned {rc}, not {_REGRESSED}")
        return 1
    return 0


_ARMS = (
    absent_suite_survives,
    regression_refuses,
    regression_does_not_record,
    read_is_read_only,
    explicit_refusal_beats_environment,
    uncountable_drop_refuses,
)

_CASE_COUNT = 3 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"reach-ratchet selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"reach-ratchet selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
