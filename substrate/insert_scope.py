# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Where a `sys.path` mutation SITS — module level, inside a function, or under a guard.

⚑⚑⚑ THE SCOPE DECIDES WHETHER A DRAIN CAN REACH THE SITE AT ALL, and the flat census cannot
say. A module-level insert runs once at import and is deletable the moment its directory
becomes importable another way. A FUNCTION-SCOPED insert runs on every call, often to reach
something the module deliberately does not depend on — so removing it changes when the import
happens, not merely whether the path is mutated. A guarded one (`if TYPE_CHECKING`, `if not
installed`, a `try` fallback) encodes a CONDITION, and deleting it deletes the condition.

⚑⚑ SO A SINGLE TOTAL OVER-STATES WHAT A CODEMOD CAN DO. Planning a drain against the flat
count treats every site as one edit; measured, they are at least three populations with three
different repairs, and only the first is mechanical. Reporting them together is the shape that
turns a tractable drain into an intractable one — or worse, licenses a sweep that changes
import timing in code nobody re-ran.

⚑ THE ENCLOSING FUNCTION IS TRACKED BY WALKING WITH PARENTS, not by `ast.walk`, which is flat
and loses exactly this. That is why this is a separate reader rather than a field on the flat
census: the traversal is different, and bolting scope onto a flat walk would mean inferring
containment from line numbers — a proxy that breaks on a decorator or a nested def.

⚑ A GUARD IS REPORTED AS A GUARD EVEN AT MODULE LEVEL. `if _ROOT not in sys.path:` is
module-scoped and still conditional, and a reader that called it plainly module-level would
license deleting a check someone added for a reason.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from substrate import insert_read, path_binding

#: A site that runs once, unconditionally, when the module is imported.
MODULE = "module"

#: A site inside a function or method — it runs per call, so removing it moves import timing.
FUNCTION = "function"

#: A site under an `if`/`try` — the branch encodes a condition that deletion would erase.
GUARDED = "guarded"


@dataclass(frozen=True, slots=True)
class Site:
    """One mutation site, with the scope that decides how it can be drained."""

    path: str
    line: int
    target: str
    scope: str
    enclosing: str

    @property
    def is_mechanical(self) -> bool:
        """Whether a codemod could remove this site without changing behaviour.

        ⚑ ONLY THE UNGUARDED MODULE-LEVEL CASE. The other two change WHEN an import happens
        or WHAT condition governs it, and a drain that treated them alike would be editing
        semantics while claiming to edit hygiene.
        """
        return self.scope == MODULE


def _guarding(stack: list[ast.AST]) -> bool:
    """Report whether any enclosing node is a conditional or handler."""
    return any(isinstance(n, (ast.If, ast.Try, ast.While)) for n in stack)


def _enclosing_function(stack: list[ast.AST]) -> str:
    """Return the innermost enclosing function's name, or empty at module level."""
    for node in reversed(stack):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return node.name
    return ""


def _scope_of(stack: list[ast.AST]) -> str:
    """Return the scope kind for a site with this ancestor stack.

    ⚑ FUNCTION BEATS GUARD when both apply. A guarded insert inside a function is still a
    per-call site, and the timing question dominates the condition question — a caller
    deciding what is mechanically drainable must not see it as merely conditional.
    """
    if _enclosing_function(stack):
        return FUNCTION
    if _guarding(stack):
        return GUARDED
    return MODULE


def sites(tree: ast.Module, label: str) -> list[Site]:
    """Return every `sys.path` mutation in `tree`, each with its scope.

    ⚑ THE TARGET IS RESOLVED BY THE EXISTING READER, not re-derived here. Which directory an
    insert names and where the insert sits are two questions, and one authority each is what
    keeps them from disagreeing.
    """
    derived = path_binding.file_derived_names(tree)
    found: list[Site] = []

    def walk(node: ast.AST, stack: list[ast.AST]) -> None:
        """Visit `node`, carrying its ancestors so scope stays knowable."""
        if isinstance(node, ast.Call) and insert_read.is_mutation(node):
            found.append(
                Site(
                    path=label,
                    line=node.lineno,
                    target=insert_read.target_of(node, label, derived),
                    scope=_scope_of(stack),
                    enclosing=_enclosing_function(stack),
                )
            )
        stack.append(node)
        for child in ast.iter_child_nodes(node):
            walk(child, stack)
        stack.pop()

    walk(tree, [])
    return found


def by_scope(found: list[Site]) -> dict[str, list[Site]]:
    """Group sites by scope, so a caller reports three queues rather than one total."""
    out: dict[str, list[Site]] = {MODULE: [], FUNCTION: [], GUARDED: []}
    for site in found:
        out[site.scope].append(site)
    return out


def mechanical(found: list[Site]) -> list[Site]:
    """Return only the sites a codemod could remove without changing behaviour."""
    return [s for s in found if s.is_mechanical]
