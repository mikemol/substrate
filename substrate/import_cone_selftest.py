#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `import_cone` - the blocked cone, participation vs exclusivity, and a differential.

THE FIXTURE DAG HAS A SHARED SUBTREE on purpose: two seeds (`A`, `B`) both block `Shared`,
so the cones overlap and `exclusive` is strictly smaller than the cone - the 60-75% overlap
the origin measured, in miniature. The cone excludes the seeds, exclusivity is None without
`against`, and the ranking is returned whole.

THE DIFFERENTIAL PRE-FILLS THE ORIGIN'S MEMO. `split_census._import_dag()` parses the live
tree once and caches the tuple in a module-level `_DAG` dict; seeding that dict with the
fixture's `(disk, deps, rdeps, src_to_mod)` makes the origin's `_blast_radius` and `leverage`
answer over the SAME graph without a tree walk. Skipped, not failed, if the origin will not
import here.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import import_cone as ic
from substrate.agda_dag import Dag

_ORIGIN = Path(__file__).resolve().parent.parent / "scratch" / "split_census.py"
_MODS = (
    "Substrate.A",
    "Substrate.B",
    "Substrate.OnlyA",
    "Substrate.Shared",
    "Substrate.Top",
    "Substrate.Lone",
)
_DAG = Dag(
    disk={m: m.replace(".", "/") + ".agda" for m in _MODS},
    # deps: importer -> imports. OnlyA imports A; Shared imports A and B; Top imports Shared.
    deps={
        "Substrate.OnlyA": frozenset({"Substrate.A"}),
        "Substrate.Shared": frozenset({"Substrate.A", "Substrate.B"}),
        "Substrate.Top": frozenset({"Substrate.Shared"}),
    },
)
_A, _B = "Substrate/A.agda", "Substrate/B.agda"
_A_CONE = {"Substrate/OnlyA.agda", "Substrate/Shared.agda", "Substrate/Top.agda"}
_B_CONE = {"Substrate/Shared.agda", "Substrate/Top.agda"}

Cases = list[tuple[str, bool]]


class _OriginLeverage(Protocol):
    def __getitem__(self, i: int) -> object: ...
    @property
    def exclusive(self) -> int | None: ...
    @property
    def members(self) -> list[str] | None: ...


class _Origin(Protocol):
    _DAG: dict[str, object]

    def _blast_radius(self, failed_srcs: list[str], root: str = "agda") -> set[str]: ...
    def leverage(
        self, srcs: list[str], root: str = "agda", against: tuple[list[str], ...] = ()
    ) -> _OriginLeverage: ...


def _origin() -> _Origin | None:
    """Load `split_census.py` by PATH with its DAG memo pre-filled, or None."""
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_split_census_origin_ic", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImportError:
        return None
    o = cast("_Origin", module)
    o._DAG.update(
        disk=dict(_DAG.disk),  # noqa: SLF001 - the memo, filled as `_import_dag` fills it
        deps={m: set(v) for m, v in _DAG.deps.items()},
        rdeps={m: set(v) for m, v in _DAG.rdeps.items()},
        src_to_mod=dict(_DAG.src_to_mod),
    )
    return o


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _cone_cases(cases: Cases) -> None:
    """Pin blast_radius and the importers relation."""
    _check(
        cases,
        "blast_radius is every transitive importer, seeds excluded",
        ok=ic.blast_radius(_DAG, [_A]) == _A_CONE,
    )
    _check(
        cases,
        "a source nothing imports has an empty cone",
        ok=ic.blast_radius(_DAG, ["Substrate/Lone.agda"]) == set(),
    )
    _check(
        cases, "an unknown source is not a seed", ok=ic.blast_radius(_DAG, ["nope.agda"]) == set()
    )
    _check(
        cases,
        "importers_of answers direct importers as sorted relpaths",
        ok=ic.importers_of(_DAG)(_A) == ["Substrate/OnlyA.agda", "Substrate/Shared.agda"],
    )


def _leverage_cases(cases: Cases) -> None:
    """Pin cost, cone, ranking, and exclusivity."""
    lv = ic.leverage(_DAG, [_A, _B])
    _check(
        cases,
        "n_seeds is the cost and n_cone the union of the cones",
        ok=lv.n_seeds == 2
        and lv.n_cone == len(_A_CONE | _B_CONE)  # noqa: PLR2004 - two seeds
        and lv.members == sorted(_A_CONE | _B_CONE),
    )
    _check(cases, "exclusivity is UNDEFINED without against", ok=lv.exclusive is None)
    _check(
        cases,
        "the ranking is whole and descending: A reaches 3, B reaches 2",
        ok=lv.top == [(3, _A), (2, _B)],
    )
    ex = ic.leverage(_DAG, [_A], against=[[_B]])
    _check(
        cases,
        "against B, A's exclusive cone is OnlyA alone - the overlap subtracted",
        ok=ex.exclusive == 1
        and ex.exclusive_members == ["Substrate/OnlyA.agda"]
        and ex.n_cone == len(_A_CONE),
    )


def _differential_cases(cases: Cases) -> None:
    """Assert both functions agree with the origin over the pre-filled memo, or skip."""
    o = _origin()
    if o is None:
        _check(cases, "differential: origin unavailable, skipped", ok=True)
        return
    _check(
        cases,
        "differential: _blast_radius agrees",
        ok=o._blast_radius([_A, _B]) == ic.blast_radius(_DAG, [_A, _B]),
    )  # noqa: SLF001
    theirs = o.leverage([_A, _B])
    ours = ic.leverage(_DAG, [_A, _B])
    _check(
        cases,
        "differential: leverage cone/cost/members agree",
        ok=(theirs[0], theirs[1]) == (ours.n_cone, ours.n_seeds)
        and theirs.members == ours.members
        and theirs.exclusive is None,
    )
    theirs_ex = o.leverage([_A], against=([_B],))
    _check(
        cases,
        "differential: exclusive count agrees",
        ok=theirs_ex.exclusive == ic.leverage(_DAG, [_A], against=[[_B]]).exclusive,
    )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _cone_cases(cases)
    _leverage_cases(cases)
    _differential_cases(cases)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"import_cone_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
