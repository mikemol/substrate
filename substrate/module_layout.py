#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Where a module CUTS — every top-level statement group, named, spanned and sized.

⚑⚑⚑ THE CENSUS THAT NAMES A VIOLATION MUST EXPOSE THE STRUCTURE THAT PAYS IT DOWN. The origin
(`scratch/pycodemod.py --size`) reports a file's code lines against a budget and stops. The very
next question — WHERE does this file cut — had no mode, and the fallback was `grep '^def '`, which
the structural-query hook correctly refuses. A census that reports a defect without exposing the
structure needed to pay it down leaves the paydown to be re-derived by hand, differently, every
time.

⚑⚑ TOP-LEVEL ONLY, AND THAT IS THE POINT. A split moves top-level statements; a nested def
travels with its parent and is noise here. `--dead` lists nested visitor methods (`visit_Call`
&c.) precisely because it does not track scope, which is why it could not answer this question
either.

⚑⚑ AN ANNOTATED ASSIGN IS A BINDING TOO, AND OMITTING IT COST A BREAKAGE. `_BARE_CACHE: dict = {}`
is an `AnnAssign`, not an `Assign`, so the origin's labeller returned `"-"` and the module-level
memo showed up as an unnamed group. Planning a split from that census, the origin's author moved
its only consumer and left the cache behind; `--discards` then died with `NameError: _BARE_CACHE`.
**A census that cannot NAME a thing silently excludes it from every decision made by reading the
census** — a fact about the METHOD reported as a fact about the SUBSTRATE.

⚑⚑ `ast`, NOT libcst, AND THAT IS A DELIBERATE DIVERGENCE FROM THE ORIGIN. The origin's `layout`
parses with `cst` and resolves a `PositionProvider`, so in a checkout without libcst the one mode
whose whole job is "help me split this file" is unavailable — and the origin has already paid for
exactly that: `--size` died in `cst.metadata` despite being pure `ast` + `splitlines`, and a peer
running the tooling by symlink reported the tool as absent when it was present and unreachable.
Every fact this reader needs — kind, name, span, code lines — is carried by `ast` nodes with
`end_lineno`, so the dependency bought nothing and cost availability.

⚑ THE CODE-LINE COUNT EXCLUDES BLANKS AND WHOLE-LINE COMMENTS, matching the origin, because the
number is read against a size budget that counts the same way. A comment-heavy group is not a
large group for splitting purposes; it is a well-documented one.

⚑ PROMOTED AS A READER, NOT AS A PATCH TO THE ORIGIN (⟡promote-pycodemod, the route
`module_importers` and `attr_reads` already took). `scratch/` is a staging area whose correct final
size is zero, and its `INP001` is the exit sign rather than a wall. The origin file carries
thousands of findings and the per-file gate has no partial-credit path, so no edit to it can land;
extraction is the move the gate's own refusal text names.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

from substrate import corpus
from substrate.ratchet_flags import check_argv

# The kinds a top-level statement is reported as. ⚑ NAMED ONCE: the classifier, the render and the
# cases cite these rather than respelling the strings, so a renamed kind cannot leave a case
# asserting the old spelling while the classifier emits the new one.
DEF: str = "def"
CLASS: str = "class"
GUARD: str = "if"
STMT: str = "stmt"

# The label a statement group gets when nothing in it binds a readable name. ⚑ IT IS A CONSTANT
# BECAUSE IT IS A FINDING: a group rendered as this is one a split plan cannot refer to, which is
# the `_BARE_CACHE` incident in the header.
UNNAMED: str = "-"

# The name every `if __name__ == "__main__":` group is reported under.
GUARD_NAME: str = "__main__ guard"

# The node types that carry a `decorator_list`. ⚑ ENUMERATED RATHER THAN REACHED BY `getattr`,
# because `getattr(node, "decorator_list", [])` types as `Any` and this package forbids `Any` from
# being spelled OR inferred — and the enumeration is also the honest statement of what the grammar
# allows, which a defaulted attribute lookup silently widens to "anything might have one".
_DECORATED = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


@dataclass(frozen=True, slots=True)
class Group:
    """One top-level statement group: what it is, what it is called, where it runs, how big."""

    kind: str
    name: str
    first_line: int
    last_line: int
    code_lines: int

    @property
    def span(self) -> int:
        """Return the group's total line span, comments and blanks included."""
        return self.last_line - self.first_line + 1


def _is_main_guard(node: ast.If) -> bool:
    """Return whether this `if` is the `__name__ == "__main__"` entry guard.

    ⚑ TESTED STRUCTURALLY, NOT BY SOURCE TEXT. A module may carry other top-level `if`s — a
    version fork, an optional-import guard — and calling every one of them the entry guard would
    put a name on a group that does not have it, which is the `UNNAMED` defect inverted: a
    confident WRONG name is worse than an honest missing one.
    """
    test = node.test
    if not isinstance(test, ast.Compare) or len(test.ops) != 1:
        return False
    if not isinstance(test.ops[0], ast.Eq):
        return False
    left, right = test.left, test.comparators[0]
    return (
        isinstance(left, ast.Name)
        and left.id == "__name__"
        and isinstance(right, ast.Constant)
        and right.value == "__main__"
    )


def _assign_name(node: ast.stmt) -> str | None:
    """Return the name a plain or annotated assignment binds, or None.

    ⚑ BOTH SPELLINGS, AND THE SECOND IS WHY THIS FUNCTION EXISTS. `x = {}` is an `Assign` and
    `x: dict = {}` is an `AnnAssign`; a reader that knows one of two live spellings reports a fact
    about ITSELF as a fact about the module (`census-keyed-on-one-spelling`).
    """
    if isinstance(node, ast.Assign) and node.targets:
        target = node.targets[0]
        return target.id if isinstance(target, ast.Name) else None
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id
    return None


