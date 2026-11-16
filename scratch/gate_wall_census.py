#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which files would REFUSE an edit right now — the per-file gate wall, mechanized.

⚑ WHY THIS EXISTS. Three single-file discoveries in one session (jea/metalanguage/schema.py:
588 findings, scratch/_pycodemod_census.py: 10 mypy codes, scratch/_pycodemod_fingerprint.py:
5 mypy codes) each cost an attempted Edit and a refusal to learn "this file is also walled".
That is judgement-in-the-turn: it evaporates, and the next reader re-derives it the same
expensive way. This censuses a file SET against the SAME checker the edit-time hook runs, so
"would this file refuse an edit" becomes a query rather than an experiment.

    gate_wall_census.py <path>...              report each path: WALLED / clean / UNKNOWN
    gate_wall_census.py <path>... --waypoints  ALSO print one $PF --add line per walled file

⚑ REUSES THE HOOK'S OWN CHECKER. `run_checks`/`census` in `scripts/pycheck_show.py` are what
`hook_pycheck` itself runs — a second, independently written checker here would be the
rival-authority defect this repo's own standing rule forbids. A result from this tool matches
what an actual Edit attempt would face, because it is the same subprocess call.

⚑ THE COULD-NOT-RUN MARKER IS MIRRORED, NOT IMPORTED. `pycheck_show._UNRUN` is private to
that module by its leading underscore; reaching across a module boundary for a private name
is the same class of coupling this repo's own `aliases()` census flags for Agda imports, one
layer down. The string is small and load-bearing enough to duplicate with a note rather than
widen `pycheck_show`'s public surface for one caller.

