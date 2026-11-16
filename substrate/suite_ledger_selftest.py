#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_ledger` — the round trip, and the four states it separates.

⚑⚑ THE STATES ARE NOT ONE SCALAR AND THEY DEMAND DIFFERENT ACTIONS. A suite can be CURRENT-and-
ok, CURRENT-and-broken, STALE (edited since the run), or GONE (recorded, no longer a suite).
Collapsing any pair sends a reader to the wrong place: `stale` folded into `clean` is a census
reporting a tree it did not measure, and `broken` folded into `stale` blames today's source for
yesterday's run.

⚑ THE KIND-IS-A-COLUMN ARM IS THE ONE A WHOLE SESSION BOUGHT. The verdict was `BROKEN`/`ok` —
one bit — while the run loop already distinguished four states. A reader cannot recover what the
writer discarded, and a suite killed by its memory lease reads identically to one whose
assertions failed.

⚑ AND THE NOT-`ok` ARM IS TOTAL BY CONSTRUCTION. Keying on a literal spelling is how a reader
reports every failing suite as passing the moment the writer adds a kind it does not know.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import suite_ledger


def _suites(root: Path, bodies: dict[str, str]) -> list[tuple[str, str]]:
    """Write fixture suites and return the `(label, path)` roster."""
    out: list[tuple[str, str]] = []
    for name, body in bodies.items():
        path = root / name
        path.write_text(body, encoding="utf-8")
        out.append((name, str(path)))
    return sorted(out)


def _ledger(suites: list[tuple[str, str]], kinds: dict[str, str], broken: set[str]) -> str:
    """Render a ledger for one run over these suites."""
    return suite_ledger.render(suites, (1, 1), kinds, broken)


def a_clean_run_reads_current(out: list[str]) -> int:
    """Check an unedited tree reads CURRENT with nothing broken."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        suites = _suites(Path(tmp), {"a.py": "x = 1\n"})
        got = suite_ledger.read(_ledger(suites, {"a.py": "ok"}, set()), suites)
        if not got.current or got.broken:
            out.append(f"selftest: a clean run read stale={got.stale!r} broken={got.broken!r}")
            bad += 1
    return bad


def an_edited_suite_reads_stale(out: list[str]) -> int:
    """Check a suite edited since the run is named STALE, not silently carried."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        suites = _suites(root, {"a.py": "x = 1\n"})
        body = _ledger(suites, {"a.py": "ok"}, set())
        (root / "a.py").write_text("x = 2\n", encoding="utf-8")
        got = suite_ledger.read(body, suites)
        if got.stale != ("a.py",):
            out.append(f"selftest: an edited suite read stale={got.stale!r}")
            bad += 1
    return bad


def a_new_suite_reads_stale(out: list[str]) -> int:
    """Check a suite the record never saw reads STALE — never measured is not clean."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        one = _suites(root, {"a.py": "x = 1\n"})
        body = _ledger(one, {"a.py": "ok"}, set())
        both = _suites(root, {"a.py": "x = 1\n", "b.py": "y = 1\n"})
        got = suite_ledger.read(body, both)
        if got.stale != ("b.py",):
            out.append(f"selftest: a new suite read stale={got.stale!r}")
            bad += 1
    return bad


def a_removed_suite_reads_gone(out: list[str]) -> int:
    """Check a recorded suite that is no longer one reads GONE — a different state from stale."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        both = _suites(root, {"a.py": "x = 1\n", "b.py": "y = 1\n"})
        body = _ledger(both, {"a.py": "ok", "b.py": "ok"}, set())
        got = suite_ledger.read(body, [row for row in both if row[0] == "a.py"])
        if got.gone != ("b.py",):
            out.append(f"selftest: a removed suite read gone={got.gone!r}")
            bad += 1
    return bad


