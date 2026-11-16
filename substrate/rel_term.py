#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""RelTerm - a relational-op pipeline - and the pure readers that lower python to it.

THE SECOND CUT OF THE DRAIN'S THIRD FILE (`jea/metalanguage/sql_lift.py:44-70, 77-195, 329-353`,
W4 tick 30). The graded relational carrier's element is a linear chain of Rel HEADS over a Scan
leaf; its grade is the chain's length, and the grade IS the liftability boundary - a bounded-grade
pipeline flattens to a relational normal form and an unbounded one (a recursive walk) never does.
`rel_of_expr` is the GradedHomOver from python expressions into that carrier: it recognises the
relational shapes (`sorted`, `Counter`, `set`, `len`, a filtered comprehension, a slice) and STOPS -
returns None - at a non-relational op, which is the kept residue.

INTERNING IS A PARAMETER, NOT AN IMPORT. The origin's `intern_into` reaches `jea_pyalg.Intern`
and `IR` through a `sys.path` insert (`sql_lift.py:29`); a clean module cannot. So the lowering is
expressed against a callable `(op, lit, children) -> id` that the caller supplies from whichever
interner it holds - the same move `sql_circuit` made for the circuit folds, minus the transcription,
because here nothing needs copying: the SHAPE of the lowering (innermost Scan first, each head
wrapping the sub-pipeline as one child) is the whole of what this module owns.

THE CORPUS SHAPE `licensed_lifts` READS IS A PARAMETER TOO: two mappings from interned id to
`RelTerm`, one per side, which is exactly what the origin's `build()` returns. The roofline it
ranks by is `sql_circuit.roofline` over `(heads, breadth)` - cut 1 - so the two cuts compose
without the origin in between.

THE FOUR RECORDED READINGS ARE KEPT AS RULES: a non-Limit subscript PASSES THROUGH to its value;
`dict(rows)` is a lookup-table load and passes through; a map-only comprehension passes its source
through while a filtered one adds `Filter`; and a bare `Name` is a bounded leaf (`Scan` over that
variable), never a stop. Each is a case in the suite, because each is where a reader that
"looks fine" silently drops a lift or manufactures one.
"""

from __future__ import annotations

import ast
import re
from typing import TYPE_CHECKING

from substrate import sql_circuit

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

# The curated relational head-set - each a generator of the graded carrier.
REL_HEADS = ("Scan", "Filter", "Distinct", "GroupBy", "Agg", "OrderBy", "Limit", "Join")
# SQL canonical evaluation order - the head SEQUENCE coherence matches as a sub-pipeline.
SQL_ORDER = {
    h: i
    for i, h in enumerate(
        ("Scan", "Join", "Filter", "GroupBy", "Agg", "Distinct", "OrderBy", "Limit")
    )
}
_UNORDERED = 99
# Calls that read rows from a store or a mapping - the Scan leaf of a python pipeline.
SCAN_CALLS = frozenset({"run", "execute", "fetchall", "fetchone", "items", "keys", "values"})
# Builtins that lower to a head prefix over their first argument; the leaf used when it has none.
_PREFIX_CALLS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "sorted": (("OrderBy",), ("Scan",)),
    "Counter": (("GroupBy", "Agg"), ()),
    "set": (("Distinct",), ("Scan",)),
    "frozenset": (("Distinct",), ("Scan",)),
}
_AGG_CALLS = frozenset({"len", "sum", "max", "min"})
# How deep `rel_of_expr` follows a nested expression before giving up - a bound, not a limit met.
MAX_DEPTH = 40
# A COMPOSED pipeline (at least two relational heads) is the real eager-to-fused win.
MIN_LIFT_HEADS = 2

Site = tuple[str, int, str]
Comp = ast.SetComp | ast.ListComp | ast.GeneratorExp
Lift = tuple["RelTerm", list["RelTerm"]]


def _sql_rank(head: str) -> int:
    """Return a head's position in SQL evaluation order, unknown heads last."""
    return SQL_ORDER.get(head, _UNORDERED)


