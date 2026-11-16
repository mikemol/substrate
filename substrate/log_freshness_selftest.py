#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `log_freshness` - every verdict shape over a fake DAG, and the index over a tree.

THE MTIME READER IS A DICT, so each of the origin's recorded silent failures is a case that
cannot be silent: a module the DAG does not know withholds the verdict; a missing log; an
unreadable log; an unreadable DEPENDENCY makes the verdict unsafe (stale, with the count); a
log older than a transitive import is stale and names the culprit; a log at least as new as
everything is fresh. The transitive walk is cased through a chain A -> B -> C where only C
moved.

`log_index` IS DIFFERENCED BY PATH against the origin's `_log_index(root)` over a temporary
`_build` tree with two hash dirs and a duplicate module - first writer wins on both sides. The
origin's `log_is_fresh` reads the live tree through `_import_dag` and `ROOT`, so it is not
differenced; its verdict shapes are pinned instead.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
from typing import Protocol, cast

from substrate import log_freshness as lf
from substrate.agda_dag import Dag

_ORIGIN = Path(__file__).resolve().parent.parent / "scratch" / "split_census.py"
_ROOT = "/x"
# ⚑ `agda_dag.Dag`, THE parsed graph; `src_to_mod` is derived from `disk`, so the withheld-verdict
# case uses a source that is genuinely absent from `disk` rather than one omitted from a map.
_DAG = Dag(
    disk={
        "Substrate.A": "Substrate/A.agda",
        "Substrate.B": "Substrate/B.agda",
        "Substrate.C": "Substrate/C.agda",
        "Substrate.Lost": "Substrate/Lost.agda",
    },
    deps={
        "Substrate.A": frozenset({"Substrate.B"}),
        "Substrate.B": frozenset({"Substrate.C"}),
        "Substrate.Lost": frozenset({"Substrate.C"}),
    },
)
_LOG_A = "/x/agda/_build/h/agda/Substrate/A.agdai.log"
_LOG_LOST = "/x/agda/_build/h/agda/Substrate/Lost.agdai.log"
_INDEX = {"Substrate.A": _LOG_A, "Substrate.Lost": _LOG_LOST, "Substrate.B": "/x/B.log"}
_T_A, _T_B, _T_C = 10.0, 20.0, 30.0
_MTIMES = {
    "/x/Substrate/A.agda": _T_A,
    "/x/Substrate/B.agda": _T_B,
    "/x/Substrate/C.agda": _T_C,
    _LOG_A: 25.0,
    _LOG_LOST: 99.0,
}
_CHAIN = 3

Cases = list[tuple[str, bool]]


class _Origin(Protocol):
    def _log_index(self, root: str = "agda") -> dict[str, str]: ...


def _origin() -> _Origin | None:
    """Load `split_census.py` by PATH, or None when it is gone or will not import here."""
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_split_census_origin_lf", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImportError:
        return None
    return cast("_Origin", module)


def _mtime(path: str) -> float | None:
    """Return the fixture's mtime for a path, None for anything unlisted."""
    return _MTIMES.get(path)


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _verdict_cases(cases: Cases) -> None:
    """Pin every verdict shape."""
    fresh, log, why = lf.log_is_fresh("agda/Substrate/Nope.agda", _DAG, _INDEX, _mtime, _ROOT)
    _check(
        cases,
        "a source the DAG does not know withholds the verdict",
        ok=not fresh and log is None and "withheld" in str(why["why"]),
    )
    _check(
        cases,
        "the agda/ prefix is stripped, never added",
        ok=lf.log_is_fresh("agda/Substrate/A.agda", _DAG, _INDEX, _mtime, _ROOT)[1] == _LOG_A
        and lf.log_is_fresh("Substrate/A.agda", _DAG, _INDEX, _mtime, _ROOT)[1] == _LOG_A,
    )
    _check(
        cases,
        "no log for the module",
        ok=lf.freshness("Substrate.C", None, _DAG, _mtime, _ROOT)
        == (False, None, {"why": "no build log for this module"}),
    )
    _check(
        cases,
        "an unreadable log",
        ok=lf.freshness("Substrate.B", "/x/B.log", _DAG, _mtime, _ROOT)
        == (False, "/x/B.log", {"why": "log unreadable"}),
    )
    fresh, log, why = lf.log_is_fresh("Substrate/A.agda", _DAG, _INDEX, _mtime, _ROOT)
    _check(
        cases,
        "a log older than a TRANSITIVE import is stale and names the culprit",
        ok=not fresh
        and why["newest_dep"] == "Substrate.C"
        and why["newest_dep_mtime"] == _T_C
        and why["n_deps"] == _CHAIN,
    )
    fresh, _log, why = lf.freshness("Substrate.A", _LOG_LOST, _DAG, _mtime, _ROOT)
    _check(
        cases,
        "a log at least as new as every dependency is fresh, with the numbers",
        ok=fresh and why["log_mtime"] == _MTIMES[_LOG_LOST] and why["newest_dep_mtime"] == _T_C,
    )
    fresh, log, why = lf.log_is_fresh("Substrate/Lost.agda", _DAG, _INDEX, _mtime, _ROOT)
    _check(
        cases,
        "an unreadable dependency source makes the verdict UNSAFE: stale, counted",
        ok=not fresh and log == _LOG_LOST and str(why["why"]).startswith("1 of 2 dependency"),
    )


