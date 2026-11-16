# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read one file's import surface: its `sys.path` mutations and its bare imports.

⚑⚑⚑ THIS IS AN EXTRACTION, AND THE GATE ASKED FOR IT RATHER THAN THE EDIT I WANTED.
Wiring `path_binding` into `drain_leverage` needed an import AND a use — two hunks, which
the per-file gate requires in ONE write, which requires the whole file to be clean. That
read as "the edit is too big to stage", and the reflex was to go read 400 lines to satisfy
it. It says the opposite: THE FILE IS TOO BIG TO EDIT. `drain_leverage` held the mutation
detector, the target resolver, the bare-import reader, the leverage join, the ranking and
the CLI — and a two-line wiring could not land because five jobs share one file. Once the
reading moved here, the wiring was free: one file, one import, one use.

⚑⚑ SO THE READING MOVES AND THE RANKING STAYS. Everything here answers ONE question — what
does this file's source say about how it reaches its imports — and nothing here knows what
a drain is, what a candidate is, or how to rank one. That separation is what lets the
resolver improve without touching the ranking, which is the change that was blocked.

⚑ AND THE RESOLVER IT NOW CONSULTS IS THE POINT OF THE MOVE. The origin attributed an insert
only from a string literal or an INLINE `__file__` walk, so `sys.path.insert(0, HERE)` — the
dominant spelling, measured at 111 `HERE` bindings — resolved to nothing and 157 of 492
inserts reported UNKNOWN. `path_binding` resolves that binding one hop out. A name it still
cannot resolve stays UNKNOWN, because a well-formed wrong attribution reads as a measurement
and is worse than the admitted gap.

⚑ THE VOCABULARY IS THE ORIGIN'S, DELIBERATELY. `Insert.line`, `<root>`, `<unresolved>` and
`opaque-target` are spelled exactly as `drain_leverage` spelled them. A cleaner name here
would be a SECOND spelling of one relation — the defect this toolkit keeps paying for — and
the extraction is meant to remove a fork, not open one.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import adopter_import, imported_constant, path_binding

if TYPE_CHECKING:
    from pathlib import Path

# The `sys.path` mutators an insert can be spelled with. ⚑ `append` counts because it is the
# same hazard arriving at the other end of the list.
MUTATORS = frozenset({"insert", "append", "extend"})

# The attribute chain a mutation walks: `sys.path.<mutator>`.
_SYS = "sys"
_PATH = "path"

# `insert(index, path)` carries the path second; `append(path)` carries it first.
_INSERT_ARITY = 2

# The shapes whose target directory this reader cannot name. ⚑ REPORTED AS THEMSELVES, never
# folded into a zero — an insert built from an unresolvable expression is still an insert, and a
# reader that dropped it silently would under-report the debt it exists to measure.
OPAQUE = "opaque-target"

# What a resolved insert target is called when nothing names a recognisable directory.
UNKNOWN = "<unresolved>"

# What a `__file__` walk that climbs past every path component names: the repo root itself.
ROOT_DIR = "<root>"


@dataclass(frozen=True, slots=True)
class Insert:
    """One `sys.path` mutation site, and the directory it makes importable."""

    path: str
    line: int
    target: str

    @property
    def resolved(self) -> bool:
        """Report whether this reader could name the directory the insert adds."""
        return self.target != UNKNOWN


def is_mutation(node: ast.Call) -> bool:
    """Report whether this call mutates `sys.path`."""
    func = node.func
    if not isinstance(func, ast.Attribute) or func.attr not in MUTATORS:
        return False
    owner = func.value
    return (
        isinstance(owner, ast.Attribute)
        and owner.attr == _PATH
        and isinstance(owner.value, ast.Name)
        and owner.value.id == _SYS
    )


def _path_arg(node: ast.Call) -> ast.expr | None:
    """Return the argument naming a directory, or None when the call carries none."""
    args = node.args
    if len(args) >= _INSERT_ARITY:
        return args[1]
    return args[0] if args else None


def _from_depth(label: str, depth: int) -> str:
    """Return the directory `depth` walk-up steps above this file, as a name."""
    parts = label.split("/")[:-1]
    keep = parts[: len(parts) - (depth - 1)] if depth > 1 else parts
    return keep[-1] if keep else ROOT_DIR


