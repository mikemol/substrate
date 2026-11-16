#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The SQL and numpy bridges into the graded relational carrier - two more GradedHomOvers.

THE FOURTH CUT OF THE DRAIN'S THIRD FILE (`jea/metalanguage/sql_lift.py:197-281`, W4 tick 33).
`rel_of_select` lowers an SQLAlchemy Core `Select` to its Rel head-set in SQL evaluation order,
from the statement's clause STATE - a recursive CTE among its froms is the L7 reachability
closure (`("Closure",)`, the recursion-to-parallel transition); otherwise Scan, then Join /
Filter / GroupBy / Agg / Distinct / OrderBy / Limit as each clause is present. `rel_of_np` lowers
a chain of numpy-builder names to the SAME heads, so co-interning the two reaches ONE carrier
point - the CrossMix leg of the SQL-numpy hexagon, whose VALUE identity `numpy_builders` proves
separately, byte-exact.

EVERY ATTRIBUTE READ HERE IS DECLARED IN THE STUB FROM THE LIBRARY SOURCE (gate-G415, tick 32).
The origin reached them through `getattr(stmt, "_where_criteria", ())` and
`type(f).__name__ == "CTE"` - a string compare on a class name, and `Any` on every read. Here
each is an `isinstance` against the declared class and a typed attribute, so a renamed clause
attribute is a type error at the reader rather than a silently-empty head-set.

THE INTERNER AND THE COHERENCE PREDICATE ARE PARAMETERS. `np_sql_coherent` in the origin interns
both sides into `jea_pyalg.Intern` and asks `CrossMix(I).coherent(p, s)` - bare imports a clean
module cannot reach. Coherence at degree 0 IS same-interned-id, so the caller passes the
interner it holds (the `rel_term.RelTerm.intern_into` shape) and a `coherent(p, s) -> bool`;
the default predicate is equality of ids, which is what degree-0 coherence means.

THE SOURCE IS THE FIRST NAMED FROM, ELSE '*'. A `NamedFromClause` carries `name`; a `Join` does
not, and a select over a join alone reports `'*'` - the origin's reading, kept.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.sql import visitors
from sqlalchemy.sql.functions import Function
from sqlalchemy.sql.selectable import CTE, Join, NamedFromClause, Select

from substrate.rel_term import RelTerm

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from sqlalchemy.sql.selectable import FromClause

# The SQL aggregate names an Agg head stands for.
AGGREGATES = frozenset({"count", "sum", "max", "min", "avg"})
# numpy-builder function name -> the Rel head it realises.
NP_HEAD: dict[str, str] = {
    "np_scan": "Scan",
    "np_filter": "Filter",
    "np_distinct": "Distinct",
    "np_group_count": "GroupBy",
    "np_order": "OrderBy",
    "np_limit": "Limit",
    "np_join": "Join",
    "np_closure": "Closure",
}

Interner = "Callable[[str, str | None, tuple[int, ...]], int]"


def has_aggregate(stmt: Select) -> bool:
    """Return whether any selected column contains a named aggregate function call."""
    for col in stmt.selected_columns:
        for el in visitors.iterate(col):
            if isinstance(el, Function) and el.name.lower() in AGGREGATES:
                return True
    return False


def select_source(froms: Iterable[FromClause]) -> str:
    """Return the first named FROM element's name, else '*'."""
    for f in froms:
        if isinstance(f, NamedFromClause) and f.name:
            return f.name
    return "*"


def rel_of_select(stmt: Select) -> RelTerm:
    """Lower a Select to its Rel heads in SQL evaluation order over its source."""
    froms = list(stmt.get_final_froms())
    if any(isinstance(f, CTE) and f.recursive for f in froms):
        return RelTerm(("Closure",), select_source(froms))
    heads = ["Scan"]
    if any(isinstance(f, Join) for f in froms):
        heads.append("Join")
    if stmt._where_criteria:  # noqa: SLF001 - the clause state, declared in the stub from the library
        heads.append("Filter")
    if stmt._group_by_clauses:  # noqa: SLF001
        heads.append("GroupBy")
    if has_aggregate(stmt):
        heads.append("Agg")
    if stmt._distinct:  # noqa: SLF001
        heads.append("Distinct")
    if stmt._order_by_clauses:  # noqa: SLF001
        heads.append("OrderBy")
    if stmt._limit_clause is not None:  # noqa: SLF001
        heads.append("Limit")
    return RelTerm(tuple(heads), select_source(froms))


def rel_of_np(np_heads: Iterable[str], source: str = "*") -> RelTerm:
    """Lower a chain of numpy-builder names to Rel heads; a group-count emits GroupBy then Agg."""
    heads: list[str] = []
    for h in np_heads:
        rh = NP_HEAD[h]
        heads.append(rh)
        if rh == "GroupBy":
            heads.append("Agg")
    return RelTerm(tuple(heads), source)


def _same(p: int, s: int) -> bool:
    """Degree-0 coherence: the two sides interned to one carrier node."""
    return p == s


def np_sql_coherent(
    intern: Callable[[str, str | None, tuple[int, ...]], int],
    np_heads: Iterable[str],
    stmt: Select,
    coherent: Callable[[int, int], bool] = _same,
) -> bool:
    """Return whether the numpy chain and the Select lower to ONE carrier node, Scan abstracted."""
    p_heads = tuple(h for h in rel_of_np(np_heads).canon_seq() if h != "Scan")
    s_heads = tuple(h for h in rel_of_select(stmt).canon_seq() if h != "Scan")
    return coherent(RelTerm(p_heads).intern_into(intern), RelTerm(s_heads).intern_into(intern))
