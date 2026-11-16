#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What a SQLAlchemy Core statement READS, WRITES and RETURNS — exact, from the statement tree.

⚑⚑⚑ THE FOURTH CUT OF THE DRAIN'S SECOND FILE. `query_defs` held five readers over compiled
builder statements — `written_table`, `returned_columns`, `_table_occurrences`, `_tables_of`,
`_columns_of` — each pure over the statement object and each carrying a measured correction.
They read `_MD.tables` (the declared relation vocabulary) from module scope; here that vocabulary
is a PARAMETER, so the readers say what they read and a fixture can declare its own. The cut
waited on `stubs/sqlalchemy/` declaring the statement surface (W19, gate-G409); every attribute
this module reads is one that stub transcribed from the library.

⚑⚑ EVERY READER WALKS THE TREE, NEVER THE SURFACE. `get_final_froms()` answers the wrong
question for a composed builder — it returns the OUTERMOST froms, so a table scanned inside a
recursive CTE is one layer down and invisible. Measured: `--touching obs` reported ONE reader
where four builders read `obs` through CTEs. The statements are SQLAlchemy Core objects, so
`sqlalchemy.sql.visitors.iterate` walks them, and the surface accessor was a wrong accessor,
not a missing mode (operator, 2026-08-15: *"they're surely not just raw SQL… we can decompose
them with ast"*).

⚑⚑ FOUR MEASURED CORRECTIONS ARE KEPT AS RULES:
  - A WRITE IS NOT A READ. `tables_of` over `INSERT INTO ref SELECT …` reports `ref`, so the
    insert read as a READER of the relation it populates and every edge ran backwards.
    `written_table` reads the statement TYPE, and it SEARCHES THE TREE: `q_pack_level_insert`
    is a `Select` over a data-modifying CTE, and a top-level `isinstance` reported zero writes
    for a builder whose entire purpose is writing.
  - AN ALIAS IS NOT A TABLE. `q_fanin` joins `terms` four times as aliases; an `isinstance(t,
    Table)` on `Column.table` skipped every one, and `--touching terms` omitted the RETIRE
    LICENCE from the per-column readers — under-reporting in the direction that licenses a
    drop. `.element` unwraps an alias layer, iterated, bounded.
  - A CTE HAS A NAME TOO. Only a DECLARED relation may be reported, so membership in the
    declared vocabulary is the filter for tables and for columns alike.
  - A DML STATEMENT RETURNS ONLY WHAT IT `RETURNING`s; a `Select` returns its selected columns.
    Reads and returns are DIFFERENT flow edges (operator, 2026-08-15), and `q_pack_level` vs
    `q_pack_level_summary` — 529,003 rows vs three scalars over one input — is the lift itself.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, Table
from sqlalchemy.sql import dml, visitors
from sqlalchemy.sql.selectable import AliasedReturnsRows, SelectBase

if TYPE_CHECKING:
    from collections.abc import Iterable

    from sqlalchemy.sql.visitors import ExternallyTraversible

# How many alias layers `_declared_table` unwraps before giving up — a bound, not a limit met.
_ALIAS_DEPTH = 8

_DML = (dml.Insert, dml.Update, dml.Delete)


def _nodes(stmt: ExternallyTraversible) -> Iterable[ExternallyTraversible]:
    """Yield every node of the statement tree, breadth-first."""
    return visitors.iterate(stmt)


def written_table(stmt: ExternallyTraversible) -> str | None:
    """Return the table a DML statement WRITES — anywhere in the tree — or None for a pure read."""
    for node in _nodes(stmt):
        if isinstance(node, _DML) and isinstance(node.table, Table):
            return node.table.name
    return None


def returned_columns(stmt: ExternallyTraversible) -> list[str]:
    """Return the column names a statement HANDS BACK, or [] if it returns nothing."""
    if isinstance(stmt, _DML):
        return [c.name if isinstance(c, Column) else str(c) for c in stmt._returning]  # noqa: SLF001 - RETURNING has no public raw accessor
    if isinstance(stmt, SelectBase):
        return [str(k) for k in stmt.selected_columns.keys()]  # noqa: SIM118 - a ColumnCollection, not a dict
    return []


def table_occurrences(stmt: ExternallyTraversible, table: str) -> int:
    """Count how often `table` appears in the tree — more than once for a DML is a fixpoint."""
    return sum(1 for n in _nodes(stmt) if isinstance(n, Table) and n.name == table)


def tables_of(stmt: ExternallyTraversible, declared: frozenset[str]) -> frozenset[str]:
    """Return every DECLARED table the statement reads, through CTEs and subqueries."""
    return frozenset(n.name for n in _nodes(stmt) if isinstance(n, Table) and n.name in declared)


def _declared_table(node: Column[object]) -> Table | None:
    """Return the base Table under a column's `.table`, unwrapping alias layers, or None."""
    t: object = node.table
    for _ in range(_ALIAS_DEPTH):
        if isinstance(t, Table) or t is None:
            break
        t = t.element if isinstance(t, AliasedReturnsRows) else None
    return t if isinstance(t, Table) else None


def columns_of(stmt: ExternallyTraversible, table: str, declared: frozenset[str]) -> frozenset[str]:
    """Return every DECLARED column of `table` the statement mentions, through aliases."""
    out: set[str] = set()
    for node in _nodes(stmt):
        if not isinstance(node, Column):
            continue
        base = _declared_table(node)
        if base is not None and base.name == table and base.name in declared:
            out.add(node.name)
    return frozenset(out)
