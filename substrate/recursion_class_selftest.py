#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `recursion_class` - one fixture per pole, the control, and the REFUTED spec.

THE ORIGIN'S SUITE IS RED ON THIS SURFACE (30/33 at tick 29) and the three reds are about the
CORPUS, not the rules: `canon_syms` in `sppf_db.py` no longer classifies as a walk, so
`R.get("canon_syms")` is empty and the three assertions about it fail. This suite therefore pins
what those assertions SPECIFY - a flatten+sort self-recursion named in `REFUTED` reads `residue`
by the rule AND `REFUTED` as its verdict AND a `why` naming the discriminating probe - on a fixture
whose shape cannot drift with the corpus. The differential runs the origin's `classify_recursion`
by path over the same fixtures with its `STORED_RELATIONS` pinned to this suite's declared set,
and skips if the origin will not import here.

THE CONTROL IS LOAD-BEARING. A classifier returning `carrier-unmodelled` for everything passes
every unmodelled case; a walk over a DECLARED relation must still come back `derived-liftable`
with the relation named as its evidence.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import recursion_class as rc

_ORIGIN = Path(__file__).resolve().parent.parent / "jea" / "metalanguage" / "sql_lift.py"
_DECLARED = frozenset({"node_child", "obs"})

# One function per pole. Each is parsed once; names are what the classifier keys on.
_FIXTURE = """
def reach(con, root):
    seen = set()
    todo = [root]
    while todo:
        n = todo.pop()
        seen.add(n)
        todo.extend(QB.run(con, "node_child", n))
    return seen

def total(con, n):
    acc = 0
    for c in QB.run(con, "SELECT child FROM node_child WHERE parent = ?", n):
        acc += total(con, c)
    return acc

def support(node):
    out = set()
    for c in node.children:
        out.update(support(c))
    return out

def lsz(t):
    xs = [lsz(c) for c in t.kids]
    m = max(xs)
    return m + log(sum(exp(x - m) for x in xs))

def canon_syms(t):
    out = []
    for c in t.kids:
        out.extend(canon_syms(c))
    return sorted(out)

def render(t):
    return ",".join(render(c) for c in t.kids)

def flat(rows):
    return sorted(set(rows))

def linear(n):
    return 1 if n == 0 else n * linear(n - 1)
"""

Cases = list[tuple[str, bool]]


class _OriginVerdict(Protocol):
    def get(self, key: str, default: object = None) -> object: ...


class _Origin(Protocol):
    STORED_RELATIONS: frozenset[str]

    def classify_recursion(self, fn: ast.AST) -> _OriginVerdict | None: ...


def _origin() -> _Origin | None:
    """Load `sql_lift.py` by PATH with its declared set pinned, or None if it will not import."""
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_sql_lift_origin_rc", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImportError:
        return None
    o = cast("_Origin", module)
    o.STORED_RELATIONS = _DECLARED
    return o


