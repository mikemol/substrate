#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report whether a tool's write paths are gated and armed, per write.

⚑⚑⚑ THE ORIGIN ASKED THREE SUBSTRING QUESTIONS OF THE WHOLE FILE, AND EACH IS SATISFIED BY PROSE.
`"edit_snapshot" not in src` is false for a file whose comment EXPLAINS why it has no snapshot; a
docstring naming `--apply` satisfies the gate check; and all three are file-wide, so **one armed
write makes every other write in the file read as armed.** A tool with three write paths and one
guard passes.

⚑⚑ AND THE SUBSTRING TEST WOULD ALSO HAVE MISSED THE TRUTH FROM THE OTHER SIDE. MEASURED:
`--calls edit_snapshot` on the live tool reports **0 calls, 3 refs** — the guard is reached
through `import edit_snapshot as _es` and called as `_es.guard(...)`, so a call census keyed on
the module name reports an armed tool as unarmed. **Two spellings of one act**, which is why the
question asked here is *does this write have a guard call before it*, never *does this file
mention a guard*.

⚑ SO THE UNIT IS THE WRITE, NOT THE FILE. Each `open(..., "w")` is a row; a row is GATED when its
enclosing function tests the apply flag and ARMED when a snapshot guard is called before it.
Reporting per file is what let one guard cover three writes.

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

# The call that opens a file for writing.
OPENER = "open"

# The write modes a row is opened in.
WRITE_MODES = frozenset({"w", "a", "wb", "ab", "w+", "a+"})

# The guard that makes a write recoverable.
GUARD = "guard"

# The flag that must gate a write.
APPLY = "--apply"

# Scopes whose writes are fixtures, not edits to the tree.
#
# ⚑⚑⚑ A TEST WRITING ITS OWN FIXTURES OWES NO SNAPSHOT, AND THE FIRST CUT REPORTED 26 OF 29
# UNPROTECTED BECAUSE OF IT. Every flagged row sat inside `_selftest`, writing into a
# `TemporaryDirectory` — a population entirely manufactured by the reader's scope, and at that
# ratio it reads as a catastrophe in the tool rather than as a defect in the census.
#
# ⚑ NAMED BY SCOPE, NOT BY PATH. Asking whether the destination is a temp directory would need to
# follow a variable to its binding; asking which function encloses the write is decidable, and
# the enclosing suite is exactly what makes the write a fixture.
FIXTURE_SCOPES = frozenset({"_selftest", "selftest"})


def called_name(node: ast.Call) -> str:
    """Return the name a call invokes, whether bare or through a module.

    ⚑ ONE READER FOR BOTH SPELLINGS. `guard(...)` and `_es.guard(...)` are the same act, and a
    census seeing only one of them reports a live tool's state backwards — measured on this very
    subject.
    """
    target = node.func
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return ""


@dataclass(frozen=True, slots=True)
class Write:
    """One write path, and what protects it."""

    tool: str
    line: int
    # A snapshot guard is called before this write, in the same function.
    armed: bool
    # The enclosing function tests the apply flag.
    gated: bool

    @property
    def protected(self) -> bool:
        """Report whether the write is both gated and armed."""
        return self.armed and self.gated

    @property
    def missing(self) -> tuple[str, ...]:
        """Return what this write lacks, named so a reader can act."""
        out = []
        if not self.gated:
            out.append(f"no {APPLY} gate: a read would write")
        if not self.armed:
            out.append("no snapshot guard: a write with no recovery")
        return tuple(out)


def _modes_of(node: ast.Call) -> set[str]:
    """Return the string arguments a call was given, positional or by keyword."""
    found = {
        arg.value
        for arg in node.args
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
    }
    found.update(
        kw.value.value
        for kw in node.keywords
        if kw.arg == "mode"
        and isinstance(kw.value, ast.Constant)
        and isinstance(kw.value.value, str)
    )
    return found


def _is_write_open(node: ast.Call) -> bool:
    """Report whether a call opens a file for writing."""
    return called_name(node) == OPENER and bool(_modes_of(node) & WRITE_MODES)


