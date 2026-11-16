#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Outline a python module: every top-level def/class with its span and summary.

⚑ THE DEFECT THIS PREVENTS: *deciding what a file HOLDS by reading it*. A 1,819-line
module cannot be censused by eye, and the judgement "what are its concerns" then happens
in a turn instead of in a program — it evaporates, and the next reader re-derives it
differently. `pycodemod` answers about a NAME you already know (`--source`, `--calls`);
nothing answered *what names are in this file, and how big is each*. That gap is exactly
why an n-split plan gets written from a skim.

⚑ SPAN, NOT JUST NAME. The size of a def is what makes it leaf-most or not: a promotion
plan ranks by lines-carried and by how few module-level names a body reads. A bare name
list cannot rank, so it produces a plan that cannot say which part to cut first.

⚑ NESTED DEFS ARE NOT OUTLINE ENTRIES. A closure inside a function is part of that
function's body, and listing it as a peer would double-count its lines and invent a
promotion candidate that cannot be promoted alone. Only module-level statements are
reported — the level a split can actually cut at.

⚑⚑ AND ITS OWN CORRECTNESS IS TRUSTED RATHER THAN CHECKED, WHICH IS WHY IT HAS A SUITE
(`module_outline_selftest`). This is the tool a reader consults INSTEAD of opening the
callee, so a wrong outline cannot be caught by its consumer: they call a name that does
not exist and attribute the miss to the callee. It shipped with no cases at all while
being the standing answer to "what is that module's surface".
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from substrate import ratchet_flags

Definition = ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef


class OutlineEntry:
    """Hold one module-level definition: its kind, name, line span and summary line."""

    def __init__(self, kind: str, name: str, lineno: int, end_lineno: int, summary: str) -> None:
        """Record the fields verbatim; no derivation, so a test can build one by hand."""
        self.kind = kind
        self.name = name
        self.lineno = lineno
        self.end_lineno = end_lineno
        self.summary = summary

    @property
    def lines(self) -> int:
        """Report how many source lines this definition spans, inclusive of both ends."""
        return self.end_lineno - self.lineno + 1

    def __repr__(self) -> str:
        """Render a stable one line, used by the CLI and readable inside a failure."""
        return f"{self.lineno:5d} {self.lines:5d}  {self.kind:5s} {self.name}"


def _summary(node: Definition) -> str:
    """Take the first line of the docstring, or the empty string when there is none."""
    doc = ast.get_docstring(node)
    if not doc:
        return ""
    return doc.split("\n")[0].strip()


def _bound_names(target: ast.expr) -> list[str]:
    """List the names one assignment target binds, descending into tuple/list targets.

    ⚑ RECURSIVE BECAUSE NESTING IS LEGAL: `A, (B, C) = ...` is one target binding three
    names, and a single-level unwrap would report two of them — a partial census is worse
    than none, because it looks complete.
    """
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        return [name for element in target.elts for name in _bound_names(element)]
    return []


def outline(source: str) -> list[OutlineEntry]:
    """List every module-level def/class in `source`, in source order.

    ⚑ Parses rather than scanning for `^def `: a `def` inside a triple-quoted string is
    not a definition, and a decorated def's span must start at the `def` line so the
    reported sizes sum to something meaningful.

    ⚑ AN UNPARSEABLE SOURCE RAISES; it does not render as an empty module. `[]` means
    "defines nothing" and a `SyntaxError` means "this instrument could not read it" —
    opposite facts, and collapsing the second into the first reports the boundary of the
    METHOD as a fact about the substrate.
    """
    tree = ast.parse(source)
    out: list[OutlineEntry] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            kind = "class"
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            kind = "def"
        else:
            continue
        end = node.end_lineno if node.end_lineno is not None else node.lineno
        out.append(OutlineEntry(kind, node.name, node.lineno, end, _summary(node)))
    return out


def module_constants(source: str) -> list[str]:
    """List the module-level names bound by assignment — the memo tables and config.

    ⚑ THESE TRAVEL WITH THEIR READERS OR THEY BECOME ORPHANS. A split that moves a
    function and leaves the table it consults behind produces a module that imports back
    into the file it was cut from — the import edge a promotion was meant to CUT.

    ⚑⚑ A TUPLE TARGET BINDS EVERY NAME IN IT, and this dropped all of them until the suite
    was written: `A, B = 4, 5` has one `ast.Tuple` target, which the `isinstance(t, Name)`
    filter discarded silently. A module using the paired-constants idiom therefore reported
    FEWER constants than it has, and a promotion planned from that census strands exactly
    the names it could not see — a census zero reporting the method's boundary as the
    substrate's, in the tool whose whole job is answering what a file holds.
    """
    tree = ast.parse(source)
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                names.extend(_bound_names(target))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.append(node.target.id)
    return names


def outline_path(path: Path) -> list[OutlineEntry]:
    """Read `path` and outline it, so callers need not repeat the decode."""
    return outline(path.read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    """Print the outline of each named file, followed by its module constants.

    ⚑⚑ A FLAG IS REFUSED, NEVER OPENED AS A PATH. Measured: `--selftest` — the flag every
    other tool in this package answers — was handed straight to `Path.read_text` and
    crashed with a file-not-found, which reads as "that file is missing" rather than "this
    tool has no such mode". A discarded operand is indistinguishable from an honoured one;
    this is the third operand-discard measured in this package, so it refuses rather than
    guessing what was meant.
    """
    rc = ratchet_flags.check_argv(argv, (), "module_outline")
    if rc is not None:
        return rc
    if not argv:
        sys.stderr.write("usage: python3 -m substrate.module_outline <file.py> [...]\n")
        return 2
    for arg in argv:
        path = Path(arg)
        text = path.read_text(encoding="utf-8")
        entries = outline(text)
        consts = module_constants(text)
        sys.stdout.write(f"{path}: {len(entries)} definition(s), {len(consts)} constant(s)\n")
        for entry in entries:
            sys.stdout.write(f"{entry!r}  {entry.summary[:70]}\n")
        if consts:
            sys.stdout.write("  constants: " + ", ".join(consts) + "\n")
    return 0


# ⚑⚑ THE Ⓝ86 RETIREMENT IS ABOUT WHERE THE SLICE IS DECIDED, AND THE NAIVE READING IS WORSE
# THAN THE DEFECT. Handing `main` the whole `sys.argv` satisfies `ratchet_flags` — `_rest`
# tolerates a full vector or a pre-sliced one — but the OPERAND loop does not, so `main(sys.argv)`
# outlined the tool's OWN path as an extra file. MEASURED here while making this edit: it
# reported `module_outline.py` beside the requested file, and the output read as a legitimate
# result. Two consumers of one vector disagreeing about what an operand is, which is the same
# shape as the discarded-operand defect this file was opened to fix.
#
# ⚑ AND THE SUITE IS IMPORTED IN THIS BLOCK, NOT IN A FUNCTION BODY. It imports this module, so
# a top-level import is circular; `PLC0415` (Ⓝ97) forbids the in-function form. The module-scope
# guard is neither, and is the one place both constraints hold.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import module_outline_selftest

        sys.exit(module_outline_selftest.selftest())
    sys.exit(main(sys.argv[1:]))
