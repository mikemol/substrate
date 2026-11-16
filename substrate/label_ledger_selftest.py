#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.label_ledger` — the window, and what an absent row means.

⚑⚑ THE STAMPLESS-ROW CASE IS THE ONE THAT PREVENTS A FALSE PASS. Rows predating the timestamp
column carry an empty field, and a reader that coerced those to "now" (or ignored the column
when absent) would report a years-old run as a fresh one — a freshness gate that cannot fail.
The conservative direction is epoch-0, and only a case says so.

⚑ AND THE CUTOFF IS ABSOLUTE IN EVERY CASE HERE, never `30m`, so no case depends on when it
runs. A duration-based fixture would pass today and fail whenever the fixture aged past the
window — a test whose verdict moves without the code moving.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import label_ledger

# The fixture's two stamps, named so an assertion and its message cannot drift apart.
_NEW, _OLD = 3000, 1000

# A window cutoff between them.
_CUT = 2500

# A bare epoch spec and its value — the absolute spelling of a window.
_EPOCH = 1234

# A fixture ledger. Columns: label, wall, peak, stamp, usr, sys — as `_record_time` writes them.
# ⚑ THE FOURTH ROW HAS NO STAMP, which is the shape rows written before that column carry.
_FIXTURE = (
    f"selftest:a.py\t1.5\t20\t2000\t0.9\t0.2\n"
    f"selftest:a.py\t2.0\t30\t{_NEW}\t1.1\t0.3\n"
    f"selftest:b.py\t0.5\t10\t{_OLD}\t0.2\t0.1\n"
    f"selftest:old.py\t0.5\t10\t\t\t\n"
    f"claim:pg\t9.0\t99\t{_NEW}\t8.0\t0.5\n"
)


def _ledger(d: str) -> Path:
    """Write the fixture ledger and return its path."""
    path = Path(d) / "labels.tsv"
    path.write_text(_FIXTURE, encoding="utf-8")
    return path


def window_excludes_older(out: list[str]) -> int:
    """Check a cutoff drops runs that finished before it."""
    with tempfile.TemporaryDirectory() as d:
        got = label_ledger.runs(_ledger(d), since=_CUT)
    labels = sorted(r.label for r in got)
    if labels != ["claim:pg", "selftest:a.py"]:
        out.append(f"selftest: a window since={_CUT} returned {labels}")
        return 1
    return 0


def stampless_row_is_never_fresh(out: list[str]) -> int:
    """Check a row with no timestamp stays out of every window.

    ⚑ THE FALSE-PASS CASE. A stampless row admitted into a window would let a suite that has
    not run in months satisfy a freshness gate, and the gate would look green while measuring
    nothing.
    """
    with tempfile.TemporaryDirectory() as d:
        path = _ledger(d)
        fresh = label_ledger.runs(path, prefix="selftest:old.py", since=1)
        always = label_ledger.runs(path, prefix="selftest:old.py")
    bad = 0
    if fresh:
        out.append("selftest: a stampless row was admitted into a window")
        bad += 1
    if not always:
        out.append("selftest: a stampless row is invisible even with no window")
        bad += 1
    return bad


def prefix_selects_a_class(out: list[str]) -> int:
    """Check the label prefix selects a namespace, matching `membudget peaks`."""
    with tempfile.TemporaryDirectory() as d:
        got = label_ledger.runs(_ledger(d), prefix="claim:")
    if len(got) != 1 or got[0].label != "claim:pg":
        out.append(f"selftest: prefix 'claim:' returned {[r.label for r in got]}")
        return 1
    return 0


def latest_is_the_newest_not_the_last(out: list[str]) -> int:
    """Check `latest` picks by timestamp, not by file order.

    ⚑ THE LEDGER IS APPEND-ORDERED IN PRACTICE AND NOTHING GUARANTEES IT. Two runs of one
    suite can land out of order (a retry after an OOM, a replayed row), so a reader taking
    "the last line wins" would report the older run's cost as current.
    """
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "labels.tsv"
        path.write_text(
            f"selftest:a.py\t2.0\t30\t{_NEW}\t1\t0\nselftest:a.py\t1.0\t10\t{_OLD}\t1\t0\n",
            encoding="utf-8",
        )
        got = label_ledger.latest(path)
    run = got.get("selftest:a.py")
    if run is None or run.stamp != _NEW:
        out.append(f"selftest: latest picked {None if run is None else run.stamp}")
        return 1
    return 0


def missing_ledger_is_empty_not_an_error(out: list[str]) -> int:
    """Check an absent ledger reads as no runs.

    ⚑ A MACHINE THAT HAS NEVER RUN A LEASED COMMAND HAS NO LEDGER, and that is a legitimate
    state, not a failure. The CALLER decides what an empty history means; raising here would
    make every reader handle it as an exception.
    """
    with tempfile.TemporaryDirectory() as d:
        got = label_ledger.runs(Path(d) / "nothing-here.tsv")
    if got != []:
        out.append(f"selftest: a missing ledger returned {got}")
        return 1
    return 0


def since_parses_durations_and_epochs(out: list[str]) -> int:
    """Check both window spellings, against a pinned `now`."""
    bad = 0
    if label_ledger.parse_since("30m", now=10_000) != 10_000 - 1800:
        out.append("selftest: '30m' did not parse as 1800 seconds back")
        bad += 1
    if label_ledger.parse_since("2h", now=10_000) != 10_000 - 7200:
        out.append("selftest: '2h' did not parse as 7200 seconds back")
        bad += 1
    if label_ledger.parse_since(str(_EPOCH)) != _EPOCH:
        out.append("selftest: a bare integer did not parse as an absolute epoch")
        bad += 1
    return bad


_ARMS = (
    window_excludes_older,
    stampless_row_is_never_fresh,
    prefix_selects_a_class,
    latest_is_the_newest_not_the_last,
    missing_ledger_is_empty_not_an_error,
    since_parses_durations_and_epochs,
)

_CASE_COUNT = 1 + 2 + 1 + 1 + 1 + 3


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"label-ledger selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"label-ledger selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
