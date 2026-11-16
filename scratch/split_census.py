#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""split_census - the READ side of the split pipeline, now a shim over the package.

THIS FILE IS ADAPTORS (W4 file 4 swap, tick 49). Every mechanism it once held lives in
`substrate/` and is witnessed there: the import DAG is `agda_dag.parse`; the blocked cone and
the leverage verdict are `import_cone`; the log index and the freshness predicate are
`log_freshness`; the error classifier and its remedy table are `agda_error_class`; the build
census and the stale split are `agda_build_census`; the one-command census is
`agda_run_census`; the content stamp and the split-leaf population are `agda_tree_state`.
What stays here is the SHAPE sixteen bare consumer sites reach through `split_pipeline`:

- `_import_dag()` returns the `(disk, deps, rdeps, src_to_mod)` TUPLE and memoises it in the
  module-level `_DAG` dict under the origin's keys, because a consumer pre-fills that dict to
  drive the readers over a fixture graph (`import_cone_selftest` does exactly this).
- `leverage(...)` returns the origin's `Leverage` - a 3-tuple subclass carrying `.exclusive`
  and `.members` - because three sites unpack `n_cone, n_seeds, top = leverage(...)` and a
  fourth reads the attributes. The package's `Leverage` is a dataclass; this class is the
  adaptor and its only reason to exist, so it retires with the last positional unpack.
- `run_census(...)` returns the log path on success and the integer 2 on a straddled tree -
  the origin's forked return shape, kept for `split_pipeline --census`.
- `root` defaults to `"agda"` everywhere, as the origin's did.

The origin's docstrings were the record of why each reader exists; each package module
carries its own now, and this file does not repeat them.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Self

from substrate import (
    agda_build_census,
    agda_dag,
    agda_error_class,
    agda_run_census,
    agda_tree_state,
    import_cone,
    log_freshness,
)
from substrate.agda_error_class import CLASS_REMEDY, is_other, other_kind

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

__all__ = [
    "CLASS_REMEDY",
    "_DAG",
    "_LOG_INDEX",
    "Leverage",
    "_blast_radius",
    "_classify",
    "_import_dag",
    "_log_index",
    "census_from_build",
    "is_other",
    "leaves",
    "leverage",
    "log_is_fresh",
    "other_kind",
    "run_census",
    "stale_why",
    "tree_stamp",
]

ROOT = str(Path(__file__).resolve().parent.parent)
AG = "agda"
# How many ranked seeds the origin's leverage carried in its tuple - a display cap, kept here
# only because the tuple shape is the adaptor's contract.
_TOP_CAP = 5

DagTuple = tuple[dict[str, str], dict[str, set[str]], dict[str, set[str]], dict[str, str]]

# The memo, under the origin's keys. Pre-fill it to run the readers over a fixture graph.
_DAG: dict[str, object] = {}
_LOG_INDEX: dict[str, dict[str, str]] = {}


def _import_dag() -> DagTuple:
    """Return (disk, deps, rdeps, src_to_mod), parsed once per process and memoised in `_DAG`."""
    if not _DAG:
        dag = agda_dag.parse()
        _DAG.update(disk=dict(dag.disk), deps={m: set(v) for m, v in dag.deps.items()},
                    rdeps={m: set(v) for m, v in dag.rdeps.items()},
                    src_to_mod=dict(dag.src_to_mod))
    disk = _DAG["disk"]
    deps = _DAG["deps"]
    rdeps = _DAG["rdeps"]
    s2m = _DAG["src_to_mod"]
    if not (isinstance(disk, dict) and isinstance(deps, dict) and isinstance(rdeps, dict)
            and isinstance(s2m, dict)):
        msg = "_DAG memo holds something other than the four maps"
        raise TypeError(msg)
    return disk, deps, rdeps, s2m


def _dag() -> agda_dag.Dag:
    """Return the memoised graph as the package's own type."""
    disk, deps, _rdeps, _s2m = _import_dag()
    return agda_dag.Dag(disk=disk, deps={m: frozenset(v) for m, v in deps.items()})


def _blast_radius(failed_srcs: Iterable[str], root: str = AG) -> set[str]:  # noqa: ARG001 - the origin's arity
    """Return every source transitively importing one of `failed_srcs`."""
    return import_cone.blast_radius(_dag(), failed_srcs)