class RelTerm:
    """A linear chain of Rel heads (outer to inner) over a Scan leaf at `source`."""

    __slots__ = ("heads", "sites", "source")

    def __init__(self, heads: Iterable[str], source: str = "*") -> None:
        """Bind the head chain and its source; emission sites start empty."""
        self.heads: tuple[str, ...] = tuple(heads)
        self.source = source
        self.sites: list[Site] = []

    @property
    def grade(self) -> int:
        """Return the composition depth - the GradedProductOver grade."""
        return len(self.heads)

    def key(self) -> tuple[tuple[str, ...], str]:
        """Return the identity two pipelines share when they are the same lift."""
        return (self.heads, self.source)

    def intern_into(self, intern: Callable[[str, str | None, tuple[int, ...]], int]) -> int:
        """Lower into a carrier: innermost Scan leaf first, each head wrapping the sub-pipeline."""
        cur = intern("Scan", self.source, ())
        for h in reversed(self.heads):
            cur = intern(h, None, (cur,))
        return cur

    def canon_seq(self) -> tuple[str, ...]:
        """Return the heads in SQL evaluation order - what sub-pipeline coherence matches."""
        return tuple(sorted(self.heads, key=_sql_rank))


def callee(node: ast.Call) -> str | None:
    """Return the called name for `f(...)` or `x.f(...)`, else None."""
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def has_if(comp: ast.expr) -> bool:
    """Return whether a comprehension carries an `if` clause on any generator."""
    if not isinstance(comp, Comp):
        return False
    return any(g.ifs for g in comp.generators)


def table_of_sql(s: str) -> str:
    """Return the first FROM-table of a raw SQL string, else '*'."""
    m = re.search(r"\bFROM\s+([A-Za-z_][\w]*)", s, re.IGNORECASE)
    return str(m.group(1)) if m else "*"


def _source_of_call(node: ast.Call) -> str:
    """Return the relation a store-reading call scans: the builder name, the FROM table, or '*'."""
    fn = callee(node)
    if fn in ("run", "execute"):
        for a in node.args:
            if isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute):
                return a.func.attr
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                return table_of_sql(a.value)
    if fn in SCAN_CALLS and isinstance(node.func, ast.Attribute):
        return source_of(node.func.value)
    return "*"


def source_of(node: ast.expr | None) -> str:
    """Return the scanned-relation token (a builder name or table) where cheap, else '*'."""
    if isinstance(node, ast.Call):
        return _source_of_call(node)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.GeneratorExp):
        return source_of(node.generators[0].iter) if node.generators else "*"
    return "*"


def _wrap(
    head: tuple[str, ...], arg0: ast.expr | None, depth: int, leaf: tuple[str, ...]
) -> RelTerm:
    """Prefix `head` onto the pipeline of `arg0`, or onto `leaf` over its source."""
    inner = rel_of_expr(arg0, depth + 1)
    if inner is not None:
        return RelTerm((*head, *inner.heads), inner.source)
    return RelTerm((*head, *leaf), source_of(arg0))


def _rel_of_call(node: ast.Call, depth: int) -> RelTerm | None:
    """Lower one call: a prefix builtin, an aggregate, a Scan call, a dict load, or a stop."""
    fn = callee(node)
    arg0 = node.args[0] if node.args else None
    if fn in _PREFIX_CALLS:
        head, leaf = _PREFIX_CALLS[fn]
        return _wrap(head, arg0, depth, leaf)
    if fn in _AGG_CALLS:
        return RelTerm(("Agg",), source_of(arg0))
    if fn in SCAN_CALLS:
        return RelTerm(("Scan",), source_of(node))
    if fn == "dict":
        return rel_of_expr(arg0, depth + 1)
    return None


def _rel_of_comp(node: Comp, depth: int) -> RelTerm | None:
    """Lower a comprehension: set is Distinct, an `if` adds Filter, map-only passes through."""
    src = rel_of_expr(node.generators[0].iter, depth + 1) if node.generators else None
    heads = src.heads if src else ("Scan",)
    source = src.source if src else "*"
    if isinstance(node, ast.SetComp):
        filt: tuple[str, ...] = ("Filter",) if has_if(node) else ()
        return RelTerm(("Distinct", *filt, *heads), source)
    if has_if(node):
        return RelTerm(("Filter", *heads), source)
    return src


