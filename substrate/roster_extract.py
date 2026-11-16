# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read a roster literal out of a Python module WITHOUT importing or retyping it.

⚑⚑⚑ THIS EXISTS BECAUSE A HAND TRANSCRIPTION PRODUCED A FALSE COUNT (gate-G216). Reading a
60-item roster by eye to move it produced 47, and that figure was then filed as a CORRECTION to
the tool that had been right all along — a number produced by reading, cited against an
instrument. The remedy is not to read more carefully; it is to never read at all.

⚑⚑ AND IT PARSES RATHER THAN IMPORTS, WHICH IS THE WHOLE SAFETY ARGUMENT. Importing the module
would run its top-level code — a roster module that prints, probes the tree, or shells out would
do all of that as a side effect of being read. `ast` sees the same literal with none of the
consequences, and it works on a module whose imports are unavailable here.

⚑ THE SPAN IS RETURNED AS SOURCE TEXT, NEVER AS RECONSTITUTED OBJECTS. A round trip through
`ast.literal_eval` and back through `repr` would re-spell every string — collapsing the named
escapes this tree deliberately writes, and reflowing nothing. Returning the bytes means the
caller moves exactly what was there.

⚑⚑ AND THE TYPE GATE CAUGHT A REAL DEFECT IN THE FIRST CUT, not a style complaint. It narrowed
the node to `ast.Assign` inside a conditional expression and then read `.value` outside that
narrowing, where the binding is still `stmt` — so the element count would have been read off a
node type that has no value. An explicit `isinstance` statement narrows for the whole block; the
conditional expression narrowed only itself.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from pathlib import Path


class Span(NamedTuple):
    """A named assignment's source span, with the components that located it.

    ⚑ `lines` IS DERIVED, never stored beside the text. A record carrying both a span and its
    own line count lets the two disagree, which is the shape a stale figure hides in.
    """

    name: str
    start: int
    end: int
    text: str

    @property
    def lines(self) -> int:
        """Report how many source lines the span covers."""
        return self.end - self.start + 1

    def why(self) -> str:
        """Return a one-line account naming the components that decided the span."""
        return (
            f"{self.name} spans lines {self.start}-{self.end} "
            f"({self.lines} line(s), {len(self.text)} char(s))"
        )


def _assignment(source: str, name: str) -> ast.Assign | None:
    """Return the top-level `ast.Assign` binding `name`, or None when there is none.

    ⚑ ONE NARROWING, SHARED BY BOTH READERS. The span reader and the element counter asked the
    same question in two places, and the second copy is where the type defect lived.
    """
    for node in ast.parse(source).body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == name:
                return node
    return None


def find_assignment(source: str, name: str) -> Span | None:
    """Return the span of the top-level assignment to `name`, or None when absent.

    ⚑ A MISSING NAME RETURNS None RATHER THAN AN EMPTY SPAN. An empty span would report as a
    zero-line roster and read as "the roster is empty" — the census-green shape, where a fact
    about the query prints as a fact about the file.
    """
    node = _assignment(source, name)
    if node is None:
        return None
    lines = source.splitlines(keepends=True)
    end = node.end_lineno if node.end_lineno is not None else node.lineno
    return Span(name, node.lineno, end, "".join(lines[node.lineno - 1 : end]))


def count_elements(source: str, name: str) -> int | None:
    """Return how many elements the named list/tuple literal holds, or None when absent.

    ⚑⚑ THIS IS THE FIGURE THE HAND COUNT GOT WRONG, so it is answered by the parser rather than
    by a reader. It counts the literal's ELEMENTS — not rows, not lines — which is the same
    population `worklist.py --check` partitions by status and the predicate gate uses as its
    denominator. Three instruments, one population, and they must agree.

    ⚑ None IS RETURNED FOR A NAME THAT IS NOT A LIST, distinct from a list that is empty. A zero
    would say "the roster holds nothing" about a name that is not a roster at all.
    """
    node = _assignment(source, name)
    if node is None or not isinstance(node.value, ast.List | ast.Tuple):
        return None
    return len(node.value.elts)


def read(path: Path, name: str) -> Span | None:
    """Return the named assignment's span from a file on disk."""
    return find_assignment(path.read_text(encoding="utf-8"), name)
