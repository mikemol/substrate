#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `failure_census` - the build-failed partition, driven over supplied callables.

EVERY BRANCH OF THE WALK IS A FIXTURE: a clean row is skipped, a stale row lands in `stale-log`
unclassified, a fresh row is classified and refined, the classifier's own remedy wins and the
table's remedy fills in on the REFINED kind, a row with no log is classified over '' and lands in
the clean-looking fallback, and modules come back sorted. The refiner is cased on all three
shapes (a verdict, no verdict, an unrelated kind), and the three readers over the census.

THE DIFFERENTIAL IS BY PATH AGAINST `figures._failures_by_kind` over the LIVE ledger, driven with
the same tools the origin reaches for (the split_census shim's `log_is_fresh` / `_classify` and
the two repairing tools' `classify`), each loaded by path and read through a Protocol. It is
skipped, not failed, when any of them will not import here - and it says how many build-failed
rows it covered, because a differential over zero rows agrees about nothing.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import failure_census as fc
from substrate import leaf_ledger, log_freshness

_ROOT = Path(__file__).resolve().parent.parent
_AGDA = _ROOT / "agda"

Cases = list[tuple[str, bool]]


class _Figures(Protocol):
    def _failures_by_kind(self) -> tuple[dict[str, list[str]], dict[str, str | None]]: ...


class _Census(Protocol):
    def log_is_fresh(self, src_rel: str) -> tuple[bool, str | None, dict[str, object]]: ...
    def _classify(self, path: str, txt: str) -> tuple[str, str, str | None]: ...


class _NotInScope(Protocol):
    def classify(self, log: str) -> list[tuple[str, int, str]]: ...


class _NoParse(Protocol):
    def classify(self, log: str) -> list[tuple[str, int, int, str, str]]: ...


def _load(name: str, path: Path) -> object | None:
    """Load a module by PATH, or None when it is gone or will not import here."""
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError, RuntimeError):
        return None
    return module


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


_LOGS = {"B.agda": "/l/B.log", "C.agda": "/l/C.log", "D.agda": "/l/D.log", "N.agda": "/l/N.log"}
_TEXT = {"/l/B.log": "b", "/l/C.log": "c", "/l/D.log": "d", "/l/N.log": "n"}
_KIND = {
    "b": ("other:X", "", "fix-b"),
    "c": ("other:X", "", None),
    "d": ("consumed-parent", "", None),
    "n": (fc.NOT_IN_SCOPE, "", None),
    "": ("clean", "", None),
}


def _classify(_rel: str, txt: str) -> tuple[str, str, str | None]:
    """Classify by the log text - the fixture classifier."""
    return _KIND[txt]


def _fixture() -> fc.Inputs:
    """Six rows exercising every branch."""
    rows = [
        ("A.agda", "clean", ""),
        ("D.agda", "build-failed", ""),
        ("B.agda", "build-failed", ""),
        ("S.agda", "build-failed", ""),
        ("C.agda", "build-failed", ""),
        ("N.agda", "build-failed", ""),
        ("Z.agda", "build-failed", ""),
    ]
    return fc.Inputs(
        rows=rows,
        log_of=_LOGS.get,
        read_text=lambda p: _TEXT.get(p, ""),
        is_fresh=lambda rel: rel != "S.agda",
        classify=_classify,
        refine=lambda k, rel: fc.refine(k, rel, lambda _r: "resolvable", lambda _r: None),
        remedies={"other:X": "table-x", "consumed-parent": "rewire"},
    )


def _walk_cases(cases: Cases) -> None:
    """Pin every branch of the walk."""
    by_kind, remedy = fc.census(_fixture())
    _check(cases, "a clean row is skipped", ok="A.agda" not in remedy)
    _check(
        cases,
        "a stale row lands in stale-log, unclassified",
        ok=by_kind.get(fc.STALE_LOG) == ["S.agda"] and "S.agda" not in remedy,
    )
    _check(
        cases, "modules under a kind are sorted", ok=by_kind.get("other:X") == ["B.agda", "C.agda"]
    )
    _check(cases, "the classifier's own remedy wins", ok=remedy["B.agda"] == "fix-b")
    _check(cases, "the table fills a missing remedy", ok=remedy["C.agda"] == "table-x")
    _check(
        cases,
        "the refined kind is what partitions",
        ok=by_kind.get(f"{fc.NOT_IN_SCOPE}:resolvable") == ["N.agda"],
    )
    _check(
        cases,
        "a row with no log is classified over '' - the fallback, never skipped",
        ok=by_kind.get("clean") == ["Z.agda"] and remedy["Z.agda"] is None,
    )
    _check(
        cases,
        "kinds is the discovered roster, sorted",
        ok=fc.kinds((by_kind, remedy)) == sorted(by_kind),
    )
    got = fc.modules((by_kind, remedy), "other:X")
    got.append("mutated")
    _check(cases, "modules returns a copy", ok=by_kind["other:X"] == ["B.agda", "C.agda"])
    _check(
        cases,
        "parts pairs each module with its own remedy",
        ok=fc.parts((by_kind, remedy), "other:X") == [("B.agda", "fix-b"), ("C.agda", "table-x")],
    )
    _check(cases, "parts of an absent kind is empty", ok=fc.parts((by_kind, remedy), "nope") == [])