def _rel_of_subscript(node: ast.Subscript, depth: int) -> RelTerm | None:
    """Lower a subscript: a bounded slice is Limit; any other subscript passes through."""
    sl = node.slice
    if isinstance(sl, ast.Slice) and sl.upper is not None:
        inner = rel_of_expr(node.value, depth + 1)
        if inner is not None:
            return RelTerm(("Limit", *inner.heads), inner.source)
    return rel_of_expr(node.value, depth + 1)


def rel_of_expr(node: ast.expr | None, depth: int = 0) -> RelTerm | None:
    """Lower a python expression to a RelTerm, or None where it is not a bounded pipeline."""
    if node is None or depth > MAX_DEPTH:
        return None
    if isinstance(node, ast.Subscript):
        return _rel_of_subscript(node, depth)
    if isinstance(node, ast.Call):
        return _rel_of_call(node, depth)
    if isinstance(node, Comp):
        return _rel_of_comp(node, depth)
    if isinstance(node, ast.Attribute):
        return rel_of_expr(node.value, depth + 1)
    return RelTerm(("Scan",), node.id) if isinstance(node, ast.Name) else None


def interesting(rt: RelTerm) -> bool:
    """Return whether a term has at least one non-Scan head - worth reporting."""
    return any(h != "Scan" for h in rt.heads)


def is_suffix(short: tuple[str, ...], long: tuple[str, ...]) -> bool:
    """Return whether `short` is a PROPER suffix of `long`."""
    return len(short) < len(long) and long[len(long) - len(short) :] == short


def maximal(terms: Iterable[RelTerm]) -> list[RelTerm]:
    """Dedup identical terms; drop any whose heads are a proper suffix of another at its source."""
    uniq: dict[tuple[tuple[str, ...], str], RelTerm] = {}
    for t in terms:
        uniq[t.key()] = t
    pool = list(uniq.values())
    return [
        t
        for t in pool
        if not any(
            o is not t and o.source == t.source and is_suffix(t.heads, o.heads) for o in pool
        )
    ]


def terms_of_function(fn_node: ast.AST) -> list[RelTerm]:
    """Return every maximal, interesting Rel term in a function body - the GradedHomOver over it."""
    out: list[RelTerm] = []
    for node in ast.walk(fn_node):
        if isinstance(node, (ast.Subscript, ast.Call, Comp)):
            rt = rel_of_expr(node)
            if rt is not None and interesting(rt):
                out.append(rt)
    return maximal(out)


def is_contiguous(short: tuple[str, ...], long: tuple[str, ...]) -> bool:
    """Return whether `short` is a contiguous subsequence of `long` (the empty one always is)."""
    if not short or len(short) > len(long):
        return len(short) == 0
    return any(long[i : i + len(short)] == short for i in range(len(long) - len(short) + 1))


def _lift_rank(lift: Lift) -> float:
    """Return the sort key of a lift: negated roofline score, so the strongest lift sorts first."""
    rt = lift[0]
    return -sql_circuit.roofline(rt.heads, len(rt.sites))["score"]


def licensed_lifts(py: Mapping[int, RelTerm], sql: Mapping[int, RelTerm]) -> list[Lift]:
    """Return every composed python pipeline whose heads embed contiguously in an SQL builder's."""
    sql_seqs = [(tuple(h for h in rt.canon_seq() if h != "Scan"), rt) for rt in sql.values()]
    out: list[Lift] = []
    for rt in py.values():
        pseq = tuple(h for h in rt.canon_seq() if h != "Scan")
        if len(pseq) < MIN_LIFT_HEADS:
            continue
        matches = [srt for sseq, srt in sql_seqs if is_contiguous(pseq, sseq)]
        if matches:
            out.append((rt, matches))
    out.sort(key=_lift_rank)
    return out
