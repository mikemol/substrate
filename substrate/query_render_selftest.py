#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.query_render` and `substrate.query_ops` — a DIFFERENTIAL on the SQL.

⚑⚑ THE REPLICA IS VERIFIED, NOT BELIEVED. Each render builder is CALLED on both sides — the
origin's, loaded HERE by path and nowhere else, and the replica's — and the rendered SQL must be
IDENTICAL, since that text is what the committed query cache stores. Two builders here compare
through `query_ops.eq` (`q_modules_index`, `q_sitemap`), so their equality is also the evidence
that `eq(col, v)` renders exactly as the origin's `col == v`.

⚑ AND `eq`'s REFUSAL IS CASED: a comparison that does not build a SQL expression must raise, or
the narrowing would be a cast in disguise.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import TYPE_CHECKING

from sqlalchemy import ColumnElement

from substrate import corpus, query_ops, query_render

if TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy.sql.selectable import Select

# The origin module, relative to the tree.
_ORIGIN = ("jea", "metalanguage", "query_decl.py")

# The replica's builders, by the name the origin defines each under.
_REPLICA: dict[str, Callable[[], Select]] = {
    "q_structs_index": query_render.q_structs_index,
    "q_structs_namemod": query_render.q_structs_namemod,
    "q_structs_fpnamemod": query_render.q_structs_fpnamemod,
    "q_modules_index": query_render.q_modules_index,
    "q_structs_qnamekind": query_render.q_structs_qnamekind,
    "q_edges_all": query_render.q_edges_all,
    "q_sitemap": query_render.q_sitemap,
    "q_structs_count": query_render.q_structs_count,
    "q_edges_dst_distinct": query_render.q_edges_dst_distinct,
    "q_edges_src_distinct": query_render.q_edges_src_distinct,
    "q_structs_qname": query_render.q_structs_qname,
    "q_indegree_top": query_render.q_indegree_top,
    "q_modedges_all": query_render.q_modedges_all,
}


class _NotSql(ColumnElement[object]):
    """A column whose `==` answers a plain bool — the case `eq` must refuse."""

    def __eq__(self, other: object) -> bool:
        """Answer a plain bool, as a non-SQL comparison would."""
        return other is self

    def __hash__(self) -> int:
        """Hash by identity, since `__eq__` is overridden."""
        return id(self)


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


def _eq_refuses() -> bool:
    """Report whether `eq` raises on a comparison that builds no SQL expression."""
    try:
        query_ops.eq(_NotSql(), 1)
    except TypeError:
        return True
    return False


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
    control = str(query_render.q_edges_all()) != str(query_render.q_modedges_all())
    out.append(("two different builders render differently (negative control)", control))
    out.append(("eq refuses a comparison that builds no SQL", _eq_refuses()))
    return out


def selftest() -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"query-render selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 1)