def _refine_cases(cases: Cases) -> None:
    """Drive the refiner through its three shapes."""
    _check(
        cases,
        "NotInScope refines on the tool's verdict",
        ok=fc.refine(fc.NOT_IN_SCOPE, "r", lambda _r: "ambiguous", lambda _r: "fixity")
        == f"{fc.NOT_IN_SCOPE}:ambiguous",
    )
    _check(
        cases,
        "NoParse refines on ITS tool's verdict, not the other's",
        ok=fc.refine(fc.NO_PARSE, "r", lambda _r: "ambiguous", lambda _r: "fixity")
        == f"{fc.NO_PARSE}:fixity",
    )
    _check(
        cases,
        "no verdict: the UNREFINED kind, never a guess",
        ok=fc.refine(fc.NOT_IN_SCOPE, "r", lambda _r: None, lambda _r: None) == fc.NOT_IN_SCOPE,
    )
    _check(
        cases,
        "an unrelated kind passes through untouched",
        ok=fc.refine("other:Y", "r", lambda _r: "x", lambda _r: "y") == "other:Y",
    )
    _check(cases, "passthrough refines nothing", ok=fc.passthrough("k", "r") == "k")


def _differential_cases(cases: Cases) -> None:
    """Agree with figures._failures_by_kind over the live ledger, when everything imports."""
    live = _ROOT / leaf_ledger.LEDGER
    fig = _load("_figures_origin", _ROOT / "catalog" / "library" / "figures.py")
    sc = _load("_split_census", _ROOT / "scratch" / "split_census.py")
    nis = _load("_fix_notinscope", _ROOT / "scratch" / "fix_notinscope.py")
    nop = _load("_fix_noparse", _ROOT / "scratch" / "fix_noparse.py")
    if not live.exists() or None in (fig, sc, nis, nop):
        _check(cases, "differential: an origin is unavailable, skipped", ok=True)
        return
    f, c = cast("_Figures", fig), cast("_Census", sc)
    n, p = cast("_NotInScope", nis), cast("_NoParse", nop)
    _stamp, rows = leaf_ledger.read(live)
    index = log_freshness.log_index(_AGDA / "_build")

    def log_of(rel: str) -> str | None:
        return leaf_ledger.log_for(rel, index)

    def read_text(path: str) -> str:
        try:
            return Path(path).read_text(encoding="utf-8")
        except OSError:
            return ""

    def verdict_nis(rel: str) -> str | None:
        log = log_of(rel)
        hits = n.classify(log) if log and Path(log).exists() else []
        return hits[0][2] if hits else None

    def verdict_nop(rel: str) -> str | None:
        log = log_of(rel)
        hits = p.classify(log) if log and Path(log).exists() else []
        return hits[0][4] if hits else None

    mine = fc.census(
        fc.Inputs(
            rows=rows,
            log_of=log_of,
            read_text=read_text,
            is_fresh=lambda rel: bool(c.log_is_fresh(rel)[0]),
            classify=c._classify,  # noqa: SLF001 - the shim's spelling
            refine=lambda k, rel: fc.refine(k, rel, verdict_nis, verdict_nop),
        )
    )
    theirs = f._failures_by_kind()  # noqa: SLF001 - the origin's spelling
    n_rows = sum(1 for _r, v, _c in rows if v == fc.BUILD_FAILED)
    _check(
        cases,
        f"differential: agrees with figures over {n_rows} build-failed row(s)",
        ok=(dict(theirs[0]), dict(theirs[1])) == (mine[0], mine[1]),
    )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _walk_cases(cases)
    _refine_cases(cases)
    _differential_cases(cases)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"failure_census_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
