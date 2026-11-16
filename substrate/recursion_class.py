#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The L6 pole classifier - where a python function sits on the recursion/loop/parallel triangle.

THE THIRD CUT OF THE DRAIN'S THIRD FILE (`jea/metalanguage/sql_lift.py:500-720`, W4 tick 31).
A pipeline's grade was scalar depth - the LOOP-to-PARALLEL edge only. The full grade is a
position on the triangle whose axis is the substrate's fold/unfold adjunction: a bounded walk
flattens (Family A, the Rel path), an unbounded one is a recursion (Family B) - and a recursion is
not a dead end, because the recursion-to-parallel transition (least-fixpoint saturation, `WITH
RECURSIVE`) lifts a transitive closure to a declarative CTE. This module splits Family B by what
that transition reaches, reading the pole STRUCTURALLY from the AST.

THE VERDICT IS THE FIELD THAT MEANS SOMETHING, AND IT IS FOUR-VALUED BY CONSTRUCTION:
`derived-liftable` (the walk is over a DECLARED relation and no residue rule fires),
`derived-residue` (a residue rule fires on the COMPUTATION - a hash reducer, a permutation rank),
`carrier-unmodelled` (it walks, but nothing ties it to a stored relation - WORK, not a wall: a
VALUES list, a CTE, an unnest or a temp table is a carrier the planner accepts), and `REFUTED`
(the rule's verdict stands AND a recorded probe shows it wrong, so the tool says both). Before
the third value existed, every walking function got a `sql_target` from identifier spelling and a
stray `+= 1`, and the report read as though the corpus had been analysed.

THE DECLARED RELATIONS ARE A PARAMETER. The origin populates them from `schema_decl.MD.tables`
through a `sys.path` insert and a swallowed `except Exception` that silently yields an EMPTY set -
under which every walk reads `carrier-unmodelled`, a census-green in the direction that hides
lifts. Here the caller passes the set it has, and a classifier run with no declared relations
says so in every verdict it returns rather than pretending the store is empty.

`REFUTED` IS CARRIED AS DATA, keyed by function name, so `--report` can print the refutation
beside the verdict. Deleting an entry is a claim the classifier now gets it right, which someone
must justify - the same ratchet as every other census.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

from substrate import rel_term

if TYPE_CHECKING:
    from collections.abc import Mapping

# Reducers with no SQL aggregate - a property of the computation, not of naming.
NONSQL = frozenset(
    {"log", "exp", "log2", "log10", "hexdigest", "sha1", "sha256", "md5", "sha", "digest"}
)
PERM_CALLS = frozenset({"permutations", "product", "factorial"})
ACCUM_CALLS = frozenset({"set", "frozenset"})
ACCUM_ATTRS = frozenset({"add", "update"})
GROW_ATTRS = frozenset({"extend", "append"})
LOOP_NODES = (ast.For, ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)
SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)

# Verdicts a classifier is KNOWN to get wrong, with the witness that refutes each.
REFUTED: dict[str, str] = {
    "canon_syms": (
        "sql_lift says residue (sorted_flatten rule). sppf_db.py:1041-1049 records a PROBE of a "
        "WITH RECURSIVE joining on `op = parent.op AND assoc`, with string_agg ordered by leaf vs "
        "path - verified on the sandbox as DISCRIMINATING (canon='c,d,e' vs positional='e,d,c'), "
        "so it does not pass vacuously. The rewrite is unmigrated only because the orbit tier is "
        "empty and there is nothing to verify against - a fact about the STORE'S STATE, not a "
        "licence to keep the python."
    ),
}

Fn = ast.FunctionDef | ast.AsyncFunctionDef


@dataclass(frozen=True)
class Features:
    """What the classifier reads off a function body, each a decidable structural fact."""

    name: str
    self_rec: bool
    has_worklist: bool
    set_accum: bool
    nonsql: bool
    perm: bool
    sorted_flatten: bool
    builds_text: bool
    reducers: frozenset[str] = field(default_factory=frozenset)
    walks: bool = False


class Verdict(TypedDict):
    """One classified walk - every field the origin's report reads, evidence included."""

    pole: str
    scheme: str
    transition: str
    sql_target: str
    verdict: str
    why: str
    reason: str
    reads: list[str]


def shallow_nodes(fn: ast.AST) -> list[ast.AST]:
    """Return every node in the function's OWN body, not descending into nested scopes."""
    out: list[ast.AST] = []
    stack = list(ast.iter_child_nodes(fn))
    while stack:
        n = stack.pop()
        out.append(n)
        if isinstance(n, SCOPE_NODES):
            continue
        stack.extend(ast.iter_child_nodes(n))
    return out


def _call_name(n: ast.AST) -> str | None:
    """Return the name a call invokes, for `f()` or `x.f()`."""
    return rel_term.callee(n) if isinstance(n, ast.Call) else None


def _reducers(calls: set[str | None], ns: list[ast.AST]) -> frozenset[str]:
    """Return the SQL aggregates the body's reducers correspond to."""
    out: set[str] = set()
    aug_add = any(isinstance(n, ast.AugAssign) and isinstance(n.op, ast.Add) for n in ns)
    if "sum" in calls or aug_add:
        out.add("SUM")
    if "max" in calls:
        out.add("MAX")
    if "min" in calls:
        out.add("MIN")
    if calls & {"len", "count", "Counter"}:
        out.add("COUNT")
    return frozenset(out)