def _guard_lines(scope: ast.AST) -> tuple[int, ...]:
    """Return the lines where a snapshot guard is called inside a scope."""
    return tuple(
        inner.lineno
        for inner in ast.walk(scope)
        if isinstance(inner, ast.Call) and called_name(inner) == GUARD
    )


def _tests_apply(scope: ast.AST) -> bool:
    """Report whether a scope branches on the apply flag."""
    return any(
        isinstance(inner, ast.Constant) and inner.value == APPLY for inner in ast.walk(scope)
    )


def _by_line(row: Write) -> int:
    """Order writes by where they appear."""
    return row.line


def _fixture_lines(tree: ast.Module) -> frozenset[int]:
    """Return every line inside a fixture scope, nested helpers included.

    ⚑⚑ A NESTED HELPER IS STILL A FIXTURE, AND EXCLUDING BY NAME ALONE MISSED IT. MEASURED: after
    exempting `_selftest`, one row survived — `_via_disk`, a two-line helper DEFINED INSIDE that
    suite to write a fixture to disk. Its own name is in no exempt set, so a name-keyed exclusion
    reported the suite's own scaffolding as an unguarded write to the tree.

    ⚑ THE SPAN IS THE ANSWER, NOT THE NAME. Everything lexically inside the suite is the suite's,
    whatever it is called — decidable from the extent, and needing no roster of helper names that
    would go stale on the next one.
    """
    out: set[int] = set()
    for scope in ast.walk(tree):
        if (
            isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef))
            and scope.name in FIXTURE_SCOPES
            and scope.end_lineno is not None
        ):
            out.update(range(scope.lineno, scope.end_lineno + 1))
    return frozenset(out)


def writes(path: Path, label: str) -> tuple[Write, ...]:
    """Read every write path in one tool, with what protects it.

    ⚑ THE SCOPE IS THE ENCLOSING FUNCTION. A guard anywhere in the file protects nothing at a
    write in a different function, and file-scope matching is what let one guard cover three
    writes.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError):
        return ()

    fixtures = _fixture_lines(tree)
    out: dict[int, Write] = {}
    for scope in ast.walk(tree):
        if not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        guards = _guard_lines(scope)
        gated = _tests_apply(scope)
        for node in ast.walk(scope):
            if not (isinstance(node, ast.Call) and _is_write_open(node)):
                continue
            if node.lineno in fixtures:
                continue
            # ⚑ KEYED BY LINE, BECAUSE A NESTED FUNCTION IS WALKED TWICE. `ast.walk` yields the
            # inner scope AND reaches it again from the outer one, so a write inside a closure
            # was reported twice — once with the inner scope's guards and once with the outer's,
            # disagreeing about the same line. The innermost reading wins: it is the scope that
            # actually encloses the write.
            found = Write(
                tool=label,
                line=node.lineno,
                armed=any(at < node.lineno for at in guards),
                gated=gated,
            )
            if node.lineno not in out or found.protected:
                out[node.lineno] = found
    return tuple(sorted(out.values(), key=_by_line))


def unprotected(rows: tuple[Write, ...]) -> tuple[Write, ...]:
    """Return the writes missing a gate, a guard, or both."""
    return tuple(row for row in rows if not row.protected)


def population(tools: tuple[str, ...], root: Path | None = None) -> tuple[Write, ...]:
    """Read every write path across the named tools."""
    where = root if root is not None else corpus.ROOT
    out: list[Write] = []
    for rel in tools:
        out.extend(writes(where / rel, rel))
    return tuple(out)


def render(rows: tuple[Write, ...]) -> str:
    """Render the census, naming what an empty population means."""
    if not rows:
        return "  no write path found — UNMEASURED, not clean"

    missing = unprotected(rows)
    if not missing:
        return f"  all {len(rows)} write path(s) are gated and armed"

    out = [f"  {len(missing)} of {len(rows)} write path(s) are unprotected:"]
    out.extend(f"    ⚑ {row.tool}:{row.line}  {'; '.join(row.missing)}" for row in missing)
    return "\n".join(out)


if __name__ == "__main__":
    _tools = tuple(sys.argv[1:]) or ("scratch/bibstruct.py",)
    sys.stdout.write(render(population(_tools)) + "\n")
    sys.exit(0)