def _label(node: ast.stmt) -> str:
    """Return a short name for a non-def, non-class top-level statement.

    ⚑ A DOCSTRING IS RECOGNISED BY POSITION-INDEPENDENT SHAPE — a bare string expression — because
    the module docstring and a stray string literal are the same node and both are correctly
    reported as `docstring` for splitting purposes: neither carries a binding to move.
    """
    name = _assign_name(node)
    if name is not None:
        return name
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return "import"
    if (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    ):
        return "docstring"
    return UNNAMED


def _kind_and_name(node: ast.stmt) -> tuple[str, str]:
    """Return the reported `(kind, name)` for one top-level statement."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return DEF, node.name
    if isinstance(node, ast.ClassDef):
        return CLASS, node.name
    if isinstance(node, ast.If):
        return (GUARD, GUARD_NAME) if _is_main_guard(node) else (STMT, UNNAMED)
    return STMT, _label(node)


def first_line_of(node: ast.stmt) -> int:
    """Return the first line a cut must keep with this statement — decorators included.

    ⚑⚑ A DECORATED DEF SPANS ITS DECORATORS, AND `node.lineno` DOES NOT SAY SO. On a decorated
    `FunctionDef` it points at the `def` keyword, not at the first `@`, so a split cutting on that
    line leaves the decorators behind in the donor file — a syntax error in BOTH halves. This is
    the one place where the obvious field is the wrong one, so it is a named function rather than
    an inline expression: the next reader gets the reason, not just the arithmetic.
    """
    if isinstance(node, _DECORATED) and node.decorator_list:
        return min(node.lineno, *(d.lineno for d in node.decorator_list))
    return node.lineno


def _code_lines(lines: list[str], first: int, last: int) -> int:
    """Return the count of lines in `[first, last]` that are neither blank nor whole-line comments.

    ⚑ THE SLICE IS 1-BASED BECAUSE `ast` LINE NUMBERS ARE. Reading `lines[first:last]` instead of
    `lines[first - 1:last]` drops the group's own header — the `def` line — which understates
    every group by exactly one and understates a file of N groups by N.
    """
    return sum(
        1 for line in lines[first - 1 : last] if line.strip() and not line.lstrip().startswith("#")
    )


def groups(source: str) -> tuple[Group, ...]:
    """Return every top-level statement group in `source`, in source order."""
    tree = ast.parse(source)
    lines = source.splitlines()
    out: list[Group] = []
    for node in tree.body:
        kind, name = _kind_and_name(node)
        first = first_line_of(node)
        last = node.end_lineno if node.end_lineno is not None else node.lineno
        out.append(
            Group(
                kind=kind,
                name=name,
                first_line=first,
                last_line=last,
                code_lines=_code_lines(lines, first, last),
            )
        )
    return tuple(out)


def of_file(path: Path) -> tuple[Group, ...]:
    """Return the top-level groups of the module at `path`.

    ⚑ AN UNPARSEABLE FILE YIELDS NOTHING AND DOES NOT RAISE, so one bad file in a corpus walk does
    not take the whole census down — the far larger error. `report` prints the denominator, so a
    file that contributed no rows is still visible in the accounting.
    """
    try:
        return groups(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return ()


def render(label: str, rows: tuple[Group, ...]) -> str:
    """Return one file's layout — a line per group, then the totals a split plan reads."""
    out = [f"── {label}"]
    out.extend(
        f"  {g.kind:<6} {g.first_line:>5}-{g.last_line:<5} {g.code_lines:>5} code  {g.name}"
        for g in rows
    )
    out.append(f"   {len(rows)} top-level group(s), {sum(g.code_lines for g in rows)} code lines")
    return "\n".join(out) + "\n"


def report(paths: tuple[Path, ...]) -> str:
    """Return the layout of every file that has one, and the population it was read from.

    ⚑⚑ THE DENOMINATOR IS PRINTED EVEN WHEN NOTHING RENDERED. `no groups` and `no groups across 0
    of 1144 files` are the same finding; only the second lets a reader see the walk HAPPENED. This
    module is a splitting aid, so a silent empty result reads as *this file needs no split* — the
    confident zero, on the question where it is most expensive.
    """
    out: list[str] = []
    shown = 0
    for path in paths:
        rows = of_file(path)
        if not rows:
            continue
        shown += 1
        out.append(render(str(path), rows))
    out.append(f"module_layout: {shown} of {len(paths)} file(s) had top-level groups\n")
    return "".join(out)


def population(requested: tuple[str, ...]) -> tuple[Path, ...]:
    """Return the files to read: those named on the command line, else the whole corpus."""
    return tuple(Path(p) for p in corpus.py_files(*requested))


def main(argv: tuple[str, ...]) -> int:
    """Print the top-level layout of each named module, or of the whole corpus."""
    if (code := check_argv(argv, (), "module_layout")) is not None:
        return code
    sys.stdout.write(report(population(argv)))
    return 0


# ⚑ `--selftest` DELEGATES TO THE SIBLING SUITE (⟡selftest-discovery); anything else is a path
# population, which is this reader's whole argument surface.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import module_layout_selftest

        raise SystemExit(module_layout_selftest.selftest())
    raise SystemExit(main(tuple(sys.argv[1:])))
