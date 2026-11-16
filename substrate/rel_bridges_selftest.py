#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `rel_bridges` - clause-state lowering, the numpy chain, coherence, and a differential.

EVERY SQL FIXTURE IS A STATEMENT OBJECT built through the stub's declared generative surface
over an in-memory `MetaData` (the `sql_statement_selftest` shape). The aggregate arm uses a
`Function("count", ...)` because the stub declines `func`. The differential loads `sql_lift.py`
by path and asserts `rel_of_select` agrees head-for-head and source-for-source over every
fixture, and is SKIPPED (not failed) if the origin will not import here.

THE RECURSIVE-CTE ARM IS NAMED AND NOT PINNED: the stub declines `Select.cte()`, so a fixture
cannot build a `WITH RECURSIVE` under the gate. The reader carries the rule (`isinstance(f, CTE)
and f.recursive`), and a `cte` widening would let this suite assert it - recorded as residue,
the same shape `sql_statement_selftest` records for its CTE arm.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from sqlalchemy import Column, MetaData, Table
from sqlalchemy.sql.functions import Function
from sqlalchemy.sql.selectable import Select
from sqlalchemy.sql.type_api import TypeEngine

from substrate import rel_bridges as rb

_ORIGIN = Path(__file__).resolve().parent.parent / "jea" / "metalanguage" / "sql_lift.py"


class _AnyInt(TypeEngine[object]):
    """An integer column type at the top type, so the fixture table type-checks."""

    __visit_name__ = "integer"


_MD = MetaData()
_OBS = Table("obs", _MD, Column("core_id", _AnyInt()), Column("local_id", _AnyInt()))
_LIMIT = 10

Cases = list[tuple[str, bool]]


class _OriginTerm(Protocol):
    @property
    def heads(self) -> tuple[str, ...]: ...
    @property
    def source(self) -> str: ...


class _Origin(Protocol):
    def rel_of_select(self, stmt: Select) -> _OriginTerm: ...
    def rel_of_np(self, np_heads: list[str], source: str = "*") -> _OriginTerm: ...


def _origin() -> _Origin | None:
    """Load `sql_lift.py` by PATH, or None when it is gone or will not import here."""
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_sql_lift_origin_rb", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImportError:
        return None
    return cast("_Origin", module)


def _fixtures() -> dict[str, Select]:
    """Build one Select per clause shape."""
    core = _OBS.c["core_id"]
    return {
        "plain": Select(core),
        "filtered": Select(core).where(core.is_distinct_from(None)),
        "ordered_limited": Select(core).order_by(core).limit(_LIMIT),
        "grouped_counted": Select(core, Function("count", core)).group_by(core),
        "distinct": Select(core).distinct(),
        "everything": (
            Select(core, Function("max", core))
            .where(core.is_distinct_from(None))
            .group_by(core)
            .distinct()
            .order_by(core)
            .limit(_LIMIT)
        ),
    }


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _select_cases(cases: Cases, fx: dict[str, Select]) -> None:
    """Pin the head-set each clause shape lowers to, and the source."""
    lower = {k: rb.rel_of_select(v) for k, v in fx.items()}
    _check(
        cases,
        "a plain select is Scan over its table",
        ok=lower["plain"].heads == ("Scan",) and lower["plain"].source == "obs",
    )
    _check(cases, "a WHERE adds Filter", ok=lower["filtered"].heads == ("Scan", "Filter"))
    _check(
        cases,
        "ORDER BY then LIMIT, in SQL order",
        ok=lower["ordered_limited"].heads == ("Scan", "OrderBy", "Limit"),
    )
    _check(
        cases,
        "GROUP BY with a count is GroupBy then Agg",
        ok=lower["grouped_counted"].heads == ("Scan", "GroupBy", "Agg"),
    )
    _check(cases, "DISTINCT adds Distinct", ok=lower["distinct"].heads == ("Scan", "Distinct"))
    _check(
        cases,
        "every clause lands in SQL evaluation order",
        ok=lower["everything"].heads
        == ("Scan", "Filter", "GroupBy", "Agg", "Distinct", "OrderBy", "Limit"),
    )
    _check(
        cases,
        "has_aggregate is false without a named aggregate",
        ok=not rb.has_aggregate(fx["plain"]),
    )
    _check(cases, "select_source is '*' over no named FROM", ok=rb.select_source([]) == "*")


def _np_cases(cases: Cases, fx: dict[str, Select]) -> None:
    """Pin the numpy chain and the coherence predicate over a caller-supplied interner."""
    _check(
        cases,
        "np_group_count emits GroupBy then Agg",
        ok=rb.rel_of_np(["np_scan", "np_group_count"]).heads == ("Scan", "GroupBy", "Agg"),
    )
    _check(
        cases,
        "np_closure is the Closure head",
        ok=rb.rel_of_np(["np_closure"], "edges").heads == ("Closure",),
    )
    table: dict[tuple[str, str | None, tuple[int, ...]], int] = {}

    def intern(op: str, lit: str | None, children: tuple[int, ...]) -> int:
        return table.setdefault((op, lit, children), len(table) + 1)

    _check(
        cases,
        "a numpy order+limit chain is coherent with ORDER BY LIMIT",
        ok=rb.np_sql_coherent(intern, ["np_scan", "np_order", "np_limit"], fx["ordered_limited"]),
    )
    _check(
        cases,
        "the same chain is NOT coherent with a plain select",
        ok=not rb.np_sql_coherent(intern, ["np_scan", "np_order", "np_limit"], fx["plain"]),
    )
    _check(
        cases,
        "coherence is braiding-robust: the chain order does not matter",
        ok=rb.np_sql_coherent(intern, ["np_limit", "np_order", "np_scan"], fx["ordered_limited"]),
    )
    _check(
        cases,
        "the coherence predicate is a parameter",
        ok=not rb.np_sql_coherent(
            intern,
            ["np_scan", "np_order", "np_limit"],
            fx["ordered_limited"],
            coherent=lambda _p, _s: False,
        ),
    )


def _differential_cases(cases: Cases, fx: dict[str, Select]) -> None:
    """Assert rel_of_select and rel_of_np agree with the origin, or skip."""
    o = _origin()
    if o is None:
        _check(cases, "differential: origin unavailable, skipped", ok=True)
        return
    for name, stmt in fx.items():
        ours, theirs = rb.rel_of_select(stmt), o.rel_of_select(stmt)
        _check(
            cases,
            f"differential rel_of_select {name}",
            ok=ours.heads == tuple(theirs.heads) and ours.source == theirs.source,
        )
    chain = ["np_scan", "np_filter", "np_group_count", "np_limit"]
    _check(
        cases,
        "differential rel_of_np",
        ok=rb.rel_of_np(chain).heads == tuple(o.rel_of_np(chain).heads),
    )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    fx = _fixtures()
    _select_cases(cases, fx)
    _np_cases(cases, fx)
    _differential_cases(cases, fx)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"rel_bridges_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
