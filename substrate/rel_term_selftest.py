#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `rel_term` - the four recorded readings, the folds, and a differential by path.

THE DIFFERENTIAL IS THE LOAD-BEARING HALF. Every other case asserts what I believe the lowering
SHOULD produce; the differential asserts it is the ORIGIN's, expression for expression, over a
fixture that exercises every arm of `rel_of_expr` - which is the claim a replacement actually
owes. The origin is loaded BY PATH (`sql_lift.py`), which drags its `sys.path` inserts along;
that is the origin's business and the reason this module exists, so the loader tolerates it and
the cases are SKIPPED, not failed, if the origin will not import on this host.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import rel_term as rt

_ORIGIN = Path(__file__).resolve().parent.parent / "jea" / "metalanguage" / "sql_lift.py"

# One expression per arm of the lowering; the differential runs the origin over the same list.
_EXPRS = [
    "sorted(rows)",
    "sorted(rows)[:10]",
    "rows[0]",
    "Counter(r.x for r in rows)",
    "set(QB.run(con, QB.q_edges_all()))",
    "len(rows)",
    "dict(rows)",
    "{r.a for r in rows if r.b}",
    "[r.a for r in rows]",
    "[r.a for r in rows if r.b]",
    "(r.a for r in rows)",
    "rows.items()",
    "con.execute('SELECT x FROM obs WHERE y')",
    "helper(rows)",
    "sorted(set(rows))[:5]",
    "frozenset(x.y)",
    "max(sorted(rows))",
    "foo.bar",
]

Cases = list[tuple[str, bool]]


class _OriginTerm(Protocol):
    @property
    def heads(self) -> tuple[str, ...]: ...
    @property
    def source(self) -> str: ...


class _Origin(Protocol):
    def rel_of_expr(self, node: ast.expr, depth: int = 0) -> _OriginTerm | None: ...


def _origin() -> _Origin | None:
    """Load `sql_lift.py` by PATH, or None when it is gone or will not import here."""
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_sql_lift_origin", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImportError:
        return None
    return cast("_Origin", module)


def _expr(src: str) -> ast.expr:
    """Parse one expression."""
    return ast.parse(src, mode="eval").body


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _lower(src: str) -> tuple[tuple[str, ...], str] | None:
    """Lower an expression to its (heads, source), or None."""
    t = rt.rel_of_expr(_expr(src))
    return None if t is None else (t.heads, t.source)


def _reading_cases(cases: Cases) -> None:
    """Pin the four recorded readings and the recognised shapes."""
    _check(
        cases,
        "sorted over a name is OrderBy over Scan",
        ok=_lower("sorted(rows)") == (("OrderBy", "Scan"), "rows"),
    )
    _check(
        cases,
        "a bounded slice prefixes Limit",
        ok=_lower("sorted(rows)[:10]") == (("Limit", "OrderBy", "Scan"), "rows"),
    )
    _check(
        cases,
        "a non-Limit subscript passes through to its value",
        ok=_lower("rows[0]") == (("Scan",), "rows"),
    )
    _check(
        cases,
        "dict(rows) is a lookup-table load and passes through",
        ok=_lower("dict(rows)") == (("Scan",), "rows"),
    )
    _check(
        cases,
        "a map-only comprehension passes its source through",
        ok=_lower("[r.a for r in rows]") == (("Scan",), "rows"),
    )
    _check(
        cases,
        "a filtered comprehension adds Filter",
        ok=_lower("[r.a for r in rows if r.b]") == (("Filter", "Scan"), "rows"),
    )
    _check(
        cases,
        "a filtered set comprehension is Distinct then Filter",
        ok=_lower("{r.a for r in rows if r.b}") == (("Distinct", "Filter", "Scan"), "rows"),
    )
    _check(
        cases,
        "Counter is GroupBy then Agg over the generator's source",
        ok=_lower("Counter(r.x for r in rows)") == (("GroupBy", "Agg", "Scan"), "rows"),
    )
    _check(cases, "a non-relational call is a bounded STOP", ok=_lower("helper(rows)") is None)
    _check(
        cases, "a bare Name is a Scan leaf, never a stop", ok=_lower("rows") == (("Scan",), "rows")
    )
    _check(
        cases,
        "QB.run recovers the builder name as the source",
        ok=_lower("set(QB.run(con, QB.q_edges_all()))") == (("Distinct", "Scan"), "q_edges_all"),
    )
    _check(
        cases,
        "a raw SQL string recovers its FROM table",
        ok=_lower("con.execute('SELECT x FROM obs WHERE y')") == (("Scan",), "obs"),
    )


