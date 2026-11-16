#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report which caches store a parse tree WHOLE rather than as interned rows.

⚑⚑⚑ A TREE IN A BLOB IS THE FOUR-COPY FLOOR, AND NO CACHE TUNING REACHES IT. A consumer wanting
ONE node materialises the entire tree, so the copies are: the parse, the serialised form, the
deserialised copy, and whatever the consumer builds from it. **The granularity is the CALL, and a
tree has parts.** The interned form — a node table plus a child table with insert-or-ignore —
makes a subtree shared across hundreds of files exactly one row.

⚑⚑ THE MEASUREMENT THAT SIZES IT: RSS grew 255.3 MB against 66.2 MB traced, with a collection
freeing 240,279 objects and returning 0.0 MB — cyclic parser nodes recycled into arenas the
runtime never hands back. That is why this is a serialisation question and not a cache-size one.

⚑⚑ AND THE PREDICATE IS *"SERIALISES A TREE"*, NOT *"USES A CACHE"*. Caching is right for one
input with one indivisible output — a comment mask, a content hash — and wrong for a CST.
Censusing every cache would flag the sites that are correct, which is the shape that makes a
finding unactionable.

⚑ SO THE READ IS WHAT CROSSES THE SERIALISER, NOT WHETHER A CACHE EXISTS. MEASURED: the site this
item names first now stores a flat list of tuples as JSON — the blob defect was paid down and the
substring predicate could not see it, because it tested for the presence of the interned tables
rather than the absence of a tree.

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

# Calls that write a value out to a store.
SERIALISERS = frozenset({"dump", "dumps"})

# The module whose serialiser preserves arbitrary object graphs — a tree survives it whole.
OPAQUE = "pickle"

# The relations holding the interned tree.
INTERNED = ("node_child", "unit_node", "_node")

# What a parse produces: the names a tree is bound to at a call site.
TREE_SOURCES = frozenset({"parse", "parse_module", "parse_expression", "cst", "tree"})


@dataclass(frozen=True, slots=True)
class Cache:
    """One serialising site, and what crosses it."""

    tool: str
    name: str
    line: int
    # It writes through a serialiser that preserves arbitrary object graphs.
    opaque: bool
    # A parse tree reaches the serialiser.
    serialises_tree: bool
    # It reads or writes the interned relations instead.
    interned: bool

    @property
    def blob(self) -> bool:
        """Report whether a tree is stored whole.

        ⚑ BOTH HALVES. A pickle of a tuple list is not this defect, and a JSON dump of a tree is
        — so the verdict is what CROSSES the serialiser, not which serialiser it is.
        """
        return self.serialises_tree and not self.interned

    @property
    def route(self) -> str:
        """Return what would close this row."""
        if self.blob:
            return f"intern the tree into {INTERNED[0]} rather than storing it whole"
        return ""


def _call_name(node: ast.Call) -> str:
    """Return the name a call invokes, bare or through a receiver."""
    target = node.func
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return ""


def _receiver(node: ast.Call) -> str:
    """Return the receiver a call is made on, when it is a bare name."""
    target = node.func
    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
        return target.value.id
    return ""


def _tree_valued(node: ast.expr) -> bool:
    """Report whether an expression is, or came from, a parse.

    ⚑ THE NAME IS THE EVIDENCE AVAILABLE. Following a binding to its assignment would need a
    dataflow this reader does not have; a value spelled `tree`, or produced by a `parse` call, is
    what a reader can see and is how these sites are actually written.
    """
    if isinstance(node, ast.Name):
        return node.id.lstrip("_") in TREE_SOURCES
    if isinstance(node, ast.Call):
        return _call_name(node) in TREE_SOURCES
    return False


def _serialises_tree(scope: ast.AST) -> bool:
    """Report whether a parse tree reaches a serialiser inside a scope."""
    return any(
        isinstance(node, ast.Call)
        and _call_name(node) in SERIALISERS
        and any(_tree_valued(arg) for arg in node.args)
        for node in ast.walk(scope)
    )


def _uses_opaque(scope: ast.AST) -> bool:
    """Report whether a scope serialises through the object-graph writer."""
    return any(
        isinstance(node, ast.Call) and _call_name(node) in SERIALISERS and _receiver(node) == OPAQUE
        for node in ast.walk(scope)
    )


def _reaches_interned(scope: ast.AST) -> bool:
    """Report whether a scope reads or writes the interned relations."""
    return any(
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and any(rel in node.value for rel in INTERNED)
        for node in ast.walk(scope)
    )


def caches(path: Path, label: str) -> tuple[Cache, ...]:
    """Read every serialising site in one file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError):
        return ()

    out = []
    for scope in ast.walk(tree):
        if not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        opaque = _uses_opaque(scope)
        serialises = _serialises_tree(scope)
        if not (opaque or serialises):
            continue
        out.append(
            Cache(
                tool=label,
                name=scope.name,
                line=scope.lineno,
                opaque=opaque,
                serialises_tree=serialises,
                interned=_reaches_interned(scope),
            )
        )
    return tuple(out)


def population(tools: tuple[str, ...], root: Path | None = None) -> tuple[Cache, ...]:
    """Read every serialising site across the named files."""
    where = root if root is not None else corpus.ROOT
    out: list[Cache] = []
    for rel in tools:
        out.extend(caches(where / rel, rel))
    return tuple(out)


def blobs(rows: tuple[Cache, ...]) -> tuple[Cache, ...]:
    """Return the sites storing a tree whole."""
    return tuple(row for row in rows if row.blob)


def render(rows: tuple[Cache, ...]) -> str:
    """Render the census, naming what an empty population means."""
    if not rows:
        return "  no serialising site found — UNMEASURED, not clean"

    found = blobs(rows)
    if not found:
        return f"  no site stores a parse tree whole ({len(rows)} serialising site(s) read)"

    out = [f"  {len(found)} of {len(rows)} serialising site(s) store a tree whole:"]
    out.extend(f"    ⚑ {row.tool}:{row.line}  {row.name} — {row.route}" for row in found)
    return "\n".join(out)


if __name__ == "__main__":
    _tools = tuple(sys.argv[1:]) or ("scratch/_pycodemod_query.py", "scratch/cache_probe.py")
    sys.stdout.write(render(population(_tools)) + "\n")
    sys.exit(0)
