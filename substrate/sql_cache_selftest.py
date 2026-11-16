#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sql_cache` — the round-trip differential, and the verdict three ways.

⚑⚑⚑ THE COMMITTED CACHE IS THE ORIGIN'S OUTPUT, so `read` then `render` must reproduce it byte
for byte. That one arm verifies the renderer against what `query_defs.py --compile` actually
wrote, without SQLAlchemy in the process; a renderer that agreed with a fixture and not with the
committed file would silently make `--check` report STALE on every commit.

⚑⚑ THE VERDICT IS CASED IN ALL THREE STATES AND THE STALE LINE IN ALL THREE SHAPES: missing
file, fresh, and stale with a changed builder, an added one and a removed one — each named.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import corpus
from substrate import sql_cache as sc

_COMMITTED = corpus.ROOT / "jea" / "metalanguage" / "query_sql_postgres.py"

_A: sc.Entry = ("SELECT 1", {})
_B: sc.Entry = ("SELECT :x", {"x": 3})
_B2: sc.Entry = ("SELECT :x + 1", {"x": 3})
_REMEDY = "SUBSTRATE_STORE=postgres python3 jea/metalanguage/query_defs.py --compile"


def the_committed_cache_round_trips_byte_for_byte(out: list[str]) -> int:
    """Check `render(read(cache))` is the committed file — the origin's own output."""
    if not _COMMITTED.is_file():
        out.append(f"selftest: {_COMMITTED.name} is absent — the differential cannot run")
        return 1
    entries = sc.read(_COMMITTED)
    if entries is None:
        out.append("selftest: read() returned None for a present file")
        return 1
    mine = sc.render(entries).splitlines()
    theirs = _COMMITTED.read_text(encoding="utf-8").splitlines()
    for i, (a, b) in enumerate(zip(mine, theirs, strict=False)):
        if a != b:
            out.append(f"selftest: {_COMMITTED.name} diverges at line {i + 1}:")
            out.append(f"    committed: {b[:160]!r}")
            out.append(f"    rendered:  {a[:160]!r}")
            return 1
    if len(mine) != len(theirs):
        out.append(f"selftest: {_COMMITTED.name} has {len(theirs)} lines, rendered {len(mine)}")
        return 1
    return 0


def a_missing_cache_reads_none_and_reports_missing(out: list[str]) -> int:
    """Check the absent-file state is a verdict with the backend named in the remedy."""
    missing = Path(tempfile.mkdtemp(prefix="sql-cache-")) / "nope.py"
    if sc.read(missing) is not None:
        out.append("selftest: an absent cache did not read None")
        return 1
    lines, ok = sc.report("nope.py", "postgres", 0, None)
    if ok or lines != [f"query_defs --check: nope.py MISSING — run `{_REMEDY}`"]:
        out.append(f"selftest: the missing verdict read {lines!r} ok={ok}")
        return 1
    return 0


def a_fresh_cache_is_ok(out: list[str]) -> int:
    """Check identical maps are fresh and the line carries the count and backend."""
    found = sc.drift({"a": _A, "b": _B}, {"a": _A, "b": _B})
    lines, ok = sc.report("c.py", "postgres", 2, found)
    if not ok or found.stale or lines != ["query_defs --check: c.py fresh (2 builders, postgres)"]:
        out.append(f"selftest: the fresh verdict read {lines!r} ok={ok}")
        return 1
    return 0


def a_stale_cache_names_changed_added_and_removed(out: list[str]) -> int:
    """Check every drift direction is named, in the origin's order and spelling."""
    found = sc.drift({"a": _A, "b": _B2, "c": _A}, {"a": _A, "b": _B, "z": _A})
    if (found.changed, found.added, found.gone) != (("b",), ("c",), ("z",)):
        out.append(f"selftest: drift read {found!r}")
        return 1
    lines, ok = sc.report("c.py", "postgres", 3, found)
    want = [
        "query_defs --check: c.py STALE — 1 builder(s) differ, 1 added, 1 removed",
        "    b",
        "    +c",
        "    -z",
        f"  run `{_REMEDY}`",
    ]
    if ok or lines != want:
        out.append(f"selftest: the stale verdict read {lines!r}")
        return 1
    return 0


def a_malformed_cache_is_refused_not_misread(out: list[str]) -> int:
    """Check a file whose SQL is not the entry shape raises rather than yielding a partial map."""
    bad = Path(tempfile.mkdtemp(prefix="sql-cache-")) / "bad.py"
    bad.write_text('SQL = {"a": "not a pair"}\n', encoding="utf-8")
    try:
        sc.read(bad)
    except TypeError:
        return 0
    out.append("selftest: a malformed cache was read without refusal")
    return 1


_ARMS = (
    the_committed_cache_round_trips_byte_for_byte,
    a_missing_cache_reads_none_and_reports_missing,
    a_fresh_cache_is_ok,
    a_stale_cache_names_changed_added_and_removed,
    a_malformed_cache_is_refused_not_misread,
)

_CASE_COUNT = 1 + 2 + 1 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"sql-cache selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"sql-cache selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
