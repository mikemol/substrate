#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Resolve `module.CONST` to the directory it names, by parsing the module that binds it.

⚑⚑⚑ WHY THIS EXISTS (gate-F90). `drain_leverage` ranks what to drain by how many `sys.path`
inserts each drain retires, and it reported a block of sites as opaque-target — a path this
reader cannot name. Those are not distinct opacities: `attr_reads wg_engine.LIBRARY` finds
reads across `wg_dispatch`, `wg_order` and `worklist_gate`, and `wg_engine.LIBRARY` binds
`os.path.join(ROOT, "catalog", "library")` — fully resolvable, one module away.

⚑⚑ THE GAP IS THAT THE RESOLVER FOLLOWS INTRA-FILE BINDINGS ONLY. `insert_read.target_of`
reads string literals inside the call, then falls back to `path_binding.resolve_arg` over
`derived`, which `file_derived_names` computes for THE SAME MODULE. An insert whose target
is an attribute read on an IMPORTED module has neither a literal nor a same-file binding, so
it returns UNKNOWN.

⚑ AND THAT MAKES IT A RANKING DEFECT RATHER THAN A COSMETIC GAP. `unreadable`'s own docstring
says it: *"a name scoring zero retired inserts may simply hold one this reader could not
read."* A whole module family is under-credited, so the answer to *what should I drain first*
is a floor — which is exactly the question the ranking exists to answer.

⚑⚑⚑ IT PARSES, IT NEVER IMPORTS. Importing a module to read a constant runs its top level:
`wg_engine` and its siblings mutate `sys.path` at import, which is the very behaviour being
censused — the reader would perform the defect it measures. So the binding is read from the
AST, and anything the AST cannot settle is REFUSED rather than guessed.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# ⚑ THE SEARCH ORDER IS DECLARED, NOT WALKED. A deep walk can find two modules of one name
# and this reader must not choose between them; the conventional tool directories are where
# an insert's target module actually lives.
TOOL_DIRS: tuple[str, ...] = ("scripts", "substrate", "scratch", "jea/metalanguage", "")


@dataclass(frozen=True)
class Named:
    """A constant that resolves to a directory, and the segments it was built from."""

    directory: str
    segments: tuple[str, ...]


@dataclass(frozen=True)
class Unnamed:
    """Why a constant could not be resolved. Never a fallback — always a reason."""

    reason: str


def _string_segments(node: ast.expr) -> tuple[str, ...] | None:
    """Return the literal path segments of a join-like expression, or None.

    ⚑ ONLY LITERALS COUNT AS SEGMENTS. A non-literal argument means the value depends on
    something this reader is not following, and treating the literals alone would name a
    DIFFERENT directory with full confidence — the false-attribution direction, which is
    worse than the UNKNOWN it replaces.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return (node.value,)
    if not isinstance(node, ast.Call):
        return None
    out: list[str] = []
    for arg in node.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            out.append(arg.value)
        elif isinstance(arg, ast.Call):
            # A nested call (`os.path.join(os.path.dirname(...), "x")`) contributes a ROOT
            # this reader does not name; its own literals still name the tail.
            nested = _string_segments(arg)
            if nested is None:
                return None
            out.extend(nested)
        elif not isinstance(arg, ast.Name):
            # A bare Name is a root binding (`ROOT`) contributing no literal segment, which
            # is correct — the tail is what names the directory. Anything else is unread.
            return None
    return tuple(out) if out else None


def _module_assignments(tree: ast.Module, name: str) -> list[ast.expr]:
    """Return every module-level value assigned to `name`."""
    out: list[ast.expr] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and tgt.id == name:
                out.append(node.value)
                break
    return out


def resolve(source: str, const: str) -> Named | Unnamed:
    """Return the directory `const` names in `source`, or why it could not be read.

    ⚑ AMBIGUITY IS REFUSED. Two module-level bindings of one name means the later wins at
    runtime, but picking it here would attribute an insert to a directory that may not be
    the one in force — and a confident wrong attribution is worse than a reported unknown.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return Unnamed(f"the binding module does not parse: {e}")

    found = _module_assignments(tree, const)
    if not found:
        return Unnamed(f"no module-level assignment binds {const!r}")
    if len(found) > 1:
        return Unnamed(
            f"{len(found)} module-level assignments bind {const!r} — refusing to choose, "
            "since a wrong attribution is worse than a reported unknown",
        )

    segs = _string_segments(found[0])
    if not segs:
        return Unnamed(
            f"{const!r} is bound to an expression with no literal path segments — "
            "refusing to guess the directory it names",
        )
    return Named(segs[-1], segs)


def resolve_in(root: Path, module: str, const: str) -> Named | Unnamed:
    """Resolve `module.CONST` by finding `module` under `root` and parsing it."""
    for sub in TOOL_DIRS:
        cand = root / sub / f"{module}.py" if sub else root / f"{module}.py"
        if cand.is_file():
            return resolve(cand.read_text(encoding="utf-8", errors="replace"), const)
    return Unnamed(f"no module named {module!r} under the conventional tool directories")


def attribute_target(node: ast.Call) -> tuple[str, str] | None:
    """Return the (module, CONST) an insert call reaches for, or None.

    ⚑ THIS IS THE SHAPE `target_of` CANNOT SEE: `sys.path.insert(0, wg_engine.LIBRARY)` has
    no string literal in the call and no same-file binding, so the literal-then-derived
    ladder returns UNKNOWN with nothing left to try.
    """
    for arg in node.args:
        if isinstance(arg, ast.Attribute) and isinstance(arg.value, ast.Name):
            return arg.value.id, arg.attr
    return None
