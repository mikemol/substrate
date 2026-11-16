#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report which import-DAG derivations read the catalogued relation and which re-derive it.

⚑⚑⚑ THE RELATION IS ALREADY IN THE STORE, POPULATED AND INDEXED BOTH WAYS. `_module_edges (src,
dst)` holds the module-to-module import graph with an index on each column, so the two inversions
an in-memory DAG materialises — `deps` and `rdeps` — are index seeks that already exist. This is
the one-relation-several-bodies class at DAG scale.

⚑⚑ AND THE PROVENANCE GENUINELY DIFFERS, WHICH IS NOT A DEFECT. A source parse reads `.agda`
text; the catalog decodes `.agdai` CORES. **A source-parsed superset is what the BUILD needs** —
the makefile generator must emit prerequisites for modules that do not compile yet, which a
core-derived relation cannot cover. So the finding is never *"delete the parser"*: it is that
ANALYSIS consumers asking about edges should query the catalog, and only the generator needs the
superset. A verdict lumping the two would prescribe deleting the generator's own input.

⚑⚑ CLOSURE STAYS IN PYTHON, AND THAT IS MEASURED RATHER THAN OMITTED. The ⟡L7 measurement records
a recursive CTE winning ~275x at small N and **LOSING at 0.7x at full N** against in-memory BFS —
a big fixed launch cost against a small one with a larger slope. The store holds zero `RECURSIVE`
deliberately. A reader treating "not in SQL" as debt would propose the slower thing.

⚑ SO THE POPULATION IS DISCOVERED, NOT LISTED. The origin froze two `(file, function)` pairs and
skipped a missing one silently; MEASURED, one of them has since MOVED to a sibling module and is
re-exported, so the frozen roster reports on a file that no longer defines it.

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

# The catalogued relation holding the import graph, and the reader that fronts it.
RELATION = "module_edges"
STORE = "catalog_db"

# How an import appears in a pattern or a literal a derivation matches against.
IMPORT_WORDS = ("open import", "import ")

# The source-parsing derivation every Python-side import graph routes through.
#
# ⚑⚑⚑ THE RELATION IS A CALL EDGE, NOT A FILE-READING HABIT. A first cut credited a module-level
# import regex to every function in the file that touched a file, and reported NINE derivations
# where there are two — including `tree_stamp`, which counts `.agda` files and reads mtimes and
# never looks at an import. **A function that reads files is not thereby deriving the DAG**; one
# that scans import syntax, or calls the parser that does, is.
PARSER = "parse_tree"

# The consumer whose superset requirement makes a source parse correct rather than debt.
GENERATOR = "gen_build_makefiles.py"


@dataclass(frozen=True, slots=True)
class Derivation:
    """One function that builds an import graph, and where it gets its edges."""

    tool: str
    name: str
    line: int
    # It reads the catalogued relation.
    catalogued: bool
    # It scans import syntax, or calls the parser that does.
    reparses: bool

    @property
    def generator(self) -> bool:
        """Report whether this is the build generator, whose superset is required."""
        return self.tool.endswith(GENERATOR)

    @property
    def debt(self) -> bool:
        """Report whether this derivation should be querying the store instead.

        ⚑ THE GENERATOR IS NOT DEBT, and exempting it is the whole reason the two are told apart.
        It must emit prerequisites for modules that do not compile yet — edges no core-derived
        relation holds.
        """
        return self.reparses and not self.catalogued and not self.generator

    @property
    def route(self) -> str:
        """Return what should happen to this row."""
        if self.generator:
            return "keep: source-parsed superset the build generator requires"
        if self.debt:
            return f"query {RELATION} rather than re-walking the imports"
        return ""


def _names_relation(node: ast.AST) -> bool:
    """Report whether a node is a string naming the store or its relation."""
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and (RELATION in node.value or STORE in node.value)
    )


def _names_import(node: ast.AST) -> bool:
    """Report whether a node carries import syntax.

    ⚑⚑ THE SPELLING MAY BE A PATTERN, NOT A PREFIX. MEASURED: the build generator matches imports
    with a compiled regex whose literal begins with an anchor, so a `startswith` test sees nothing
    at all. Asking whether an import keyword appears ANYWHERE in the string covers the pattern and
    the plain form with one question.
    """
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and any(word in node.value for word in IMPORT_WORDS)
    )


def _call_name(node: ast.Call) -> str:
    """Return the name a call invokes, bare or through a receiver."""
    target = node.func
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return ""


def _reads_relation(scope: ast.AST) -> bool:
    """Report whether a scope reaches the catalogued relation."""
    return any(_names_relation(node) for node in ast.walk(scope))


def _reparses(scope: ast.AST) -> bool:
    """Report whether a scope derives the import graph from source.

    ⚑ TWO SHAPES, ONE PROPERTY. A function either matches import syntax itself or calls the
    parser that does — and reading only the first misses every consumer that delegates, which is
    most of them.
    """
    for node in ast.walk(scope):
        if _names_import(node):
            return True
        if isinstance(node, ast.Call) and _call_name(node) == PARSER:
            return True
    return False


def derivations(path: Path, label: str) -> tuple[Derivation, ...]:
    """Read every import-graph derivation in one file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError):
        return ()

    out = []
    for scope in ast.walk(tree):
        if not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        # ⚑ THE PARSER ITSELF IS A DERIVATION even though its pattern is a module constant: it is
        # the definition the call edge points at, so it is named rather than inferred.
        reparses = _reparses(scope) or scope.name == PARSER
        catalogued = _reads_relation(scope)
        if reparses or catalogued:
            out.append(
                Derivation(
                    tool=label,
                    name=scope.name,
                    line=scope.lineno,
                    catalogued=catalogued,
                    reparses=reparses,
                )
            )
    return tuple(out)


def population(tools: tuple[str, ...], root: Path | None = None) -> tuple[Derivation, ...]:
    """Read every import-graph derivation across the named files."""
    where = root if root is not None else corpus.ROOT
    out: list[Derivation] = []
    for rel in tools:
        out.extend(derivations(where / rel, rel))
    return tuple(out)


def debt(rows: tuple[Derivation, ...]) -> tuple[Derivation, ...]:
    """Return the derivations that should be querying the store."""
    return tuple(row for row in rows if row.debt)


def render(rows: tuple[Derivation, ...]) -> str:
    """Render the census, keeping the required superset distinct from debt."""
    if not rows:
        return "  no import-graph derivation found — UNMEASURED, not clean"

    owed = debt(rows)
    if not owed:
        return f"  no analysis consumer re-derives the import DAG ({len(rows)} derivation(s) read)"

    out = [f"  {len(owed)} of {len(rows)} derivation(s) re-derive the catalogued DAG:"]
    out.extend(f"    ⚑ {row.tool}:{row.line}  {row.name} — {row.route}" for row in owed)
    return "\n".join(out)


if __name__ == "__main__":
    _tools = tuple(sys.argv[1:]) or ("scripts/gen_build_makefiles.py", "scratch/split_census.py")
    sys.stdout.write(render(population(_tools)) + "\n")
    sys.exit(0)
