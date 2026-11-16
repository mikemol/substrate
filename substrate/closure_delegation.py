#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report whether the claim-graph walk delegates to the engine's closure and keeps both halves.

⚑⚑⚑ THE HALF WE LOSE IS THE FINDING, AND IT IS A REAL ASYMMETRY. The engine's `rests_closure`
returns `(reachable, dangling)`: reachability, and the grounding edges pointing at keys no bib
defines. A caller that takes the first and discards the second has a walk that agrees with the
engine about what EXISTS while being blind to what is BROKEN — and a dangling grounding edge is
exactly what the engine's own gate refuses. **Calling it and discarding half is the same blind
spot with an import in front of it.**

⚑⚑ THE ORIGIN ASKED THIS OF SOURCE TEXT, AND THAT IS THE CLASS THIS ARC KEEPS RETIRING. Its
predicate was `"rests_closure" not in src` over one hardcoded file, then `"dangling" not in src` —
a substring search that cannot tell a call from a mention in a comment, cannot see a call made
through an alias, and answers about one file. The same shape produced two recorded false
populations in the T25 family, each caught only by a reader noticing an implausible number.

⚑ SO THIS READS THE RELATION. A call site is an `ast.Call` whose function resolves to the name;
consumption of the second half is an assignment that unpacks two targets. Both are decidable from
the syntax tree, and neither is confused by prose.

⚑ MEASURED BEFORE WRITING: `rests_closure` has ONE caller in this tree, and it is NOT the gate the
origin interrogated — so the origin's verdict was right by accident, through an instrument that
could not distinguish *never called* from *called under another name*.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path

# The engine function whose second return is the thing at issue.
CLOSURE = "rests_closure"

# Where the claim-graph walk lives — the module this item is about.
WALKER = "scripts/worklist_gate.py"

# ⚑ THE CLOSURE RETURNS A PAIR, AND THE ARITY IS THE TEST. Named so the predicate cites the
# engine's contract rather than a bare literal a reader must infer.
RETURNS = 2


@dataclass(frozen=True, slots=True)
class Call:
    """One call to the closure, and what the caller did with its result."""

    path: str
    line: int
    consumes_both: bool

    @property
    def route(self) -> str:
        """Return the repair this call site needs, or an empty string when it needs none."""
        return (
            ""
            if self.consumes_both
            else "unpack both returns — a discarded `dangling` is a broken edge nobody sees"
        )


def _is_closure_call(node: ast.expr | None, name: str) -> bool:
    """Report whether an expression is a call to `name`, bare or by attribute.

    ⚑ BOTH SPELLINGS, because `from paperkit.bib import rests_closure` and `bib.rests_closure`
    are the same call — a reader seeing only one reports a false zero for the other.
    """
    if not isinstance(node, ast.Call):
        return False
    if isinstance(node.func, ast.Name):
        return node.func.id == name
    return isinstance(node.func, ast.Attribute) and node.func.attr == name


def _unpacks_two(node: ast.Assign) -> bool:
    """Report whether an assignment unpacks the closure's pair.

    ⚑ THE UNPACKING IS THE CONSUMPTION TEST. `a, b = f()` binds both halves; `a = f()` binds the
    pair and then almost always indexes `[0]`, which is the discard this item exists to find.
    """
    return any(
        isinstance(t, (ast.Tuple, ast.List)) and len(t.elts) == RETURNS for t in node.targets
    )


def calls(path: Path, label: str, name: str = CLOSURE) -> tuple[Call, ...]:
    """Return every call to `name` in one file, with whether both returns are consumed.

    ⚑ AN ASSIGNMENT IS MATCHED AS A STATEMENT, NEVER AS A BARE CALL. Walking the tree and asking
    each `ast.Call` whether some assignment shares its line reads the same site twice under two
    verdicts; matching the STATEMENT first makes the two cases disjoint by construction.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return ()

    assigned: set[int] = set()
    out: list[Call] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and _is_closure_call(node.value, name):
            assigned.add(node.value.lineno)
            out.append(Call(path=label, line=node.lineno, consumes_both=_unpacks_two(node)))

    # ⚑ A CALL THAT IS NOT ASSIGNED CONSUMES NEITHER HALF. Reporting it as consuming both would
    # excuse the very shape the item is about — a walk that invokes the engine and keeps nothing.
    out.extend(
        Call(path=label, line=node.lineno, consumes_both=False)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and _is_closure_call(node, name)
        and node.lineno not in assigned
    )
    return tuple(out)


def corpus_calls(name: str = CLOSURE) -> tuple[Call, ...]:
    """Return every call to `name` across the corpus.

    ⚑ THE WHOLE CORPUS, NOT ONE HARDCODED FILE. The origin asked only about the gate, so a walk
    re-rolled in a sibling module — or correctly delegated from one — was invisible either way.
    """
    out: list[Call] = []
    for found in corpus.py_files():
        label = str(found).removeprefix(str(corpus.ROOT) + "/")
        out.extend(calls(corpus.ROOT / label, label, name))
    return tuple(out)


def discarding(name: str = CLOSURE) -> tuple[Call, ...]:
    """Return the call sites that take the closure and throw half of it away."""
    return tuple(got for got in corpus_calls(name) if not got.consumes_both)


def render(found: tuple[Call, ...]) -> str:
    """Return the census — every call site, and what it keeps."""
    if not found:
        return f"  no call to {CLOSURE} anywhere in the corpus — the walk is re-rolled\n"

    lines = [f"  {len(found)} call site(s) to {CLOSURE}"]
    lines.extend(
        f"    {got.path}:{got.line}  "
        + ("consumes both returns" if got.consumes_both else f"⚑ {got.route}")
        for got in found
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.stdout.write(render(corpus_calls()))
    sys.exit(0)