def features(fn: Fn) -> Features:
    """Read the classifier's structural features off one function."""
    ns = shallow_nodes(fn)
    name = fn.name
    self_rec = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == name for n in ns
    )
    attrs = {n.attr for n in ns if isinstance(n, ast.Attribute)}
    calls = {_call_name(n) for n in ns if isinstance(n, ast.Call)}
    has_worklist = (
        any(isinstance(n, ast.While) for n in ns) and "pop" in attrs and bool(GROW_ATTRS & attrs)
    )
    has_loop_or_comp = any(isinstance(n, LOOP_NODES) for n in ns)
    return Features(
        name=name,
        self_rec=self_rec,
        has_worklist=has_worklist,
        set_accum=bool(ACCUM_CALLS & calls) or bool(ACCUM_ATTRS & attrs),
        nonsql=bool(NONSQL & calls) or bool(NONSQL & attrs),
        perm=bool(PERM_CALLS & calls),
        sorted_flatten="sorted" in calls and self_rec and bool(GROW_ATTRS & attrs),
        builds_text=any(isinstance(n, ast.JoinedStr) for n in ns) or "join" in attrs,
        reducers=_reducers(calls, ns),
        walks=has_worklist or (self_rec and has_loop_or_comp),
    )


def reads_stored(fn: ast.AST, declared: frozenset[str]) -> tuple[frozenset[str], list[str]]:
    """Return which DECLARED relations the body reads - by literal name or a literal FROM."""
    ev: list[str] = []
    for n in shallow_nodes(fn):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            tok = n.value.strip()
            if tok in declared:
                ev.append(tok)
            elif " " in tok:
                t = rel_term.table_of_sql(tok)
                if t in declared:
                    ev.append(t)
    return (frozenset(ev), ev)


@dataclass(frozen=True)
class Shape:
    """The fixed text of one verdict kind - what a rule says when it fires."""

    scheme: str
    why: str
    reason: str
    transition: str = "—"
    sql_target: str = "residue"
    verdict: str = "derived-residue"


# The four residue shapes - each fires on a property of the COMPUTATION, never of naming.
NONSQL_FOLD = Shape(
    "non-SQL numeric fold",
    "log/exp/hash reducer: no SQL aggregate exists",
    "log/exp/hash reducer has no SQL aggregate (e.g. log-sum-exp / Merkle)",
)
PERM_SEARCH = Shape(
    "permutation search / graph-iso",
    "permutation rank / canonical labeling is not relational",
    "canonical-labeling / permutation search is not relational",
)
FLATTEN_SORT = Shape(
    "variable-arity term rewrite",
    "flatten-nested + sort is a normal-form rewrite",
    "flatten-nested + sort (normal-form rewrite) is not a relational closure",
)
RENDER = Shape(
    "term-rewrite / render hylomorphism",
    "builds text/new terms per node, not a reachable set",
    "builds text/new terms per node (render/parse), not a reachable set",
)
UNMODELLED = Shape(
    scheme="closure over an UNMODELLED carrier",
    transition="model-the-carrier",
    sql_target="carrier-unmodelled",
    verdict="carrier-unmodelled",
    why=(
        "the walk is a closure; its carrier is an in-memory structure with no relational model "
        "YET - supply one (VALUES / CTE / unnest / temp) and the same walk IS a WITH RECURSIVE"
    ),
    reason="a closure whose carrier has not been given a relational model",
)


def _residue_rule(f: Features) -> Shape | None:
    """Return the shape of the first residue rule that fires, or None."""
    if f.nonsql:
        return NONSQL_FOLD
    if f.perm:
        return PERM_SEARCH
    if f.sorted_flatten:
        return FLATTEN_SORT
    if f.builds_text and not f.reducers:
        return RENDER
    return None


# The lifting transition's name — the EXACT spelling `sql_census` compares against
# (`sql_census.py:78`), so a re-spelling here would zero the census's `cte` count.
RECURSION_TO_PARALLEL = "recursion→parallel"


def _liftable(f: Features, reads: frozenset[str]) -> Shape:
    """Return the derived-liftable shape: a fold over a closure, or a reachability closure."""
    rel = ", ".join(sorted(reads))
    if f.reducers:
        agg = "/".join(sorted(f.reducers))
        return Shape(
            scheme=f"fold-over-closure ({agg})",
            transition=RECURSION_TO_PARALLEL,
            sql_target=f"WITH RECURSIVE + {agg}",
            verdict="derived-liftable",
            why=f"associative reducer over a closure on {rel}",
            reason="associative reducer over a DAG closure",
        )
    return Shape(
        scheme="reachability / transitive-closure",
        transition=RECURSION_TO_PARALLEL,
        sql_target="WITH RECURSIVE (UNION)",
        verdict="derived-liftable",
        why=f"set-accumulating walk over {rel}",
        reason="a set-accumulating walk over a child/edge adjacency",
    )


def _verdict(name: str, reads: frozenset[str], refuted: Mapping[str, str], s: Shape) -> Verdict:
    """Assemble one verdict, carrying its evidence and any recorded refutation."""
    verdict, why = s.verdict, s.why
    if name in refuted:
        verdict, why = "REFUTED", refuted[name]
    return Verdict(
        pole="recursion",
        scheme=s.scheme,
        transition=s.transition,
        sql_target=s.sql_target,
        verdict=verdict,
        why=why,
        reason=s.reason,
        reads=sorted(reads),
    )


def classify(
    fn: Fn, declared: frozenset[str], refuted: Mapping[str, str] = REFUTED
) -> Verdict | None:
    """Place a function on the triangle, or None where it is flat (the Rel-pipeline path)."""
    f = features(fn)
    if not f.walks:
        return None
    reads, _ = reads_stored(fn, declared)
    shape = _residue_rule(f)
    if shape is None:
        shape = UNMODELLED if not reads else _liftable(f, reads)
    return _verdict(f.name, reads, refuted, shape)