def the_kind_survives_the_round_trip(out: list[str]) -> int:
    """Check the verdict column carries the KIND, not one bit.

    ⚑ `unfit` and `cases` need two different next actions; one word requested one.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        suites = _suites(Path(tmp), {"a.py": "x = 1\n"})
        body = _ledger(suites, {"a.py": "unfit"}, {"a.py"})
        got = suite_ledger.read(body, suites)
        if got.broken != (("a.py", "unfit"),):
            out.append(f"selftest: the kind round-tripped to {got.broken!r}")
            bad += 1
    return bad


def an_unknown_kind_is_still_a_failure(out: list[str]) -> int:
    """Check a kind this reader has never seen reads as a failure, not as green.

    ⚑ KEYING ON "NOT ok" IS TOTAL: a kind added tomorrow refuses here without an edit.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        suites = _suites(Path(tmp), {"a.py": "x = 1\n"})
        body = _ledger(suites, {"a.py": "a-kind-invented-tomorrow"}, {"a.py"})
        got = suite_ledger.read(body, suites)
        if not got.broken:
            out.append("selftest: an unrecognised kind read as green")
            bad += 1
    return bad


def the_legacy_spelling_is_still_a_failure(out: list[str]) -> int:
    """Check a pre-kind `BROKEN` row still reads as a failure — it measured a real run."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        suites = _suites(Path(tmp), {"a.py": "x = 1\n"})
        body = _ledger(suites, {"a.py": suite_ledger.LEGACY_BROKEN}, {"a.py"})
        got = suite_ledger.read(body, suites)
        if got.broken != (("a.py", suite_ledger.LEGACY_BROKEN),):
            out.append(f"selftest: a legacy BROKEN row read {got.broken!r}")
            bad += 1
    return bad


def a_stale_row_is_not_reported_broken(out: list[str]) -> int:
    """Check an edited suite is STALE only — today's source is not blamed for the old run."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        suites = _suites(root, {"a.py": "x = 1\n"})
        body = _ledger(suites, {"a.py": "cases"}, {"a.py"})
        (root / "a.py").write_text("x = 2\n", encoding="utf-8")
        got = suite_ledger.read(body, suites)
        if got.broken or got.stale != ("a.py",):
            out.append(
                f"selftest: an edited failing suite read broken={got.broken!r} stale={got.stale!r}"
            )
            bad += 1
    return bad


def an_unreadable_source_never_reads_unchanged(out: list[str]) -> int:
    """Check a source that cannot be read stamps UNREADABLE rather than matching a digest."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        got = suite_ledger.digest_of(Path(tmp) / "absent.py")
        if got != suite_ledger.UNREADABLE:
            out.append(f"selftest: an absent source stamped {got!r}")
            bad += 1
    return bad


def the_header_is_preserved(out: list[str]) -> int:
    """Check the run's header line survives the read, so a reader sees what was measured."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        suites = _suites(Path(tmp), {"a.py": "x = 1\n"})
        got = suite_ledger.read(_ledger(suites, {"a.py": "ok"}, set()), suites)
        if not got.header.startswith("#"):
            out.append(f"selftest: the header read {got.header!r}")
            bad += 1
    return bad


def an_empty_ledger_reads_everything_stale(out: list[str]) -> int:
    """Check no record at all reads as never-measured, never as clean."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        suites = _suites(Path(tmp), {"a.py": "x = 1\n"})
        got = suite_ledger.read("", suites)
        if got.current:
            out.append("selftest: an empty ledger read as CURRENT")
            bad += 1
    return bad


_ARMS = (
    a_clean_run_reads_current,
    an_edited_suite_reads_stale,
    a_new_suite_reads_stale,
    a_removed_suite_reads_gone,
    the_kind_survives_the_round_trip,
    an_unknown_kind_is_still_a_failure,
    the_legacy_spelling_is_still_a_failure,
    a_stale_row_is_not_reported_broken,
    an_unreadable_source_never_reads_unchanged,
    the_header_is_preserved,
    an_empty_ledger_reads_everything_stale,
)

_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-ledger selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-ledger selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO DISCOVERY SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
