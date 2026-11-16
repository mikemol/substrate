#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `sql_statement` — the four recorded corrections, pinned over an in-memory schema.

⚑ EVERY CASE IS A STATEMENT OBJECT, NEVER A STRING. The readers walk the SQLAlchemy Core tree,
so a fixture that compiled to SQL and matched text would test a different reader than the one
shipped. The schema is declared here, in memory, and `declared` is passed explicitly — which is
what makes the CTE-has-a-name-too rule testable: a name outside `declared` must not be reported
even when it appears in the tree.

⚑ THE COLUMN TYPE IS A `TypeEngine[object]` SUBCLASS, NOT `Integer`, AND THE STUB IS WHY. The
stub's `TypeEngine` is invariant as upstream declares it, so `Column("x", Integer())` is a
`Column[int]` and `Table(*args: Column[object])` refuses it. `row_upsert_selftest` met the same
wall and answered it the same way; the fixture type is what lets one table mix element types.

⚑ TWO CORRECTIONS ARE NAMED AND NOT PINNED, AND THE REASON IS THE STUB, NOT THE READER. The
INSERT-inside-a-CTE case (`q_pack_level_insert`) needs `Select.cte()`, and the alias-unwrap case
(`q_fanin`) needs `Table.alias()`; `stubs/sqlalchemy/` declines the generative surface, so a
fixture cannot build either statement under the per-file gate. Both readers carry the rule
(`written_table` SEARCHES the tree; `_declared_table` unwraps `AliasedReturnsRows.element`), and
the residue arm below says what a future stub widening would let this suite assert.
"""

from __future__ import annotations

import sys

from sqlalchemy import Column, MetaData, Table
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.selectable import Select
from sqlalchemy.sql.type_api import TypeEngine

from substrate import sql_statement as ss


class _AnyInt(TypeEngine[object]):
    """An integer column type parameterised at the top type, so the fixture table type-checks."""

    __visit_name__ = "integer"


_MD = MetaData()
_OBS = Table("obs", _MD, Column("core_id", _AnyInt()), Column("local_id", _AnyInt()))
_REF = Table("ref", _MD, Column("core_id", _AnyInt()))
_DECLARED = frozenset({"obs", "ref"})

# The two corrections the stub cannot yet let a fixture build — named so a widening knows its job.
_UNBUILDABLE = ("INSERT inside a CTE", "alias unwrap through .element")
_UNBUILDABLE_COUNT = 2

Cases = list[tuple[str, bool]]


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _select_cases(cases: Cases) -> None:
    """Pin that a SELECT reads its tables, returns its columns, and writes nothing."""
    stmt = Select(_OBS.c["core_id"], _OBS.c["local_id"])
    _check(cases, "select: reads the declared table", ok=ss.tables_of(stmt, _DECLARED) == {"obs"})
    _check(
        cases,
        "select: returns its selected columns",
        ok=ss.returned_columns(stmt) == ["core_id", "local_id"],
    )
    _check(
        cases, "select: a write is not a read — no written table", ok=ss.written_table(stmt) is None
    )
    _check(
        cases,
        "select: columns of the table it mentions",
        ok=ss.columns_of(stmt, "obs", _DECLARED) == {"core_id", "local_id"},
    )
    _check(
        cases,
        "select: columns of a table it does not mention are empty",
        ok=ss.columns_of(stmt, "ref", _DECLARED) == frozenset(),
    )


def _insert_cases(cases: Cases) -> None:
    """Pin that an INSERT writes its target, returns only RETURNING, and occurs once."""
    stmt = Insert(_REF)
    _check(cases, "insert: writes its target table", ok=ss.written_table(stmt) == "ref")
    _check(cases, "insert: returns nothing without RETURNING", ok=ss.returned_columns(stmt) == [])
    _check(
        cases, "insert: the target occurs exactly once", ok=ss.table_occurrences(stmt, "ref") == 1
    )
    _check(
        cases,
        "insert: an absent table occurs zero times",
        ok=ss.table_occurrences(stmt, "obs") == 0,
    )


def _declared_cases(cases: Cases) -> None:
    """Pin that only a DECLARED relation is reported — the CTE-has-a-name-too rule."""
    stmt = Select(_OBS.c["core_id"])
    _check(
        cases,
        "declared: an undeclared table is filtered from tables_of",
        ok=ss.tables_of(stmt, frozenset({"ref"})) == frozenset(),
    )
    _check(
        cases,
        "declared: an undeclared table is filtered from columns_of",
        ok=ss.columns_of(stmt, "obs", frozenset({"ref"})) == frozenset(),
    )


def _residue_cases(cases: Cases) -> None:
    """Pin that the two unbuildable corrections are NAMED, so a stub widening knows its job."""
    _check(
        cases,
        "residue: the unbuildable corrections are named",
        ok=len(_UNBUILDABLE) == _UNBUILDABLE_COUNT,
    )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _select_cases(cases)
    _insert_cases(cases)
    _declared_cases(cases)
    _residue_cases(cases)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"sql_statement_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
