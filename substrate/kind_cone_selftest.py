#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `kind_cone` - the planning around the cone call, driven over a fixture DAG.

THE FIXTURE DAG IS FOUR MODULES IN A CHAIN WITH A FORK: A <- B <- C and A <- D, so seeding on
B reaches {C}, seeding on A reaches {B, C, D}, and B's cone measured against D's is exclusive
of nothing D reaches. `import_cone.leverage` over that DAG is the `lever` every case passes,
so the cone numbers are the package's, not this suite's. The refusals are cased first: an
undeclared schema, a kind with no keys, no seed resolving (the artefact-not-finding rule), and
a lever that cannot be asked. Then providers over a probe with every branch (splittable, a
blocker, a raise, a consumed parent, no file), the route grouping, route rows sorted by what
they free, and containment.

THE DIFFERENTIAL IS BY PATH against `figures.kind_cone` and `figures.kind_cone_exclusive` over
the LIVE ban census, with the seeds from `key_partition`-shaped keys and the lever from the
split_census shim's `leverage` (the same DAG figures reads through the driver) - skipped when
either will not import, and it prints its denominator.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import agda_dag, import_cone, key_spec, ratchet_census
from substrate import kind_cone as kc

_ROOT = Path(__file__).resolve().parent.parent
_LIVE_GATE = "check_ban_ratchet.py"
_LIVE_KIND = "using"

Cases = list[tuple[str, bool]]
Top = list[tuple[int, str]]


class _Figures(Protocol):
    def kind_cone(self, name: str, kind: str) -> tuple[tuple[int, int, Top] | None, str | None]: ...


class _Census(Protocol):
    def leverage(
        self, srcs: list[str], root: str = ..., against: list[list[str]] = ...
    ) -> tuple[int, int, Top]: ...


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


_DAG = agda_dag.Dag(
    disk={"A": "A.agda", "B": "B.agda", "C": "C.agda", "D": "D.agda"},
    deps={"A": frozenset(), "B": frozenset({"A"}), "C": frozenset({"B"}), "D": frozenset({"A"})},
)
_BAN = key_spec.KeySpec(gate="ban", baseline="", sep="::", path_field=0, arity=3, noun="")


def _lever(srcs: list[str], against: list[list[str]]) -> import_cone.Leverage | None:
    """Ask the package's cone over the fixture DAG."""
    return import_cone.leverage(_DAG, srcs, against)


def _no_lever(_srcs: list[str], _against: list[list[str]]) -> import_cone.Leverage | None:
    """Refuse - a DAG that cannot be asked."""
    return None


def _seed_cases(cases: Cases) -> None:
    """Pin the seed derivation and its refusals."""
    keys = ["agda/B.agda::P::using", "agda/D.agda::P::using", "agda/A.agda::Q::as", "bad"]
    _check(
        cases,
        "seeds strips the agda/ prefix and keeps one kind, skipping malformed",
        ok=kc.seeds(keys, _BAN, "using") == ({"B.agda", "D.agda"}, None),
    )
    _check(
        cases,
        "seeds refuses an undeclared schema",
        ok=kc.seeds(keys, None, "using") == (None, "no gate_keys.SCHEMA entry"),
    )
    _check(
        cases,
        "seeds refuses a kind with no keys",
        ok=kc.seeds(keys, _BAN, "renaming") == (None, "no keys of kind `renaming`"),
    )


def _cone_cases(cases: Cases) -> None:
    """Pin the cone, the exclusive cone and their refusals over the fixture DAG."""
    got, why = kc.cone({"B.agda"}, _lever)
    _check(
        cases,
        "cone on B reaches C alone",
        ok=why is None and got is not None and got[0] == 1 and got[1] == 1,
    )
    got, why = kc.cone({"A.agda"}, _lever)
    _check(cases, "cone on A reaches B, C, D", ok=got is not None and got[0] == 3)  # noqa: PLR2004 - three modules downstream
    _check(
        cases,
        "a lever that cannot be asked is a refusal",
        ok=kc.cone({"A.agda"}, _no_lever) == (None, "the import DAG could not be asked"),
    )
    ex, _why = kc.exclusive({"B.agda"}, [{"D.agda"}], _lever)
    _check(
        cases,
        "exclusive of D, B still frees C (D reaches nothing of B's cone)",
        ok=ex == (1, 1, ["C.agda"], ["C.agda"]),
    )
    ex, _why = kc.exclusive({"A.agda"}, [{"B.agda"}], _lever)
    _check(
        cases,
        "exclusive of B, A frees only what B does not also reach",
        ok=ex == (3, 2, ["B.agda", "C.agda", "D.agda"], ["B.agda", "D.agda"]),
    )
    ex, _why = kc.exclusive({"A.agda"}, [], _lever)
    _check(
        cases,
        "with nothing to measure against, exclusive IS the cone",
        ok=ex is not None and ex[1] == ex[0] and ex[3] is None,
    )


