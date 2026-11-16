#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.stamp_read` — absence, staleness, and the old empty stamps.

⚑⚑ THE EMPTY-STAMP CASE IS THE MIGRATION CASE. Every stamp written before the outcome moved
into it holds nothing, and a reader that raised or guessed on those would report a healthy tree
as broken on the first run after the change. They read as ABSENT — the same as never having
run, which is honest: neither carries a kind.

⚑ AND STALENESS IS mtime BECAUSE THAT IS `make`'s OWN PREDICATE. A second rule — a content
hash, a recorded population — would be one relation with two answers, which is the duplication
this cut exists to remove.
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

from substrate import stamp_read, suite_run

# A source mtime far enough back that a stamp written now is unambiguously newer.
_OLD = 1_000_000


def a_recorded_pass_reads_back(out: list[str]) -> int:
    """Check a stamp written by the wrapper parses into its fields."""
    got = stamp_read.parse(suite_run.stamp_body("fixture/p.py", "ok", 4, 4))
    if got != ("fixture/p.py", "ok", 4, 4):
        out.append(f"selftest: a written stamp parsed as {got!r}")
        return 1
    return 0


def an_empty_stamp_reads_as_absent(out: list[str]) -> int:
    """Check a stamp from the previous `touch` recipe is not mistaken for a result.

    ⚑ THE MIGRATION CASE. An empty file is what every pre-change stamp holds; reading it as a
    pass would bank a green verdict nothing measured.
    """
    if stamp_read.parse("") is not None:
        out.append("selftest: an empty stamp parsed as a result")
        return 1
    return 0


def a_malformed_stamp_reads_as_absent(out: list[str]) -> int:
    """Check a truncated or non-object stamp does not raise."""
    bad = 0
    for body in ('{"label": "a"', '"just a string"', '{"label": 1, "kind": "ok"}'):
        if stamp_read.parse(body) is not None:
            out.append(f"selftest: a malformed stamp parsed: {body!r}")
            bad += 1
    return bad


def a_stamp_older_than_its_source_is_stale(out: list[str]) -> int:
    """Check freshness is decided by mtime against the source.

    ⚑ THIS IS THE CACHE-MISS PREDICATE, and it is `make`'s. A suite edited after its last run
    has a stamp that no longer describes it — which the consumer treats as a miss to re-derive,
    not a failure to report.
    """
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "s.py"
        src.write_text("print('x')\n", encoding="utf-8")
        stamp = Path(d) / ("s.py" + stamp_read.SUFFIX)
        stamp.write_text(suite_run.stamp_body("s.py", "ok", 1, 1), encoding="utf-8")
        os.utime(stamp, (_OLD, _OLD))
        os.utime(src, (time.time(), time.time()))
        fresh = stamp.stat().st_mtime >= src.stat().st_mtime
    if fresh:
        out.append("selftest: a stamp older than its source read as fresh")
        return 1
    return 0


def a_missing_stamp_is_none(out: list[str]) -> int:
    """Check an absent stamp reads as None rather than raising.

    ⚑ AND THE ABSENCE HAS THREE CAUSES the reader cannot separate: never run, ran and failed
    (the wrapper stamps only on success), or cleaned. Reporting None is the honest answer;
    naming one cause would be an unestablished claim.
    """
    got = stamp_read.read("no/such/suite.py", "no/such/suite.py")
    if got is not None:
        out.append(f"selftest: a missing stamp read as {got!r}")
        return 1
    return 0


def the_path_matches_the_generator(out: list[str]) -> int:
    """Check the stamp path is spelled as the makefile generator spells its targets.

    ⚑ TWO SPELLINGS OF ONE PATH IS A READER THAT SILENTLY FINDS NOTHING — the census-keyed-on-
    one-spelling shape, applied to a filename.
    """
    got = stamp_read.stamp_path("substrate/corpus_selftest.py")
    if got.name != "substrate__corpus_selftest.py.ran":
        out.append(f"selftest: the stamp path is spelled {got.name!r}")
        return 1
    return 0


_ARMS = (
    a_recorded_pass_reads_back,
    an_empty_stamp_reads_as_absent,
    a_malformed_stamp_reads_as_absent,
    a_stamp_older_than_its_source_is_stale,
    a_missing_stamp_is_none,
    the_path_matches_the_generator,
)

_CASE_COUNT = 1 + 1 + 3 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"stamp-read selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"stamp-read selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