def _fns() -> dict[str, rc.Fn]:
    """Parse the fixture into its functions by name."""
    tree = ast.parse(_FIXTURE)
    return {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _pole_cases(cases: Cases, fns: dict[str, rc.Fn]) -> None:
    """Pin one verdict per pole, and that a flat function is None."""
    v = rc.classify(fns["reach"], _DECLARED)
    _check(
        cases,
        "control: a worklist over a DECLARED relation is derived-liftable (UNION)",
        ok=v is not None
        and v["verdict"] == "derived-liftable"
        and v["sql_target"] == "WITH RECURSIVE (UNION)",
    )
    _check(
        cases,
        "control: the verdict names the relation that decided it",
        ok=v is not None and v["reads"] == ["node_child"],
    )
    v = rc.classify(fns["total"], _DECLARED)
    _check(
        cases,
        "a reducer over a closure on a literal FROM is a fold (SUM)",
        ok=v is not None
        and v["sql_target"] == "WITH RECURSIVE + SUM"
        and v["reads"] == ["node_child"],
    )
    v = rc.classify(fns["support"], _DECLARED)
    _check(
        cases,
        "a walk over an in-memory carrier is carrier-unmodelled, not residue",
        ok=v is not None and v["verdict"] == "carrier-unmodelled" and v["reads"] == [],
    )
    v = rc.classify(fns["lsz"], _DECLARED)
    _check(
        cases,
        "log-sum-exp is derived-residue by the non-SQL rule",
        ok=v is not None
        and v["verdict"] == "derived-residue"
        and v["scheme"] == rc.NONSQL_FOLD.scheme,
    )
    v = rc.classify(fns["render"], _DECLARED)
    _check(
        cases,
        "a text-building hylomorphism is residue (render rule)",
        ok=v is not None and v["scheme"] == rc.RENDER.scheme,
    )
    _check(
        cases,
        "a flat set-op pipeline is not a recursion (None)",
        ok=rc.classify(fns["flat"], _DECLARED) is None,
    )
    _check(
        cases,
        "linear recursion without a loop is not a walk (None)",
        ok=rc.classify(fns["linear"], _DECLARED) is None,
    )


def _refuted_cases(cases: Cases, fns: dict[str, rc.Fn]) -> None:
    """Pin the origin's three canon_syms assertions as a spec over a stable fixture."""
    v = rc.classify(fns["canon_syms"], _DECLARED)
    _check(
        cases,
        "canon_syms (flatten+sort) is residue BY THE RULE",
        ok=v is not None and v["sql_target"] == "residue",
    )
    _check(
        cases,
        "...and is flagged REFUTED, with the probe as its witness",
        ok=v is not None and v["verdict"] == "REFUTED",
    )
    _check(
        cases,
        "...whose refutation names the discriminating probe",
        ok=v is not None and ("discriminating" in v["why"].lower() or "canon=" in v["why"]),
    )
    plain = rc.classify(fns["canon_syms"], _DECLARED, refuted={})
    _check(
        cases,
        "without the refutation record the rule's own verdict stands",
        ok=plain is not None and plain["verdict"] == "derived-residue",
    )


def _declared_cases(cases: Cases, fns: dict[str, rc.Fn]) -> None:
    """Pin that the declared set is what decides liftable-vs-unmodelled."""
    v = rc.classify(fns["reach"], frozenset())
    _check(
        cases,
        "with NO declared relations the control reads carrier-unmodelled",
        ok=v is not None and v["verdict"] == "carrier-unmodelled",
    )
    reads, ev = rc.reads_stored(fns["total"], _DECLARED)
    _check(
        cases,
        "reads_stored recovers a FROM table from a literal SELECT",
        ok=reads == {"node_child"} and ev == ["node_child"],
    )


def _differential_cases(cases: Cases, fns: dict[str, rc.Fn]) -> None:
    """Assert classify agrees with the origin on every fixture, or skip."""
    o = _origin()
    if o is None:
        _check(cases, "differential: origin unavailable, skipped", ok=True)
        return
    for name, fn in fns.items():
        ours = rc.classify(fn, _DECLARED)
        theirs = o.classify_recursion(fn)
        if ours is None or theirs is None:
            _check(
                cases,
                f"differential {name}: both flat or both walks",
                ok=(ours is None) == (theirs is None),
            )
            continue
        # ⚑ `transition` IS COMPARED because `sql_census` keys its `cte` count on that exact
        # string — a differential that skipped it passed while an ASCII re-spelling would have
        # zeroed the census (caught at the swap, tick 36).
        same = (
            ours["verdict"] == theirs.get("verdict")
            and ours["sql_target"] == theirs.get("sql_target")
            and ours["scheme"] == theirs.get("scheme")
            and ours["transition"] == theirs.get("transition")
            and ours["reads"] == theirs.get("reads")
        )
        _check(cases, f"differential {name}: verdict/target/scheme/transition/reads agree", ok=same)


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    fns = _fns()
    _pole_cases(cases, fns)
    _refuted_cases(cases, fns)
    _declared_cases(cases, fns)
    _differential_cases(cases, fns)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"recursion_class_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
