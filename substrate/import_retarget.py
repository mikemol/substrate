# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Retarget `from <old> import <name>` to `from <new> import <name>`, hoisting deferred imports.

⚑⚑⚑ BUILT FOR THE TWIN RETIREMENTS (W46), WHERE A ONE-LINE REPOINT IS NOT ONE LINE. Substrate's
twins of mtools modules are imported from inside functions in several consumers — deferred to
dodge an import CYCLE inside substrate. The replacement lives in an installed package, so no
cycle is possible and the honest repoint HOISTS the import to the module's top block. Done by
hand that is an edit at the top and a deletion inside a function: two hunks the per-file gate
refuses separately (an unused import, then a redefinition), and a textual `sed` the structural
hook refuses outright. So it is a transform over the tree, applied in one write.

⚑⚑ A DEFERRED LINE GOES WITH ITS TRAILING COMMENT. libcst attaches a trailing comment to the
statement line, so removing the line removes the comment — including any line-scoped directive
that justified the deferral. The justification ended with the cycle; carrying the comment onto
the hoisted import would restate a reason that no longer holds.

⚑ NODES ARE REBUILT WITH `dataclasses.replace`, NOT `with_changes`. libcst nodes are dataclasses;
`replace` keeps each node's precise type where `with_changes` returns `Any`.

⚑ THE WALK COVERS EVERY INDENTED BLOCK REACHABLE THROUGH A `body` — functions, classes, `if`,
`with`, `for`, `while`, `try`. An import in an `else`/`except`/`finally` arm is NOT reached; a
run over a file with one there leaves it standing, and `module_importers` still reports it.

⚑ ONE TOP-LEVEL IMPORT IS INSERTED, after the last top-level import, however many sites there
were. GROUP ORDER IS NOT DECIDED HERE: `ruff check --select I --fix` owns import sorting.

⚑ DRY BY DEFAULT: the unified diff is printed and nothing is written without `--apply`.

    python -m substrate.import_retarget <old-parent> <name> <new-parent> <file> ... [--apply]
"""

from __future__ import annotations

import dataclasses
import difflib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import libcst as cst
from libcst.helpers import get_full_name_for_node

if TYPE_CHECKING:
    from collections.abc import Sequence

# The exit a refused invocation returns.
USAGE_EXIT = 2

USAGE = (
    "usage: python -m substrate.import_retarget <old-parent> <name> <new-parent> <file> ... "
    "[--apply]"
)

# The flag that turns the dry run into a write.
APPLY = "--apply"

# The positional operands before the file list: old parent, name, new parent.
_HEAD = 3


@dataclass(slots=True)
class _Move:
    """What one retarget is moving, and what it found."""

    parent: str
    name: str
    removed: int = 0
    asname: str | None = None


def _keep(move: _Move, alias: cst.ImportAlias) -> bool:
    """Return False for the alias being moved, recording that it was seen."""
    if get_full_name_for_node(alias.name) != move.name:
        return True
    move.removed += 1
    if alias.asname is not None and isinstance(alias.asname.name, cst.Name):
        move.asname = alias.asname.name.value
    return False


def _line(move: _Move, node: cst.SimpleStatementLine) -> cst.SimpleStatementLine | None:
    """Return the line without the moved name, or None when nothing of it remains."""
    if len(node.body) != 1 or not isinstance(node.body[0], cst.ImportFrom):
        return node
    stmt = node.body[0]
    if stmt.relative or stmt.module is None or isinstance(stmt.names, cst.ImportStar):
        return node
    if get_full_name_for_node(stmt.module) != move.parent:
        return node
    kept = [alias for alias in stmt.names if _keep(move, alias)]
    if len(kept) == len(stmt.names):
        return node
    if not kept:
        return None
    kept[-1] = dataclasses.replace(kept[-1], comma=cst.MaybeSentinel.DEFAULT)
    return dataclasses.replace(node, body=[dataclasses.replace(stmt, names=kept)])


# The compound statements whose `body` the walk descends into.
_Compound = cst.FunctionDef | cst.ClassDef | cst.If | cst.For | cst.While | cst.With | cst.Try
_COMPOUND = (cst.FunctionDef, cst.ClassDef, cst.If, cst.For, cst.While, cst.With, cst.Try)


def _descend(move: _Move, stmt: _Compound) -> _Compound:
    """Rewrite a compound statement's indented `body`; a one-line suite is left as it is."""
    inner = stmt.body
    if not isinstance(inner, cst.IndentedBlock):
        return stmt
    rewritten = _block(move, inner.body)
    if not rewritten:
        rewritten = [cst.SimpleStatementLine(body=[cst.Pass()])]
    return dataclasses.replace(stmt, body=dataclasses.replace(inner, body=rewritten))


