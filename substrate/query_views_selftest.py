#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.query_views` — a DIFFERENTIAL on the compiled SQL, subquery by subquery.

⚑⚑ THE REPLICA IS VERIFIED, NOT BELIEVED. `query_views` rebuilds four compositions the origin gets
from `schema_decl` and subqueries in `query_decl`. The origin is loaded HERE, in the suite only,
and each subquery is selected from on both sides and rendered to SQL text; the texts must be
IDENTICAL. Text equality is the right bar because the SQL text is exactly what the committed
query cache stores — a replica that composes differently but "means the same" would still make the
cache drift.

⚑ AND A NEGATIVE CONTROL: the same comparison across two DIFFERENT subqueries must fail, or the
equality below could be passing on a rendering that ignores its input.
"""

from __future__ import annotations

import importlib.util
import sys

from sqlalchemy import select

from substrate import corpus, query_views

# The origin module, relative to the tree.
_ORIGIN = ("jea", "metalanguage", "query_decl.py")

# The replica's subqueries, by the name the origin binds each to.
_REPLICA: dict[str, object] = {
    "node_v": query_views.node_v,
    "unit_v": query_views.unit_v,
    "node_fanin": query_views.node_fanin,
    "shared_subtree": query_views.shared_subtree,
}


def _origin() -> object | None:
    """Load the origin module by path, or None when it cannot be loaded."""
    path = corpus.ROOT.joinpath(*_ORIGIN)
    spec = importlib.util.spec_from_file_location("_query_decl_origin", path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sql(subquery: object) -> str:
    """Return the SQL text of selecting everything from `subquery`."""
    return str(select(subquery))


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    origin = _origin()
    if origin is None:
        return [("the origin loads", False)]
    out: list[tuple[str, bool]] = [("the origin loads", True)]
    for name, replica in _REPLICA.items():
        found: object = getattr(origin, name, None)
        theirs = _sql(found)
        mine = _sql(replica)
        if theirs != mine:
            sys.stdout.write(f"  {name}:\n    origin:  {theirs}\n    replica: {mine}\n")
        out.append((f"{name} compiles to the origin's SQL", theirs == mine))
    control = _sql(query_views.node_v) != _sql(query_views.unit_v)
    out.append(("two different subqueries render differently (negative control)", control))
    return out


def selftest() -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"query-views selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 1)