def _walk_cases(cases: Cases) -> None:
    """Pin newest_dependency directly: the closure is visited once, the count is total."""
    newest, culprit, missing, seen = lf.newest_dependency("Substrate.A", _DAG, _mtime, _ROOT)
    _check(
        cases,
        "newest_dependency walks the closure and reports the max and its owner",
        ok=(newest, culprit, missing, seen) == (_T_C, "Substrate.C", 0, _CHAIN),
    )


def _index_cases(cases: Cases, build: Path) -> None:
    """Pin log_index over a temp tree, then difference it against the origin."""
    idx = lf.log_index(build)
    _check(
        cases,
        "log_index names modules from the Substrate anchor and strips the suffix",
        ok=set(idx) == {"Substrate.A", "Substrate.Deep.B"},
    )
    _check(
        cases,
        "log_index: first writer wins across hash dirs",
        ok=idx["Substrate.A"].endswith("h1/agda/Substrate/A.agdai.log"),
    )
    _check(
        cases,
        "the production mtime reader returns None for a missing path",
        ok=lf.mtime_on_disk(str(build / "nope")) is None
        and lf.mtime_on_disk(idx["Substrate.A"]) is not None,
    )
    o = _origin()
    if o is None:
        _check(cases, "differential: origin unavailable, skipped", ok=True)
        return
    theirs = {m: str(Path(p)) for m, p in o._log_index(str(build.parent)).items()}  # noqa: SLF001 - the origin's spelling
    _check(
        cases,
        "differential: log_index names the same modules as the origin",
        ok=set(theirs) == set(idx),
    )
    _check(
        cases,
        "differential: an unduplicated module resolves to the same log",
        ok=theirs["Substrate.Deep.B"] == idx["Substrate.Deep.B"],
    )
    # ⚑ THE DUPLICATE IS NOT DIFFERENCED FOR EQUALITY, AND THAT IS A FINDING. The origin walks
    # with `os.walk`, whose order is the filesystem's, so which hash dir "wins" for a module
    # logged under two of them is NONDETERMINISTIC there; this module sorts, so it is h1 every
    # time. The origin's pick is asserted to be ONE of the candidates, never a specific one.
    _check(
        cases,
        "differential: the origin's duplicate pick is one of the candidates",
        ok=theirs["Substrate.A"].endswith("/agda/Substrate/A.agdai.log"),
    )


def _mirror(build: Path) -> None:
    """Lay two hash dirs with a duplicated module and a nested one."""
    for h in ("h1", "h2"):
        (build / h / "agda" / "Substrate").mkdir(parents=True)
        (build / h / "agda" / "Substrate" / "A.agdai.log").write_text("", encoding="utf-8")
    (build / "h1" / "agda" / "Substrate" / "Deep").mkdir()
    (build / "h1" / "agda" / "Substrate" / "Deep" / "B.agdai.log").write_text("", encoding="utf-8")
    (build / "h1" / "agda" / "Substrate" / "A.agdai").write_text("", encoding="utf-8")


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _verdict_cases(cases)
    _walk_cases(cases)
    with tempfile.TemporaryDirectory() as tmp:
        build = Path(tmp) / "agda" / "_build"
        _mirror(build)
        _index_cases(cases, build)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"log_freshness_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
