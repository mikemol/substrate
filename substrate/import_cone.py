#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What a set of modules BLOCKS - the import cone, bound over the DAG and the cone algebra.

THE EIGHTH CUT OF THE DRAIN'S FOURTH FILE (`scratch/split_census.py:48-227`, W4 tick 47), AND
IT IS A BINDING, NOT A MODULE. The reuse-search fired twice: the origin's `_import_dag` tuple
`(disk, deps, rdeps, src_to_mod)` IS `substrate.agda_dag.Dag`, field for field, and its
`leverage` was already "the edge relation plus a call" into `dagcone`, which
`substrate.dagcone` carries (`reach`, `rank`, `exclusive`). What remains is the domain: the
IMPORTERS relation over source relpaths, which is what this file spells once.

`blast_radius` IS A FINDING, NOT A GAP. Given the modules `make` reported as failed, these
are the ones it therefore never attempted - so their `stale` verdict means BLOCKED, not
unmeasured. The reverse edges are the SAME relation the build's prerequisites are generated
from and the same one freshness is judged by: one import DAG, three consumers, and a private
re-scan here is how two authorities for one relation start disagreeing.

`leverage` REPORTS PARTICIPATION, NEVER "WOULD FREE". A cone is reachability - every module
transitively importing the seeds - and a module in it can sit behind several blocking sets at
once, so clearing this set frees only the modules whose remaining blockers are all inside it.
Measured over three real buckets: 538 to 205, 417 to 97, 298 to 82 exclusive - 60-75% shared,
so the naive reading was wrong by ~4x and the three figures never summed. `against` supplies
the OTHER blocking sets; without them exclusivity is UNDEFINED (None), not total. The cone
excludes the seeds: `n_seeds` is the COST and `n_cone` the LEVERAGE, and a large cost with no
cone is the sunk-cost shape. `top` is the seed ranking WHOLE - the origin's `[:5]` was a
display decision frozen into the computation, and the cap belongs at the print.

⚑ `Leverage` IS A DATACLASS, NOT A TUPLE SUBCLASS WITH ATTRIBUTES. The origin grew a fourth
field on a positional tuple and four selftest cases silently broke - its own comment names
"a tuple whose meaning is its index" as the defect - then subclassed `tuple` to keep the
unpack working. A consumer of the shim that unpacks positionally is the shim's to adapt;
the package names its fields.

⚑ THE DAG THE ORIGIN PARSED ONCE PER PROCESS IS THE CALLER'S TO HOLD. Ranking 121 failures by
cone size once re-ran a ~3000-source walk 121 times to rebuild the same graph; the fix was
memoisation at the owner, not parallelism (before reaching for concurrency, check whether the
work is repeated). `agda_dag.parse()` is that one parse; this module takes its result.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import dagcone

if TYPE_CHECKING:
    from collections.abc import Iterable

    from substrate.agda_dag import Dag


def importers_of(dag: Dag) -> dagcone.Successors[str]:
    """Return the edge relation over SOURCE RELPATHS: a source's direct in-tree importers."""
    disk, rdeps, src_to_mod = dag.disk, dag.rdeps, dag.src_to_mod

    # ⚑ `node`, because `Successors.__call__` names it so and a Protocol matches by name.
    def importers(node: str) -> list[str]:
        m = src_to_mod.get(node)
        if m is None:
            return []
        return [disk[i] for i in sorted(rdeps.get(m, ())) if i in disk]

    return importers


def blast_radius(dag: Dag, failed_srcs: Iterable[str]) -> set[str]:
    """Return every source transitively IMPORTING one of `failed_srcs` - the blocked cone."""
    return dagcone.reach(list(failed_srcs), importers_of(dag))


@dataclass(frozen=True)
class Leverage:
    """What a seed set participates in blocking: its cost, its cone, and its ranking."""

    n_cone: int
    n_seeds: int
    top: list[tuple[int, str]]
    members: list[str]
    # None when no `against` was supplied: exclusivity is then UNDEFINED, not total.
    exclusive: int | None = None
    exclusive_members: list[str] | None = None


def leverage(dag: Dag, srcs: Iterable[str], against: Iterable[Iterable[str]] = ()) -> Leverage:
    """Return the cone, cost and seed ranking of `srcs`, and the exclusive cone if asked."""
    seeds = list(srcs)
    importers = importers_of(dag)
    reached = dagcone.reach(seeds, importers)
    others = [list(g) for g in against]
    excl = dagcone.exclusive(seeds, others, importers) if others else None
    return Leverage(
        n_cone=len(reached),
        n_seeds=len(seeds),
        top=dagcone.rank(seeds, importers),
        members=sorted(reached),
        exclusive=None if excl is None else len(excl),
        exclusive_members=None if excl is None else sorted(excl),
    )
