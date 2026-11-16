# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What an import edge COSTS to cut — the axis a feedback-arc solver does not model.

⚑⚑⚑ AN EXACT MINIMUM CAN BE UNUSABLE, AND THAT IS WHY THIS EXISTS. `feedback_arc` returns a
proven minimum edge set, and on the census knot it named the STRUCTURAL edges: one direction is
a module-scope import whose caller consumes the callee's output, the other is a single line
inside a selftest importing the peer only to assert against its census. Both are one edge, so a
solver minimising edge COUNT cannot distinguish them. The minimum is correct and unusable —
not approximate, not buggy, but uniform where the domain is not.

⚑⚑ THE AXIS IS LOAD-BEARING-AT-RUNTIME VERSUS LOAD-BEARING-FOR-AN-ASSERTION. A module-scope
import runs whenever anything imports the file; a function-scoped one runs when that function
is called; an import inside a selftest runs only when the file tests itself. Cutting the third
changes no production behaviour, which is what makes it cheap — and no count of edges can say
so.

⚑ THIS IS A THIRD CATEGORY BESIDE IMPORT-VERSUS-READ, and a peer named the gap from the other
side: their closure reader separates IMPORT roots (which cone-expand) from READ roots (which do
not, since a `read_text` never loads imports), precisely because a real edge can carry no
transitive weight. A test-only import is real, carries transitive weight when it runs, and runs
in no production path. Neither repo had a name for it.

⚑ THE WEIGHTS ARE ORDINAL, NOT A CURRENCY. They rank edges for a cut decision; adding them or
comparing them across graphs would be inventing precision the classification does not have. A
solver consuming them should break ties, never compute a budget.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

# ⚑ THE THREE KINDS, CHEAPEST FIRST. A lower weight is a cheaper cut.
TEST_ONLY = "test-only"
DEFERRED = "deferred"
STRUCTURAL = "structural"

_WEIGHT = {TEST_ONLY: 0, DEFERRED: 1, STRUCTURAL: 2}

# Function names whose body runs only when a file exercises itself. ⚑ NAMED RATHER THAN
# PATTERN-MATCHED: `_selftest` and `selftest` are this repo's spellings, and admitting anything
# containing "test" would sweep in a production function that merely tests a condition.
SELFTEST_NAMES = frozenset({"selftest", "_selftest", "_cases", "main_selftest"})


@dataclass(frozen=True, slots=True)
class EdgeCost:
    """One import edge, and how expensive cutting it would be."""

    importer: str
    imported: str
    kind: str
    site: str = ""

    @property
    def weight(self) -> int:
        """Ordinal cost of cutting this edge — lower is cheaper.

        ⚑ AN UNKNOWN KIND COSTS THE MOST. A reader that could not classify an edge must not
        make it look cheap, or the cut lands on the one edge nobody understood.
        """
        return _WEIGHT.get(self.kind, _WEIGHT[STRUCTURAL])

    @property
    def is_cheap(self) -> bool:
        """Whether cutting this edge changes no production behaviour."""
        return self.kind == TEST_ONLY


def _enclosing(stack: list[ast.AST]) -> str:
    """Return the innermost enclosing function's name, or empty at module scope."""
    for node in reversed(stack):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return node.name
    return ""


def _kind_for(enclosing: str) -> str:
    """Return the cost kind for an import inside `enclosing`."""
    if not enclosing:
        return STRUCTURAL
    if enclosing in SELFTEST_NAMES:
        return TEST_ONLY
    return DEFERRED


def classify(tree: ast.Module, importer: str, names: set[str]) -> list[EdgeCost]:
    """Return a cost for each import in `tree` whose bound name is in `names`.

    ⚑ THE WALK CARRIES PARENTS because scope is the whole question — `ast.walk` is flat and
    would report every import as module-scope, collapsing the three kinds into the most
    expensive one and making every cut look equally hard.
    """
    found: list[EdgeCost] = []

    def visit(node: ast.AST, stack: list[ast.AST]) -> None:
        """Visit `node`, remembering its ancestors so scope stays knowable."""
        bound: list[str] = []
        if isinstance(node, ast.Import):
            bound = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            bound = [node.module, *[a.name for a in node.names]]
        for name in bound:
            if name in names:
                enclosing = _enclosing(stack)
                found.append(EdgeCost(importer, name, _kind_for(enclosing), enclosing))
        stack.append(node)
        for child in ast.iter_child_nodes(node):
            visit(child, stack)
        stack.pop()

    visit(tree, [])
    return found


def cheapest(costs: list[EdgeCost]) -> EdgeCost | None:
    """Return the cheapest edge to cut, or None when there is none.

    ⚑ TIES BREAK ON THE IMPORTED NAME, so two runs over an unchanged tree agree and a diff
    of two reports shows movement rather than dict ordering.
    """
    if not costs:
        return None
    ranked = sorted((c.weight, c.importer, c.imported) for c in costs)
    want = ranked[0]
    for cost in costs:
        if (cost.weight, cost.importer, cost.imported) == want:
            return cost
    return None


def render(costs: list[EdgeCost]) -> str:
    """Render the edges by cutting cost, cheapest first."""
    ordered = sorted((c.weight, c.importer, c.imported, c.kind, c.site) for c in costs)
    out = [f"{len(costs)} edge(s) by cutting cost (cheapest first):"]
    out.extend(
        f"  [{weight}] {kind:<11} {importer} -> {imported}"
        + (f"   in {site}()" if site else "   at module scope")
        for weight, importer, imported, kind, site in ordered
    )
    # ⚑ THE POINT OF THE READING, STATED. A solver that minimises COUNT cannot see this
    # column, so a minimum it returns may name the most expensive edges available.
    out.append(
        "   ⚑ a count-minimising solver cannot see this column — its minimum may "
        "name the costliest cut."
    )
    return "\n".join(out) + "\n"
