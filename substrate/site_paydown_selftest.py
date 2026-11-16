#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `site_paydown` - the rostered reach-the-store predicate.

THE PREDICATE IS DRIVEN OVER LITERAL SOURCES: a site naming a store token is paid, one naming
none is unpaid, one whose source cannot be read is SKIPPED rather than reported, and a
`yield`-shaped rewrite that still re-derives the relation stays unpaid (the earlier cut's
false pass). The two rosters are asserted non-empty with disjoint token sets, because a
roster that silently emptied would read as a paid item.

THE DIFFERENTIAL IS BY PATH against `figures.dag_rederivations` and `figures.cst_blob_sites`,
driven with `pycodemod.source_of` loaded by path - the same reader the origin reaches through
a sys.path insert - and skipped, not failed, when either will not import.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import site_paydown as sp

_ROOT = Path(__file__).resolve().parent.parent

Cases = list[tuple[str, bool]]


class _Figures(Protocol):
    def dag_rederivations(self) -> list[tuple[str, str]]: ...
    def cst_blob_sites(self) -> list[tuple[str, str]]: ...


class _Codemod(Protocol):
    def source_of(self, name: str, paths: list[str]) -> list[tuple[str, int, int, str]]: ...


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


_SOURCES = {
    ("a.py", "paid"): "def paid():\n    return con.execute('select * from module_edges')\n",
    ("a.py", "unpaid"): "def unpaid():\n    return {m: deps for m in walk()}\n",
    ("a.py", "lazy"): "def lazy():\n    for m in walk():\n        yield m\n",
    ("a.py", "gone"): None,
}


def _source_of(rel: str, fn: str) -> str | None:
    """Look a fixture source up."""
    return _SOURCES.get((rel, fn))


def _predicate_cases(cases: Cases) -> None:
    """Pin the four site shapes."""
    sites = [
        ("a.py", "paid", "p"),
        ("a.py", "unpaid", "u"),
        ("a.py", "lazy", "l"),
        ("a.py", "gone", "g"),
    ]
    got = sp.unpaid(sites, ("module_edges", "catalog_db"), _source_of)
    _check(
        cases,
        "a site naming the store is paid; unpaid and lazy are not; unreadable is skipped",
        ok=got == [("a.py", "unpaid", "u"), ("a.py", "lazy", "l")],
    )
    _check(cases, "an empty roster reports nothing", ok=sp.unpaid([], ("x",), _source_of) == [])


def _roster_cases(cases: Cases) -> None:
    """Assert the rosters are populated and their tokens disjoint."""
    _check(cases, "both rosters name sites", ok=bool(sp.DAG_SITES) and bool(sp.CST_SITES))
    _check(
        cases,
        "the two token sets are disjoint - one store each",
        ok=not (set(sp.DAG_PAID) & set(sp.CST_PAID)),
    )


def _differential_cases(cases: Cases) -> None:
    """Agree with figures over the live tree, when both readers import."""
    fig = _load("_figures_origin", _ROOT / "catalog" / "library" / "figures.py")
    pcm = _load("_pycodemod", _ROOT / "scratch" / "pycodemod.py")
    if fig is None or pcm is None:
        _check(cases, "differential: figures or pycodemod unavailable, skipped", ok=True)
        return
    f, p = cast("_Figures", fig), cast("_Codemod", pcm)

    # ⚑ `source_of` RETURNS ROWS, and the origin tested a substring against that LIST - a
    # membership test that never matches, so every existing site read UNPAID whatever its
    # source said (gate-G446). The rows' text is joined here; the origin's verdict is
    # therefore compared as the SUPERSET it is: everything this reports, the origin reports,
    # and the origin may report more - a site it could never see as paid.
    def source_of(rel: str, fn: str) -> str | None:
        try:
            rows = p.source_of(fn, [str(_ROOT / rel)])
        except (OSError, ValueError, RuntimeError):
            return None
        return "\n".join(row[3] for row in rows) or None

    dag = [(rel, fn) for rel, fn, _w in sp.unpaid(sp.DAG_SITES, sp.DAG_PAID, source_of)]
    o_dag = f.dag_rederivations()
    _check(
        cases,
        "differential: the origin's dag_rederivations contains the corrected read",
        ok=set(dag) <= set(o_dag),
    )
    cst = [(rel, f"{fn} ({w})") for rel, fn, w in sp.unpaid(sp.CST_SITES, sp.CST_PAID, source_of)]
    o_cst = f.cst_blob_sites()
    sys.stdout.write(
        f"  differential: origin unpaid dag {len(o_dag)} / cst {len(o_cst)};"
        f" corrected read dag {len(dag)} / cst {len(cst)}\n"
    )
    _check(
        cases,
        "differential: the origin's cst_blob_sites is a superset of the corrected read",
        ok=set(cst) <= set(o_cst),
    )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _predicate_cases(cases)
    _roster_cases(cases)
    _differential_cases(cases)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"site_paydown_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
