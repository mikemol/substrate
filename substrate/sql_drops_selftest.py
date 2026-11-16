#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sql_drops` — the three recorded corrections, and the differential.

⚑⚑⚑ THE DIFFERENTIAL RUNS THE ORIGIN'S `--drops` MODE AND COMPARES STDOUT LINE FOR LINE over
the live tree. The origin is `jea/metalanguage/query_defs.py`, a 2095-line module this cut is
draining; its output is read from its own process at suite time, never quoted.

⚑⚑ EACH RECORDED CORRECTION IS AN ARM IN BOTH DIRECTIONS: the commented-out drop is skipped
and the live one beside it is kept; `IF EXISTS` yields the relation and a placeholder yields
`?`; the instrument's own search-term functions are excluded in `query_defs.py` and NOT in a
file of another name.
"""

from __future__ import annotations

import subprocess
import sys

from substrate import corpus
from substrate import sql_drops as sd

_ORIGIN = corpus.ROOT / "jea" / "metalanguage" / "query_defs.py"

# A commented-out drop beside a live one, in one function.
_COMMENTED = (
    "def setup(con):\n"
    '    # con.execute("DROP TABLE old_tier")\n'
    '    con.execute("DROP TABLE new_tier")\n'
)

# Every spelling of the clause, and a placeholder that must not become a name.
#
# ⚑ THE MODULE-LEVEL LINE COMES FIRST ON PURPOSE. The enclosing-def rule is "nearest PRECEDING
# def", so a module-level statement written after `def c` reads as inside `c` — the origin's
# approximation, exact for a flat layout and wrong for a trailing constant. A first fixture put
# it last, expected ``, and the arm reddened on the approximation rather than on a defect. It
# is kept as the origin does it; this fixture pins the rule as stated, not as wished.
_CLAUSES = (
    'M = "drop table at_module_level"\n'
    "def a():\n"
    '    x = "drop table if exists events"\n'
    "def b():\n"
    '    y = "DROP TABLE IF EXISTS %s"\n'
    "def c():\n"
    '    z = "Drop Table With"\n'
)

# The instrument's own search terms, under the excluded names and under another.
_INSTRUMENT = (
    "def touching():\n"
    '    needle = "drop table"\n'
    "def real_drop():\n"
    '    con.execute("drop table real")\n'
)


def a_commented_out_drop_is_skipped_and_the_live_one_kept(out: list[str]) -> int:
    """Check the `#` line test in both directions."""
    found = sd.scan_text(_COMMENTED, "x.py")
    if [(d.relation, d.line, d.function) for d in found] != [("new_tier", 3, "setup")]:
        out.append(f"selftest: the commented drop read {found!r}")
        return 1
    return 0


def if_exists_and_placeholders_resolve_or_read_unnamed(out: list[str]) -> int:
    """Check the clause is skipped to the name, a placeholder is `?`, and module level is ``."""
    found = sd.scan_text(_CLAUSES, "x.py")
    want = [("at_module_level", ""), ("events", "a"), (sd.UNNAMED, "b"), (sd.UNNAMED, "c")]
    got = [(d.relation, d.function) for d in found]
    if got != want:
        out.append(f"selftest: clause handling read {got}, want {want}")
        return 1
    return 0


def the_instrument_does_not_count_itself_but_a_real_drop_in_it_counts(out: list[str]) -> int:
    """Check the by-function exclusion applies only in `query_defs.py`, and only to the three."""
    bad = 0
    in_instrument = sd.scan_text(_INSTRUMENT, "jea/metalanguage/query_defs.py")
    if [d.function for d in in_instrument] != ["real_drop"]:
        out.append(f"selftest: the instrument exclusion read {in_instrument!r}")
        bad += 1
    elsewhere = sd.scan_text(_INSTRUMENT, "jea/metalanguage/other.py")
    if [d.function for d in elsewhere] != ["touching", "real_drop"]:
        out.append(f"selftest: the exclusion leaked to another file: {elsewhere!r}")
        bad += 1
    return bad


def drops_are_distinct_and_sorted_by_the_declared_key(out: list[str]) -> int:
    """Check the tuple carries the order `(relation, path, line, function)` the docstring names."""
    found = sd.drops(corpus.ROOT)
    if list(found) != sorted(set(found)):
        out.append("selftest: drops() is not the sorted distinct set")
        return 1
    return 0


def _origin() -> list[str]:
    """Run the origin's `--drops` and return its stdout lines."""
    done = subprocess.run(
        [sys.executable, str(_ORIGIN), "--drops"],  # noqa: S603
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
        cwd=str(corpus.ROOT),
    )
    return done.stdout.splitlines()


def the_differential_matches_the_origin_line_for_line(out: list[str]) -> int:
    """Check this module renders exactly what the origin's `--drops` prints over the live tree."""
    if not _ORIGIN.is_file():
        out.append("selftest: the origin is absent — the differential cannot run")
        return 1
    mine = "\n".join(sd.render(sd.drops(corpus.ROOT))).splitlines()
    theirs = _origin()
    if mine != theirs:
        out.append("selftest: --drops differs from the origin:")
        out += [f"    - {line}" for line in theirs if line not in mine]
        out += [f"    + {line}" for line in mine if line not in theirs]
        return 1
    return 0


_ARMS = (
    a_commented_out_drop_is_skipped_and_the_live_one_kept,
    if_exists_and_placeholders_resolve_or_read_unnamed,
    the_instrument_does_not_count_itself_but_a_real_drop_in_it_counts,
    drops_are_distinct_and_sorted_by_the_declared_key,
    the_differential_matches_the_origin_line_for_line,
)

_CASE_COUNT = 1 + 1 + 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"sql-drops selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"sql-drops selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