⚑ NO DEFAULT FULL-TREE SWEEP. Each path runs ruff AND mypy as two separate subprocesses
(`run_checks`'s own contract), so a corpus-wide default would silently start a run of
unbounded length. The caller states the population.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

from scripts.pycheck_show import census, run_checks

# Mirrors `pycheck_show._UNRUN` verbatim — see the module docstring's note on why this is a
# duplicated literal rather than a cross-module private import.
_UNRUN = "could not run"

Row = tuple[str, int, list[tuple[str, int]]]

# The unmeasured verdict: a checker could not run against this path at all.
UNKNOWN = -1


def _by_total_desc(row: Row) -> int:
    """Return the sort key: highest finding-count first."""
    return -row[1]


def wall_census(paths: list[str]) -> list[Row]:
    """[(path, total findings, [(code, count)...])], WALLED first, then clean, then UNKNOWN.

    ⚑ A PATH WHOSE CHECKER COULD NOT RUN IS `UNKNOWN`, NEVER FOLDED INTO CLEAN. `run_checks`
    already distinguishes "no findings" from "could not run"; reading the second as the first
    is exactly the empty-census-passes class this repo's own mutators test for.
    """
    out: list[Row] = []
    for p in paths:
        report = run_checks(Path(p))
        if _UNRUN in report.lower():
            out.append((p, UNKNOWN, []))
            continue
        rows = census(report)
        out.append((p, sum(n for _code, n in rows), rows))
    return sorted(out, key=_by_total_desc)


def render(rows: list[Row]) -> list[str]:
    """One line per path: its verdict and, for a walled file, its top rule codes."""
    out = []
    for path, total, codes in rows:
        if total == UNKNOWN:
            out.append(f"  UNKNOWN  {path}  (a checker could not run)")
        elif total == 0:
            out.append(f"  clean    {path}")
        else:
            top = ", ".join(f"{code}:{n}" for code, n in codes[:3])
            out.append(f"  WALLED   {path}  ({total} finding(s) — {top})")
    return out


def waypoint_lines(rows: list[Row]) -> list[str]:
    """Return one ready-to-paste `$PF --add` line per WALLED path.

    ⚑ THE TITLE NAMES THE CLEANROOM ANSWER, NOT A PATCH. Per the standing rule
    (feedback_cleanroom_not_air_freshener): rebuild whole, difference, swap — never patch,
    never re-suppress. Minting a waypoint that proposed anything else would be wrong by
    construction, so the title states the correct remedy rather than leaving it to be
    re-derived at mint time.
    """
    out = []
    for path, total, _codes in rows:
        if total > 0:
            title = (
                f"cleanroom {path}: {total} pre-existing finding(s) under the "
                "all-or-nothing per-file gate — rebuild whole, difference, swap "
                "(never patch, never re-suppress)"
            )
            out.append(f'$PF --add "{title}" --caused-by gate-wall-census --touches cleanroom')
    return out


def main(argv: list[str]) -> int:
    """Census the named paths and print their verdicts."""
    want_waypoints = "--waypoints" in argv
    paths = [a for a in argv[1:] if not a.startswith("--")]
    if not paths:
        sys.stderr.write(
            "usage: gate_wall_census.py <path>... [--waypoints]\n"
            "  no default population — name the paths to census\n"
        )
        return 2
    rows = wall_census(paths)
    sys.stdout.write("\n".join(render(rows)) + "\n")
    walled = sum(1 for _p, total, _c in rows if total > 0)
    sys.stdout.write(f"\n{walled} of {len(rows)} path(s) WALLED\n")
    if want_waypoints:
        lines = waypoint_lines(rows)
        if lines:
            sys.stdout.write("\n" + "\n".join(lines) + "\n")
    return 0


def _cases(tmp: Path) -> list[tuple[str, bool]]:
    """Return `(label, passed)` for `wall_census`'s three-way verdict.

    ⚑ THE FIXTURE NEEDS A SIBLING `__init__.py`. Without one, ruff's INP001 (implicit
    namespace package) fires on every file here regardless of its own content — measured: a
    bare one-line docstring module read WALLED on its own. That is a fact about the
    directory, not the file, and it would have made this case assert something false about
    `wall_census` rather than about the fixture.
    """
    (tmp / "__init__.py").write_text("", encoding="utf-8")
    clean = tmp / "clean.py"
    clean.write_text('"""A clean module."""\n', encoding="utf-8")
    dirty = tmp / "dirty.py"
    dirty.write_text("import os\nx=1\n", encoding="utf-8")

    rows = wall_census([str(clean), str(dirty)])
    by_path = {p: (total, codes) for p, total, codes in rows}

    clean_total, _ = by_path[str(clean)]
    dirty_total, dirty_codes = by_path[str(dirty)]

    return [
        (f"a clean module reads 0 findings: {clean_total}", clean_total == 0),
        (f"a dirty module reads WALLED: {dirty_total}", dirty_total > 0),
        (f"a dirty module's codes are non-empty: {dirty_codes}", len(dirty_codes) > 0),
    ]


def _render_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for `render`'s own formatting decision."""
    lines = render([("a.py", 0, []), ("b.py", 3, [("F401", 3)]), ("c.py", UNKNOWN, [])])
    return [
        ("a clean path reads 'clean'", "clean" in lines[0]),
        (
            "a walled path reads 'WALLED' with its top code",
            "WALLED" in lines[1] and "F401" in lines[1],
        ),
        ("an unrunnable path reads 'UNKNOWN'", "UNKNOWN" in lines[2]),
    ]


def _waypoint_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for `waypoint_lines`'s own filtering decision."""
    lines = waypoint_lines([("a.py", 0, []), ("b.py", 3, [("F401", 3)]), ("c.py", UNKNOWN, [])])
    return [
        ("only the walled path gets a waypoint line", len(lines) == 1),
        ("the line names cleanroom, never a patch", "cleanroom" in lines[0]),
        ("the line names the finding count", "3 pre-existing finding" in lines[0]),
    ]


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    tmp = Path(tempfile.mkdtemp())
    try:
        cases = _cases(tmp) + _render_cases() + _waypoint_cases()
    finally:
        shutil.rmtree(tmp)
    ok = sum(1 for _label, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"gate-wall-census selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    sys.exit(main(sys.argv))