def _provider_cases(cases: Cases) -> None:
    """Every branch of the provider verdict, through a fake probe."""

    def blockers(path: str) -> list[tuple[str, object]]:
        if path == "raises":
            msg = "boom"
            raise ValueError(msg)
        return [("applied-open", ["x"])] if path == "blocked" else []

    probe = kc.Probe(
        file_of=lambda m: {"S": "ok", "T": "blocked", "U": "raises", "V": "gone", "W": "gone2"}[m],
        exists=lambda p: p in {"ok", "blocked", "raises"},
        has_leaf_dir=lambda m: m == "V",
        blockers=blockers,
    )
    conc = [
        ("S::using", 5, "k"),
        ("T::using", 4, "k"),
        ("U::using", 3, "k"),
        ("V::using", 2, "k"),
        ("W::using", 1, "k"),
    ]
    got = kc.providers(conc, probe)
    _check(
        cases,
        "providers: splittable / blocked / raised / consumed-parent / no-file",
        ok=got
        == [
            ("S", 5, ""),
            ("T", 4, "applied-open"),
            ("U", 3, "ValueError: boom"),
            ("V", 2, kc.CONSUMED_PARENT),
            ("W", 1, kc.NO_FILE),
        ],
    )
    routes = kc.by_route(got)
    _check(
        cases,
        "by_route sends an empty verdict to decomposition and groups the rest",
        ok=routes[kc.DECOMPOSE] == ["S"]
        and routes["applied-open"] == ["T"]
        and routes[kc.CONSUMED_PARENT] == ["V"],
    )


def _route_cases(cases: Cases) -> None:
    """Route rows over the fixture DAG, sorted by what each frees."""
    routes = {"decompose": ["A"], "rewire": ["B"]}
    seeds_of = {"decompose": ["A.agda"], "rewire": ["B.agda"]}
    rows = kc.route_rows(routes, seeds_of, _lever)
    _check(
        cases,
        "route rows are (route, providers, seeds, cone, exclusive), largest freed first",
        ok=rows == [("decompose", 1, 1, 3, 2), ("rewire", 1, 1, 1, 0)],
    )
    rows = kc.route_rows(routes, seeds_of, _no_lever)
    _check(
        cases,
        "a lever that cannot be asked leaves cone and exclusive None, seeds counted",
        ok=rows == [("decompose", 1, 1, None, None), ("rewire", 1, 1, None, None)],
    )
    _check(
        cases,
        "containment counts consumers inside the reach",
        ok=kc.containment(["B.agda", "X.agda", "C.agda"], ["B.agda", "C.agda", "D.agda"]) == (2, 3),
    )


def _differential_cases(cases: Cases) -> None:
    """Agree with figures.kind_cone over the live ban census, when both sides can read it."""
    fig = _load("_figures_origin", _ROOT / "catalog" / "library" / "figures.py")
    sc = _load("_split_census", _ROOT / "scratch" / "split_census.py")
    got, _why = ratchet_census.census(_LIVE_GATE)
    if fig is None or sc is None or got is None:
        _check(
            cases, "differential: figures, the shim or the live gate unavailable, skipped", ok=True
        )
        return
    f, c = cast("_Figures", fig), cast("_Census", sc)
    seed_set, why = kc.seeds(got.added, key_spec.spec_for(_LIVE_GATE), _LIVE_KIND)
    if seed_set is None:
        _check(cases, f"differential: {why}, skipped", ok=True)
        return

    def lever(srcs: list[str], against: list[list[str]]) -> import_cone.Leverage | None:
        n_cone, n_seeds, top = c.leverage(srcs, against=against)
        return import_cone.Leverage(n_cone=n_cone, n_seeds=n_seeds, top=top, members=[])

    sys.stdout.write(f"  differential over {_LIVE_GATE}/{_LIVE_KIND}: {len(seed_set)} seed(s)\n")
    mine = kc.cone(seed_set, lever)
    _check(
        cases,
        "differential: kind_cone agrees with figures over the live seeds",
        ok=mine == f.kind_cone(_LIVE_GATE, _LIVE_KIND),
    )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _seed_cases(cases)
    _cone_cases(cases)
    _provider_cases(cases)
    _route_cases(cases)
    _differential_cases(cases)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"kind_cone_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
