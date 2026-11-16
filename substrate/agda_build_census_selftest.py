#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `agda_build_census` - every verdict, the retired freshness copy, the three causes.

THE TREE IS A DICT-BACKED `Tree`, so each row's verdict is decided by data the case states:
mtimes, log texts, which cores exist. The retired-copy correction is pinned as a DIRECTION - a
module whose dependency source cannot be stat'd is `stale` here where the origin's inline rule
read it as fresh - and `stale_why` is driven over rows whose verdicts include a failed import,
a fresh log with no core, and a log that merely predates a named source.

NO DIFFERENTIAL AGAINST THE ORIGIN: `census_from_build` reads `ROOT` and `_import_dag` off the
live tree and globs the real `_build`, so a by-path call is a census of this machine, not a
comparison. The origin's row and cause shapes are pinned instead, verbatim.
"""

from __future__ import annotations

import sys

from substrate import agda_build_census as bc
from substrate.agda_dag import Dag

_ROOT = "/x/agda"
_B = "/x/agda/_build/h/agda/Substrate"
_DAG = Dag(
    disk={
        "Substrate.A": "Substrate/A.agda",
        "Substrate.B": "Substrate/B.agda",
        "Substrate.C": "Substrate/C.agda",
        "Substrate.D": "Substrate/D.agda",
        "Substrate.E": "Substrate/E.agda",
        "Substrate.Ghost": "Substrate/Ghost.agda",
        "Substrate.OnGhost": "Substrate/OnGhost.agda",
        "Substrate.NoCore": "Substrate/NoCore.agda",
        "Substrate.F": "Substrate/F.agda",
    },
    deps={
        "Substrate.A": frozenset({"Substrate.B"}),
        "Substrate.C": frozenset({"Substrate.B"}),
        "Substrate.D": frozenset({"Substrate.E"}),
        "Substrate.OnGhost": frozenset({"Substrate.Ghost"}),
    },
)
_MODS = (
    "Substrate.A",
    "Substrate.B",
    "Substrate.C",
    "Substrate.D",
    "Substrate.E",
    "Substrate.OnGhost",
    "Substrate.NoCore",
    "Substrate.F",
)
_INDEX = {m: f"{_B}/{m.split('.')[-1]}.agdai.log" for m in _MODS}
_T_OLD, _T_NEW, _T_LOG = 10.0, 20.0, 15.0
_MTIMES = {
    f"{_ROOT}/Substrate/A.agda": _T_OLD,
    f"{_ROOT}/Substrate/B.agda": _T_OLD,
    f"{_ROOT}/Substrate/C.agda": _T_NEW,
    f"{_ROOT}/Substrate/D.agda": _T_OLD,
    f"{_ROOT}/Substrate/E.agda": _T_NEW,
    f"{_ROOT}/Substrate/OnGhost.agda": _T_OLD,
    f"{_ROOT}/Substrate/NoCore.agda": _T_OLD,
    f"{_ROOT}/Substrate/F.agda": _T_OLD,
    **{_INDEX[m]: _T_LOG for m in _MODS},
}
_LOGS = {_INDEX[m]: "" for m in _MODS}
_LOGS[_INDEX["Substrate.E"]] = "/x/agda/Substrate/E.agda:4,1-9: error: [UnequalTerms]\n"
_LOGS[_INDEX["Substrate.F"]] = "/x/agda/Substrate/F.agda:4,1-9: error: [UnequalTerms]\n"
_CORES = {
    bc.core_of(_INDEX[m])
    for m in ("Substrate.A", "Substrate.B", "Substrate.D", "Substrate.OnGhost")
}

Cases = list[tuple[str, bool]]


def _tree() -> bc.Tree:
    """Build the fixture tree."""
    return bc.Tree(
        _DAG,
        _INDEX,
        _ROOT,
        mtime_of=_MTIMES.get,
        read_text=_LOGS.get,
        core_exists=_CORES.__contains__,
    )


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _census_cases(cases: Cases, rows: dict[str, bc.Row]) -> None:
    """Pin every verdict a row can carry."""
    _check(
        cases,
        "a fresh log with a core is clean",
        ok=rows["Substrate/A.agda"] == ("Substrate/A.agda", "clean", ""),
    )
    _check(
        cases,
        "a log older than a dependency source is stale",
        ok=rows["Substrate/C.agda"][1] == "stale",
    )
    _check(
        cases, "a log older than its OWN source is stale", ok=rows["Substrate/E.agda"][1] == "stale"
    )
    # ⚑ THE ORIGIN'S READING, KEPT: no core + an EMPTY log blames as clean (blame reads no
    # error), which is the no-core disagreement `stale_why` exists to name, not a row verdict.
    _check(
        cases,
        "a fresh log with no core goes to blame: empty text reads clean",
        ok=rows["Substrate/NoCore.agda"] == ("Substrate/NoCore.agda", "clean", None),
    )
    _check(
        cases,
        "a fresh log with no core and an own-citing error is own, citing the leaf",
        ok=rows["Substrate/F.agda"][1] == "own"
        and str(rows["Substrate/F.agda"][2]).endswith("Substrate/F.agda"),
    )
    _check(
        cases,
        "the retired copy: an unreadable dependency source reads STALE, never clean",
        ok=rows["Substrate/OnGhost.agda"][1] == "stale",
    )
    _check(cases, "a module with no log has no row", ok="Substrate/Ghost.agda" not in rows)
    _check(cases, "rows are sorted by module", ok=list(rows) == sorted(rows))


def _shape_cases(cases: Cases) -> None:
    """Pin the path helpers."""
    _check(
        cases,
        "core_of strips exactly the .log suffix",
        ok=bc.core_of("/b/X.agdai.log") == "/b/X.agdai",
    )
    _check(
        cases,
        "rel_of and mod_of are inverse",
        ok=bc.mod_of(bc.rel_of("Substrate.Foo.Bar")) == "Substrate.Foo.Bar"
        and bc.rel_of("Substrate.Foo.Bar") == "Substrate/Foo/Bar.agda",
    )


def _why_cases(cases: Cases, tree: bc.Tree) -> None:
    """Pin the three stale causes over rows that exercise each."""
    rows: list[bc.Row] = [
        ("Substrate/B.agda", "own", "/x/agda/Substrate/B.agda"),
        ("Substrate/A.agda", "stale", ""),
        ("Substrate/NoCore.agda", "stale", ""),
        ("Substrate/C.agda", "stale", ""),
        ("Substrate/D.agda", "stale", ""),
        ("Substrate/E.agda", "clean", ""),
    ]
    why = {m: (c, w) for m, c, w in bc.stale_why(rows, tree)}
    _check(
        cases,
        "a stale module over a FAILED import is blocked-upstream, naming the import",
        ok=why["Substrate.A"] == ("blocked-upstream", "Substrate.B"),
    )
    _check(
        cases,
        "a stale module whose core is absent is no-core",
        ok=why["Substrate.NoCore"][0] == "no-core",
    )
    _check(
        cases,
        "a stale module over clean imports is unbuilt, naming the newest source",
        ok=why["Substrate.D"] == ("unbuilt", "Substrate.E"),
    )
    _check(
        cases,
        "only stale rows are explained",
        ok=set(why) <= {"Substrate.A", "Substrate.C", "Substrate.NoCore", "Substrate.D"},
    )
    _check(
        cases,
        "the failed set is the origin's three verdicts",
        ok={"build-failed", "own", "dependency"} == bc.FAILED,
    )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    tree = _tree()
    rows = {rel: (rel, v, c) for rel, v, c in bc.census(tree)}
    _census_cases(cases, rows)
    _shape_cases(cases)
    _why_cases(cases, tree)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"agda_build_census_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
