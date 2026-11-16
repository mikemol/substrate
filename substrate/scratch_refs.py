#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which lines of a Python file reference `scratch/` — and whether each is a PATH or a MENTION.

⚑⚑⚑ THE FIRST DRAIN OF THE ⟡drain-arc (operator ruling, 2026-09-19). The gate
`scripts/check_scratch_independence.py` carries 363 pycheck findings under the all-or-nothing
per-file gate, so a ONE-LINE repair to its selftest — an arm pinning `809 in _dep` where the
coupling had moved to 811 — was refused whole (gate-G376). The gate's own refusal text is the
design: *"extract the one concern you need into a NEW module, written clean in one pass, and let
the next consumer import that instead."* This is that concern: the three readers that decide what
a `scratch` reference IS, moved verbatim in logic and typed at the seams.

⚑⚑ THE GATE'S OWN DEFINITION IS NARROWER THAN ITS IMPLEMENTATION, AND THAT GAP IS KEPT ON PURPOSE.
Its docstring says LIVE means *"a string literal USED AS A PATH"*; `scan_file` flags EVERY
non-docstring string containing `scratch`, error messages included. Over `jea/` (8 hits) that is
harmless; over `scripts/` it reported 129 of which the large majority were diagnostics, and the
gate itself accounted for 20 by describing its own findings. A count nobody can act on is not a
measurement. So `dependency_sites` NARROWS BY USE and the wide reading is kept, not discarded:
`--scope` reports both, DEPENDENCIES (this predicate) and MENTIONS (the rest). A mention is not
nothing — a stale path in a diagnostic is a broken pointer — it is simply not a runtime
dependency, and collapsing the two is the cleaver. `scan_file` is the gate's predicate and
narrowing it would change a verdict, so it is unchanged.

⚑⚑ TWO MEASURED MISCLASSIFICATIONS ARE ARMS IN THIS MODULE'S SUITE, NOT COMMENTS.
  - `append` is not path-shaped. Admitting it matched `reasons.append(f"… scratch/ …")` on the
    call NAME while the scratch-bearing string was prose in an f-string. `list.append` says
    nothing about paths; `sys.path.append` does, so `append` is admitted only under a `path`
    receiver.
  - The argument must be the string ITSELF, not any descendant. `ast.walk` reached into an
    f-string's interpolated `relpath(...)` and credited the whole node, so a diagnostic that
    merely NAMED a path operation read as performing one.

⚑ `guard_depth` DISTINGUISHES HARD FROM GUARDED, NEVER FINE. A module-level import after a
`sys.path.insert` is HARD — the file cannot be imported without `scratch/`, so a gate there
cannot run at all. The same import inside a `try:` or a `def` DEGRADES: it takes an except-branch
and continues, possibly reporting less. And `guarded` is not a clean bill (⟡inert-guard): a guard
whose import ALWAYS fails satisfies a census while never running. What the fallback does is a
separate question this reader cannot answer, and it says so by never returning `fine`.

⚑ EVERY `ast` READ IS NARROWED BY `isinstance` AT THE SEAM, AND THE NARROWING KEEPS THE NODE.
`ast.Constant.value` and every `getattr` over a node are `Any` by construction. A helper that
returned only the string left its caller holding a bare `ast.AST` with no `lineno` — so the
helper returns the NARROWED NODE, and the caller reads both text and position from something
the type system can see.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# The substring whose presence in a string literal or import name makes it a reference at all.
NEEDLE = "scratch"

# How a hit is classified by `scan_file`.
PATH_STRING = "path-string"
IMPORT = "import"

# How deep a reference sits, per `guard_depth`. ⚑ THERE IS NO `fine`.
HARD = "HARD"
GUARDED = "guarded"
UNREADABLE = "?"

# Call names that consume a path. ⚑ `append` IS DELIBERATELY ABSENT — see the header.
PATH_CALLS = frozenset(
    {
        "join",
        "open",
        "exists",
        "isdir",
        "isfile",
        "walk",
        "listdir",
        "relpath",
        "abspath",
        "read_text",
        "glob",
        "iglob",
    }
)

