#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sql_writers` — the verb-before-table rule, and the differential.

⚑⚑⚑ THE DIFFERENTIAL RUNS THE ORIGIN'S `--touching <table>` AND COMPARES ITS `writers` BLOCK
line for line, for a relation that HAS writers and one that has none. The block is sliced out
of the origin's report by its header line and its indentation — the origin owns the other three
blocks (readers, builder writes, by column), which this module deliberately does not reproduce.

⚑⚑ THE RULE IS CASED IN BOTH DIRECTIONS: a verb AFTER the table name is not a write; a literal
naming the table with no verb is not a write; the first verb in the roster's order wins when two
precede the name; the table is matched as a WORD, so `tt` does not match `t`.
"""

from __future__ import annotations

import subprocess
import sys

from substrate import corpus
from substrate import sql_writers as sw

_ORIGIN = corpus.ROOT / "jea" / "metalanguage" / "query_defs.py"
_HEADER = "  writers ("
_ROW = "      "

# A relation the live tree writes, and one it declares but never writes through a literal.
_WRITTEN = "obs_node"
_UNWRITTEN = "no_such_relation_anywhere"

_FIXTURE = (
    'a = "insert into t (x) values (1)"\n'
    'b = "select * from t where x = 1"\n'
    'c = "t is updated by the update job"\n'
    'd = "delete from t where x in (select x from tt)"\n'
    'e = "update tt set y = 2"\n'
    'f = "insert into t select * from t where update"\n'
)


def the_verb_must_precede_the_table_name(out: list[str]) -> int:
    """Check the four directions of the rule on one fixture."""
    found = sw.scan_text(_FIXTURE, "x.py", "t")
    got = [(w.line, w.verb) for w in found]
    want = [(1, "insert into"), (4, "delete from"), (6, "insert into")]
    if got != want:
        out.append(f"selftest: the verb rule read {got}, want {want}")
        return 1
    return 0


def _origin_writers(table: str) -> list[str]:
    """Run the origin's `--touching` and return only its `writers` block."""
    done = subprocess.run(
        [sys.executable, str(_ORIGIN), "--touching", table],  # noqa: S603
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
        cwd=str(corpus.ROOT),
    )
    lines = done.stdout.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith(_HEADER)), None)
    if start is None:
        return []
    block = [lines[start]]
    for line in lines[start + 1 :]:
        if not line.startswith(_ROW):
            break
        block.append(line)
    return block


def the_differential_matches_the_origin_writers_block(out: list[str]) -> int:
    """Check this module renders the origin's `writers` block, written and unwritten alike."""
    if not _ORIGIN.is_file():
        out.append("selftest: the origin is absent — the differential cannot run")
        return 1
    bad = 0
    for table in (_WRITTEN, _UNWRITTEN):
        mine = sw.render(sw.writers(table, corpus.ROOT))
        theirs = _origin_writers(table)
        if mine != theirs:
            out.append(f"selftest: writers({table}) differs from the origin:")
            out += [f"    - {line}" for line in theirs if line not in mine]
            out += [f"    + {line}" for line in mine if line not in theirs]
            bad += 1
    return bad


_ARMS = (the_verb_must_precede_the_table_name, the_differential_matches_the_origin_writers_block)

_CASE_COUNT = 4 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"sql-writers selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"sql-writers selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