def _fold_cases(cases: Cases) -> None:
    """Pin canon_seq, maximal, is_contiguous and the interning shape."""
    t = rt.RelTerm(("Limit", "OrderBy", "Filter", "Scan"), "rows")
    _check(
        cases,
        "canon_seq is SQL evaluation order",
        ok=t.canon_seq() == ("Scan", "Filter", "OrderBy", "Limit"),
    )
    _check(cases, "grade is the head count", ok=t.grade == 4)  # noqa: PLR2004 - the four heads above
    short = rt.RelTerm(("Filter", "Scan"), "rows")
    other = rt.RelTerm(("Filter", "Scan"), "other")
    kept = rt.maximal([t, short, other, rt.RelTerm(("Filter", "Scan"), "rows")])
    _check(
        cases,
        "maximal drops a proper suffix at the same source and dedups",
        ok=[k.key() for k in kept] == [t.key(), other.key()],
    )
    _check(
        cases,
        "maximal keeps a non-suffix at the same source (Filter is not a suffix here)",
        ok=len(rt.maximal([t, rt.RelTerm(("OrderBy", "Scan"), "rows")])) == 2,
    )  # noqa: PLR2004 - both kept
    _check(
        cases,
        "is_contiguous: an inner run matches, the empty run always does",
        ok=rt.is_contiguous(("b", "c"), ("a", "b", "c", "d")) and rt.is_contiguous((), ()),
    )
    _check(
        cases,
        "is_contiguous: a gapped run does not match",
        ok=not rt.is_contiguous(("a", "c"), ("a", "b", "c")),
    )
    log: list[tuple[str, str | None, tuple[int, ...]]] = []

    def intern(op: str, lit: str | None, children: tuple[int, ...]) -> int:
        log.append((op, lit, children))
        return len(log)

    root = rt.RelTerm(("OrderBy", "Scan"), "rows").intern_into(intern)
    _check(
        cases,
        "intern_into lowers the Scan leaf first and wraps outward",
        ok=root == 3
        and log
        == [
            ("Scan", "rows", ()),
            ("Scan", None, (1,)),  # noqa: PLR2004 - three interned nodes
            ("OrderBy", None, (2,)),
        ],
    )


def _lift_cases(cases: Cases) -> None:
    """Pin licensed_lifts over a fixture corpus: composed pipelines embed, singletons do not."""
    py = {
        1: rt.RelTerm(("Limit", "OrderBy", "Scan"), "rows"),
        2: rt.RelTerm(("OrderBy", "Scan"), "rows"),
        3: rt.RelTerm(("GroupBy", "Agg", "Scan"), "rows"),
    }
    sql = {
        10: rt.RelTerm(("Limit", "OrderBy", "Filter", "Scan"), "q_top"),
        11: rt.RelTerm(("Distinct", "Scan"), "q_names"),
    }
    lifts = rt.licensed_lifts(py, sql)
    _check(
        cases,
        "a composed pipeline embedding contiguously is licensed",
        ok=[t.key() for t, _ in lifts] == [py[1].key()],
    )
    _check(cases, "the licence names the SQL builder it embeds in", ok=lifts[0][1][0] is sql[10])
    _check(cases, "a single-head pipeline is not a lift", ok=all(t is not py[2] for t, _ in lifts))
    _check(
        cases,
        "a composed pipeline with no SQL host is not licensed",
        ok=all(t is not py[3] for t, _ in lifts),
    )


def _differential_cases(cases: Cases) -> None:
    """Assert rel_of_expr agrees with the origin over every fixture expression, or skip."""
    o = _origin()
    if o is None:
        _check(cases, "differential: origin unavailable, skipped", ok=True)
        return
    for src in _EXPRS:
        ours = _lower(src)
        theirs = o.rel_of_expr(_expr(src))
        want = None if theirs is None else (tuple(theirs.heads), theirs.source)
        _check(cases, f"differential: {src}", ok=ours == want)


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _reading_cases(cases)
    _fold_cases(cases)
    _lift_cases(cases)
    _differential_cases(cases)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"rel_term_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