class Leverage(tuple[int, int, list[tuple[int, str]]]):  # noqa: SLOT001 - a tuple subclass cannot take non-empty __slots__, and an empty one drops the __dict__ these attributes live in
    """The origin's shape: a 3-tuple `(n_cone, n_seeds, top)` carrying three attributes."""

    exclusive: int | None
    members: list[str] | None
    exclusive_members: list[str] | None

    def __new__(cls, n_cone: int, n_seeds: int, top: list[tuple[int, str]]) -> Self:
        """Build the tuple; the attributes are hung on by `of`."""
        self = super().__new__(cls, (n_cone, n_seeds, top))
        self.exclusive = None
        self.members = None
        self.exclusive_members = None
        return self

    @classmethod
    def of(cls, lv: import_cone.Leverage) -> Leverage:
        """Adapt the package's dataclass to the origin's tuple shape."""
        self = cls(lv.n_cone, lv.n_seeds, lv.top[:_TOP_CAP])
        self.exclusive = lv.exclusive
        self.members = lv.members
        self.exclusive_members = lv.exclusive_members
        return self


def leverage(srcs: Iterable[str], root: str = AG,  # noqa: ARG001 - the origin's arity
             against: Iterable[Iterable[str]] = ()) -> Leverage:
    """Return the origin-shaped leverage over the package's verdict."""
    return Leverage.of(import_cone.leverage(_dag(), srcs, against))


def _log_index(root: str = AG) -> dict[str, str]:
    """Return module -> `.agdai.log` path, one walk per root, memoised in `_LOG_INDEX`."""
    if root not in _LOG_INDEX:
        _LOG_INDEX[root] = log_freshness.log_index(Path(root) / "_build")
    return _LOG_INDEX[root]


def log_is_fresh(src_rel: str, root: str = AG) -> log_freshness.Verdict:
    """Return (fresh?, log_path | None, why) for one source."""
    return log_freshness.log_is_fresh(src_rel, _dag(), _log_index(root),
                                      log_freshness.mtime_on_disk, str(Path(ROOT) / root))


def _classify(path: str, txt: str,  # noqa: ARG001 - the origin's arity; the path never decided anything
              trace: list[str] | None = None) -> agda_error_class.Verdict:
    """Return (kind, detail, remedy) for one compile's error text.

    ⚑ THE LEAF PROBE FOLLOWS `AG`, as the origin's did - a suite repoints `AG` at a temporary
    tree to drive the consumed-parent branch, and the first shim ignored it (caught by
    `agda_error_class_selftest`'s differential the moment the swap landed).
    """
    base = Path(AG) if Path(AG).is_absolute() else Path(ROOT) / AG
    probe = agda_error_class.leaves_on_disk(base.parent, base.name)
    return agda_error_class.classify(txt, probe, trace)


def _tree(root: str) -> agda_build_census.Tree:
    """Return the build tree the census reads, over the memoised DAG and log index."""
    return agda_build_census.Tree(_dag(), _log_index(root), str(Path(ROOT) / root))


def census_from_build(root: str = AG) -> list[agda_build_census.Row]:
    """Return [(module_path, verdict, cited)] read from the build's own logs."""
    return agda_build_census.census(_tree(root))


def stale_why(root: str = AG) -> list[agda_build_census.Why]:
    """Return [(module, cause, witness)] for every stale module."""
    tree = _tree(root)
    return agda_build_census.stale_why(agda_build_census.census(tree), tree)


def run_census(root: str = AG, jobs: int | None = None) -> str | int:
    """BUILD then READ: return the log path, or 2 when the tree changed during the build."""
    flag: Sequence[str] = [f"-j{jobs}"] if jobs else agda_build_cmd_jobs()
    run = agda_run_census.run_census(ROOT, flag, agda_dir=root)
    return run.log if run.banked else run.exit


def agda_build_cmd_jobs() -> Sequence[str]:
    """Return the `-j` fragment from the ONE authority, or the bare `-j` fallback."""
    try:
        import gen_build_makefiles  # noqa: PLC0415 - scripts/, reachable only beside the tree
    except ImportError:
        return ("-j",)
    return list(gen_build_makefiles.jobs_flag())


def tree_stamp(root: str = AG) -> str:
    """Return `<count>:<newest mtime>` over the sources under `root`."""
    return agda_tree_state.tree_stamp(str(Path(ROOT) / root))


def leaves(root: str = AG) -> list[str]:
    """Return every split-emitted leaf under `root`."""
    return agda_tree_state.leaves(str(Path(ROOT) / root))