def _imported(node: ast.Call, root: Path | None) -> str | None:
    """Return the directory an imported constant names, or None when nothing settles it.

    ⚑⚑ THE FOURTH RUNG, AND THE LADDER WAS BUILT TO TAKE IT (gate-F90). The three rungs above
    read THIS file: a literal in the call, a joined literal, a binding `file_derived_names`
    computed for THIS module. An insert whose target is an attribute on an IMPORTED module —
    `sys.path.insert(0, wg_engine.LIBRARY)` — has none of them, so the ladder ran out with the
    answer one hop away. MEASURED: `attr_reads wg_engine.LIBRARY` finds reads across
    `wg_dispatch`, `wg_order` and `worklist_gate`, which held most of the opaque population.

    ⚑ IT STAYS UNRESOLVED UNLESS THE OTHER MODULE SETTLES IT. `imported_constant` PARSES the
    binding module rather than importing it — importing `wg_engine` would run the `sys.path`
    mutation being censused — and REFUSES an ambiguous or computed binding. A well-formed
    wrong attribution reads as a measurement and is worse than the admitted gap, which is the
    rule this module's own header states about the rung below.

    ⚑ `root` IS OPTIONAL SO EVERY EXISTING CALLER KEEPS WORKING. Without it this rung cannot
    fire and the answer is exactly what it was before — a caller that has not opted in is not
    silently given a different verdict.
    """
    if root is None:
        return None
    reached = imported_constant.attribute_target(node)
    if reached is None:
        return None
    named = imported_constant.resolve_in(root, *reached)
    return named.directory if isinstance(named, imported_constant.Named) else None


def target_of(node: ast.Call, label: str, derived: dict[str, int], root: Path | None = None) -> str:
    """Return the directory an insert names, or UNKNOWN when nothing resolves it.

    ⚑ THE LITERAL SPELLINGS ARE READ FIRST because they are unambiguous: `os.path.join(ROOT,
    "scratch")` and a bare `"scratch"` both name a directory outright. Only when no literal
    is present does this consult the module's bindings, so adding the binding resolver cannot
    change an answer that was already definite.
    """
    leaves = [
        n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)
    ]
    named = [v for v in leaves if v and "/" not in v and v not in (label, "..")]
    if named:
        return named[-1]
    joined = [v for v in leaves if "/" in v]
    if joined:
        return joined[-1].rstrip("/").split("/")[-1]

    arg = _path_arg(node)
    if arg is not None:
        depth = path_binding.resolve_arg(arg, derived)
        if depth is not None:
            return _from_depth(label, depth)

    reached = _imported(node, root)
    return reached if reached is not None else UNKNOWN


def bare_from(node: ast.ImportFrom) -> str | None:
    """Return the bare module a `from` names, or None when it needs no insert.

    ⚑ A DOTTED OR RELATIVE `from` IS EXCLUDED BECAUSE IT NEEDS NO INSERT. `from a.b import c`
    carries its package and travels; `from . import c` names a package this reader cannot
    resolve.

    ⚑⚑ AND A SINGLE-WORD `node.module` IS NOT THEREBY BARE — reading it that way was a MEASURED
    defect in the origin's first cut. `from scripts import ratchet` names the PACKAGE `scripts`,
    resolves for an adopter, and needs no insert; `from ratchet import x` names a module that
    does. Both spell `node.module` as one dot-free word, so the word alone cannot decide it.
    """
    if node.level or not node.module or "." in node.module:
        return None
    if node.module in adopter_import.DEFAULT_PACKAGES:
        return None
    return node.module


def bare_names(tree: ast.AST) -> tuple[str, ...]:
    """Return every module this file imports BARE — reachable only under an insert.

    ⚑ COUNTING DOTTED IMPORTS TOO WOULD MAKE EVERY PACKAGED CONSUMER LOOK LIKE PATH DEBT and
    bury the population that actually is.
    """
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(
                a.name
                for a in node.names
                if "." not in a.name and a.name not in adopter_import.DEFAULT_PACKAGES
            )
        elif isinstance(node, ast.ImportFrom):
            got = bare_from(node)
            if got is not None:
                found.add(got)
    return tuple(sorted(found))


def inserts(tree: ast.AST, label: str, root: Path | None = None) -> tuple[Insert, ...]:
    """Return every `sys.path` mutation site in `tree`, each with the directory it names."""
    derived = path_binding.file_derived_names(tree) if isinstance(tree, ast.Module) else {}
    return tuple(
        Insert(label, n.lineno, target_of(n, label, derived, root))
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and is_mutation(n)
    )
