# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The origin's graph API, served from the clean model — so `gen_build_makefiles` can become a shim.

⚑⚑⚑ WHAT THE CONSUMERS BOUND TO, KEPT EXACTLY. `scripts/build_census`, `scratch/fix_notinscope`
and friends import `parse_tree`, `kahn_depth`, `kahn_check` and `IMPRE` from the generator by bare
name. Their SHAPES are the contract: `parse_tree()` → `(dict[module, relpath], dict[module,
set[module]])` with mutable `set`s, `kahn_depth` → `(depth, order)`, and a cycle EXITS the
process with code 2 — `fix_notinscope` relies on that to reach its fallback. The model
(`agda_dag`) returns a `Cycle` value instead; the exit is re-imposed HERE, at the compat seam,
rather than pushed back into the model that was cleaned of it.

⚑⚑ THE GRAPH IS PROVEN EQUAL BEFORE IT IS SERVED. `graph_parity_selftest` holds `agda_dag.parse`
(with the origin's stripper) equal to the origin's `parse_tree` on every module and edge — so this
module changes where the graph comes from, never what it is.

⚑ THE STRIPPER IS INJECTED. `scripts/_agdatext.strip` is a bare `scripts/` module; the shim, which
lives there, passes it in.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from substrate import agda_dag

if TYPE_CHECKING:
    import re

#: The in-tree import pattern: the model's, held equal to the origin by `graph_parity_selftest`.
IMPRE: re.Pattern[str] = agda_dag.IMPORT_RE
#: The exit code the origin used for a cycle; `fix_notinscope` catches it.
CYCLE_EXIT = 2


def parse_tree(strip: agda_dag.Stripper) -> tuple[dict[str, str], dict[str, set[str]]]:
    """Return `(disk, deps)` in the origin's shape: module → relpath, module → set of imports."""
    dag = agda_dag.parse(strip=strip)
    return dict(dag.disk), {m: set(v) for m, v in dag.deps.items()}


def kahn_depth(disk: dict[str, str], deps: dict[str, set[str]]) -> tuple[int, list[str]]:
    """Return `(critical_path_depth, order)`; a cycle EXITS with code 2, as the origin did."""
    dag = agda_dag.Dag(disk=dict(disk), deps={m: frozenset(v) for m, v in deps.items()})
    walked = agda_dag.topo(dag)
    if isinstance(walked, agda_dag.Cycle):
        sys.stderr.write(f"gen_build_makefiles: ⚠ {walked.message}\n")
        raise SystemExit(CYCLE_EXIT)
    depth, order = walked
    return depth, list(order)


def kahn_check(disk: dict[str, str], deps: dict[str, set[str]]) -> None:
    """Refuse a cyclic graph (exit 2); return nothing when it is acyclic."""
    kahn_depth(disk, deps)