# Call names that insert into a search path, admitted only under a `path` receiver.
PATH_INSERTS = frozenset({"insert", "append"})
PATH_RECEIVER = "path"

# Assignment-target fragments that mark a value as path-like.
PATH_TARGETS = ("PATH", "DIR", "ROOT", "HOME", "SCRATCH", "FILE")

# The scopes whose span makes a reference GUARDED rather than HARD.
_GUARD_SCOPES = (ast.Try, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

# The scopes whose leading string constant is a docstring.
_DOC_SCOPES = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

# How much of a hit's text to carry, so one long literal cannot bury a report.
SNIPPET = 70


@dataclass(frozen=True, slots=True)
class Hit:
    """One live reference: where, what kind, and a bounded slice of the text."""

    lineno: int
    kind: str
    snippet: str


@dataclass(frozen=True, slots=True)
class Scan:
    """What `scan_file` found, and what it could not read.

    ⚑ AN UNPARSEABLE FILE IS A WARNING CARRIED, NEVER A SILENT ZERO. A file that could not be
    scanned has an unknown number of references, and reporting none would be the census-green
    failure: a fact about the reader banked as a fact about the file.
    """

    hits: tuple[Hit, ...]
    warns: tuple[str, ...]


def _parse(path: Path) -> ast.Module | None:
    """Return the file's AST, or None when it cannot be read or parsed."""
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None


def _string_constant(node: ast.AST) -> ast.Constant | None:
    """Return `node` narrowed to a string Constant, or None — keeping the NODE, not its text."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node
    return None


def _text_of(node: ast.AST) -> str | None:
    """Return a string constant's text, or None for anything else."""
    found = _string_constant(node)
    if found is None:
        return None
    return str(found.value)


def _mentions(node: ast.AST) -> bool:
    """Report whether `node` is a string constant containing the needle."""
    text = _text_of(node)
    return text is not None and NEEDLE in text


def _name_of(node: ast.AST) -> str | None:
    """Return the bare name a Name or Attribute node carries, narrowed at the seam."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _import_names(node: ast.Import | ast.ImportFrom) -> list[str]:
    """Return every name an import statement binds or imports from."""
    names = [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom) and node.module:
        names.append(node.module)
    return names


def _names_needle(node: ast.Import | ast.ImportFrom) -> bool:
    """Report whether an import statement names the `scratch` PACKAGE — a top-level segment.

    ⚑⚑ NARROWED FROM A SUBSTRING TEST, BY RULING (gate-G396). The origin asked `"scratch" in
    name`, and the first scan of `substrate/` — a tree the origin could never see — reported
    `from substrate import scratch_module`, `scratch_refs`, even `check_scratch_independence`
    as RUNTIME couplings on `scratch/`. A module whose NAME contains the word is not the
    package at the repo root; an import is a dependency on `scratch/` exactly when the first
    dotted segment of what it imports, or of the module it imports from, is `scratch`.
    """
    return any(name.split(".")[0] == NEEDLE for name in _import_names(node))


def docstring_ids(tree: ast.Module) -> frozenset[int]:
    """Return the ids of the Constant nodes that are docstrings — exempt as prose.

    ⚑ A DOCSTRING IS THE FIRST STATEMENT OF A MODULE, DEF OR CLASS, and only that. A string
    constant anywhere else — a message, a path — is not prose by position and is not exempted.
    """
    found: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, _DOC_SCOPES):
            continue
        body = node.body
        if body and isinstance(body[0], ast.Expr) and _string_constant(body[0].value) is not None:
            found.add(id(body[0].value))
    return frozenset(found)


def scan_file(path: Path) -> Scan:
    """Return every LIVE reference in a file — the gate's own predicate, unchanged.

    ⚑ WIDE ON PURPOSE. This is the verdict the gate refuses on, and narrowing it here would
    change that verdict silently. `dependency_sites` is the narrow reading, kept beside it.
    """
    tree = _parse(path)
    if tree is None:
        return Scan((), (f"{path}: could not parse or read; not scanned",))
    exempt = docstring_ids(tree)
    hits: list[Hit] = []
    for node in ast.walk(tree):
        constant = _string_constant(node)
        if constant is not None:
            text = str(constant.value)
            if NEEDLE in text and id(constant) not in exempt:
                hits.append(Hit(constant.lineno, PATH_STRING, text.strip()[:SNIPPET]))
        elif isinstance(node, (ast.Import, ast.ImportFrom)) and _names_needle(node):
            hits.append(Hit(node.lineno, IMPORT, ",".join(_import_names(node))))
    return Scan(tuple(hits), ())


def _call_is_path_shaped(call: ast.Call) -> bool:
    """Report whether a call consumes a path, or inserts into one under a `path` receiver."""
    name = _name_of(call.func)
    if name is None:
        return False
    if name in PATH_CALLS:
        return True
    if name not in PATH_INSERTS or not isinstance(call.func, ast.Attribute):
        return False
    return _name_of(call.func.value) == PATH_RECEIVER


def _direct_arg_mentions(call: ast.Call) -> bool:
    """Report whether a DIRECT argument mentions the needle — never a deeper descendant.

    ⚑ THE ARGUMENT MUST BE THE STRING ITSELF, or a literal one level inside a BinOp/JoinedStr.
    Walking deeper reached into an f-string's interpolated call and credited the whole node.
    """
    for arg in call.args:
        if _mentions(arg):
            return True
        if isinstance(arg, (ast.BinOp, ast.JoinedStr)) and any(
            _mentions(child) for child in ast.iter_child_nodes(arg)
        ):
            return True
    return False


def _assign_is_path_shaped(node: ast.Assign) -> bool:
    """Report whether an assignment's target looks like a path or path constant."""
    if not node.targets:
        return False
    name = _name_of(node.targets[0])
    if name is None:
        return False
    upper = name.upper()
    return any(fragment in upper for fragment in PATH_TARGETS)


def dependency_sites(path: Path) -> frozenset[int]:
    """Return the line numbers where a scratch reference is USED AS A PATH, plus every import.

    ⚑ THE NARROW READING, kept beside the wide one. An import naming scratch is a dependency,
    full stop. A string is a dependency only when it feeds a path-shaped call or a path-shaped
    assignment — a diagnostic that merely says the word is a MENTION, reported separately.
    """
    tree = _parse(path)
    if tree is None:
        return frozenset()
    sites: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if _names_needle(node):
                sites.add(node.lineno)
        elif isinstance(node, ast.Call):
            if _call_is_path_shaped(node) and _direct_arg_mentions(node):
                sites.add(node.lineno)
        elif (
            isinstance(node, ast.Assign)
            and _assign_is_path_shaped(node)
            and any(_mentions(child) for child in ast.walk(node.value))
        ):
            sites.add(node.lineno)
    return frozenset(sites)


def guard_depth(path: Path, lineno: int) -> str:
    """Return HARD, GUARDED, or UNREADABLE for the reference at `lineno`.

    ⚑ HARD is module level — the file cannot be imported without scratch/. GUARDED is inside a
    try/def/class — the reference degrades rather than aborting. NEVER `fine`: a guard whose
    fallback always fails is guarded and still does nothing (⟡inert-guard).
    """
    tree = _parse(path)
    if tree is None:
        return UNREADABLE
    for node in ast.walk(tree):
        if not isinstance(node, _GUARD_SCOPES):
            continue
        end = node.end_lineno
        if end is not None and node.lineno <= lineno <= end:
            return GUARDED
    return HARD


def mentions(path: Path) -> frozenset[int]:
    """Return the lines `scan_file` flags that `dependency_sites` does NOT — the residue.

    ⚑ COMPUTED, NOT RE-DERIVED BY THE CALLER. `--scope` needs both halves and the origin had
    each caller subtract by hand; the difference is one reader's answer and belongs here.
    """
    wide = {hit.lineno for hit in scan_file(path).hits}
    return frozenset(wide - dependency_sites(path))