def _block(move: _Move, stmts: Sequence[cst.BaseStatement]) -> list[cst.BaseStatement]:
    """Rewrite a statement sequence, descending into every compound statement's `body`."""
    out: list[cst.BaseStatement] = []
    for stmt in stmts:
        if isinstance(stmt, cst.SimpleStatementLine):
            kept = _line(move, stmt)
            if kept is not None:
                out.append(kept)
        elif isinstance(stmt, _COMPOUND):
            out.append(_descend(move, stmt))
        else:
            out.append(stmt)
    return out


def _top_level(
    stmts: list[cst.BaseStatement],
) -> list[cst.SimpleStatementLine | cst.BaseCompoundStatement]:
    """Narrow a sequence to what a `Module` body holds; every statement is one of the two."""
    return [s for s in stmts if isinstance(s, (cst.SimpleStatementLine, cst.BaseCompoundStatement))]


def _is_import(stmt: cst.BaseStatement) -> bool:
    """Report whether a top-level statement is an import line."""
    return isinstance(stmt, cst.SimpleStatementLine) and any(
        isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body
    )


def _module_name(dotted: str) -> cst.Attribute | cst.Name:
    """Parse a dotted module name into the node an `ImportFrom` takes."""
    parsed = cst.parse_expression(dotted)
    if not isinstance(parsed, (cst.Attribute, cst.Name)):
        msg = f"not a dotted module name: {dotted!r}"
        raise TypeError(msg)
    return parsed


def retarget(src: str, old: str, name: str, new: str) -> tuple[str, int]:
    """Return `src` with `name` imported from `new` instead of `old`, and how many sites moved."""
    move = _Move(parent=old, name=name)
    module = cst.parse_module(src)
    body = _top_level(_block(move, module.body))
    if not move.removed:
        return src, 0
    alias = cst.ImportAlias(
        name=cst.Name(name),
        asname=cst.AsName(cst.Name(move.asname)) if move.asname else None,
    )
    added = cst.SimpleStatementLine(body=[cst.ImportFrom(module=_module_name(new), names=[alias])])
    last = max((i for i, stmt in enumerate(body) if _is_import(stmt)), default=-1)
    body.insert(last + 1, added)
    return dataclasses.replace(module, body=body).code, move.removed


def main(argv: list[str]) -> int:
    """Print the diff for each file, and write it only under `--apply`."""
    apply = APPLY in argv
    operands = [a for a in argv[1:] if a != APPLY]
    if len(operands) <= _HEAD:
        sys.stderr.write(USAGE + "\n")
        return USAGE_EXIT
    old, name, new, *files = operands
    moved_total = 0
    for file in files:
        path = Path(file)
        before = path.read_text(encoding="utf-8")
        after, moved = retarget(before, old, name, new)
        moved_total += moved
        if not moved:
            sys.stdout.write(f"{file}: no `from {old} import {name}` - unchanged\n")
            continue
        diff = difflib.unified_diff(
            before.splitlines(keepends=True), after.splitlines(keepends=True), file, file
        )
        sys.stdout.writelines(diff)
        if apply:
            path.write_text(after, encoding="utf-8")
    verb = "wrote" if apply else "would write (dry run; --apply to write)"
    sys.stdout.write(f"{moved_total} site(s) over {len(files)} file(s); {verb}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
