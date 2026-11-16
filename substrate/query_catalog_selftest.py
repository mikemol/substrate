#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.query_catalog` — a DIFFERENTIAL on each builder's rendered SQL.

⚑⚑ THE REPLICA IS VERIFIED, NOT BELIEVED. Each builder is CALLED on both sides — the origin's,
loaded HERE by path and nowhere else, and the replica's — and the two statements are rendered to
SQL text, which must be IDENTICAL: that text is what the committed query cache stores.

⚑ AND A NEGATIVE CONTROL: two different builders must render differently, or the equality could be
passing on a rendering that ignores its input.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import TYPE_CHECKING

from substrate import corpus, query_catalog

if TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy.sql.selectable import Select

# The origin module, relative to the tree.
_ORIGIN = ("jea", "metalanguage", "query_decl.py")

# The replica's builders, by the name the origin defines each under.
_REPLICA: dict[str, Callable[[], Select]] = {
    "v_structs": query_catalog.v_structs,
    "v_members": query_catalog.v_members,
    "v_refs": query_catalog.v_refs,
    "v_edges": query_catalog.v_edges,
    "v_module_edges": query_catalog.v_module_edges,
    "v_modules": query_catalog.v_modules,
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


def _origin_sql(origin: object, name: str) -> str:
    """Return the SQL text of the origin's builder `name`, or a marker when it is not callable."""
    builder: object = getattr(origin, name, None)
    if not callable(builder):
        return f"<origin has no builder {name}>"
    stmt: object = builder()
    return str(stmt)


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    origin = _origin()
    if origin is None:
        return [("the origin loads", False)]
    out: list[tuple[str, bool]] = [("the origin loads", True)]
    for name, builder in _REPLICA.items():
        theirs = _origin_sql(origin, name)
        mine = str(builder())
        if theirs != mine:
            sys.stdout.write(f"  {name}:\n    origin:  {theirs}\n    replica: {mine}\n")
        out.append((f"{name} renders the origin's SQL", theirs == mine))
    control = str(query_catalog.v_edges()) != str(query_catalog.v_modules())
    out.append(("two different builders render differently (negative control)", control))
    return out


def selftest() -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"query-catalog selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 1)
