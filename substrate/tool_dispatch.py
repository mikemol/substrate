#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""What a tool ACCEPTS — the flags its code can branch on, read from the AST.

⚑⚑⚑ NOT A MODE CLAIM — WHAT A DISPATCH COULD POSSIBLY REACH. A tool's self-description is the
authority for what it SAYS it does; this is the authority for what it DOES. The gap between them
is the only structural way to see a mode a self-description omits, and for `agda_lex` — whose
bare output is its selftest — it is the only signal at all.

⚑⚑ A FLAG A TOOL *PASSES* IS NOT A FLAG IT *ACCEPTS*, and a false positive here is a bug rather
than a caveat. Reading every flag-shaped literal as a mode credited `pycodemod` with mypy's
`--ignore-missing-imports`, `mdstruct` with git's `--porcelain`, and `agda_defs` with the Agda
pragma `--without-K` it SEARCHES FOR: 55 "undocumented modes", most of them another program's
vocabulary quoted inside a subprocess argument list.

⚑ SO THE DISCRIMINATOR IS ANCHORING TO THE ARGUMENT VECTOR. A flag is ACCEPTED when it is
compared against argv, registered with `add_argument`, declared to this repo's `check_argv`
guard, or used as a key in an all-flag dispatch table. Everything else is reported separately:
present in the source, but not this tool's vocabulary.

⚑⚑ AND THE ANCHOR IS THE VECTOR, NOT THE SPELLING `sys.argv` — which took the census being run
against its own tool to notice. Every tool in the corpus dispatches as `if "--x" in sys.argv`, so
a literal test for that expression looked total until it met one doing `args = argv[1:]` then
`flag = args[0]` then `flag == "--find"`. `--find` came back UNBACKED. A detector that sees one
idiom reports a different idiom as a missing capability. The alias walk is a FIXPOINT rather than
one pass, because the chain has length and a single sweep in source order catches only its first
link.

⚑⚑⚑ THE IMPORT HOP IS ONE LEVEL AND HAS THREE GUARDS, EACH A MEASURED WRONG ATTRIBUTION. The big
tools are DECOMPOSED — `pycodemod.py` dispatches out of `_pycodemod_query.py` — so reading only
the entry module reports nearly every documented mode as unbacked. But hopping too far invents
modes on tools that reject them:

  * a PEER TOOL — `agda_lex` imports `agda_defs`, and the hop credited it with all twelve of that
    tool's modes. The roster is the discriminator: a module the routing table names is a tool in
    its own right and is censused separately.
  * a SHARED UTILITY THAT IS ALSO A CLI — `edit_snapshot.py` is imported by three tools for
    snapshot arming and has its own `--holding`/`--list` dispatch, so the hop reported those as
    three independent undocumented modes on three tools that accept neither (verified by running
    them: both fall through to the usage block, exit 2). The peer guard cannot see this, because
    it excludes only modules the routing table names.
  * ⚑ AND THE COST OF THE WRONG CALL IS ASYMMETRIC. Refusing a hop into a real implementation
    half under-reports that tool's modes — a gap someone can see. Taking one into a CLI module
    INVENTS modes, and a reader who "documents" one is documenting a flag its tool does not own.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers), 2,196 findings, refused whole by the
per-file gate. The cut continues until the dispatch moves out and the original is retired.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import tool_declaration, tool_population

if TYPE_CHECKING:
    from pathlib import Path

# How many times the alias walk re-runs looking for new bindings. ⚑ A FIXPOINT, NOT A SWEEP: the
# chain `argv → args → flag` has length, and one pass in source order catches only its first link.
ALIAS_PASSES = 4

# The functions that REGISTER a flag as accepted, rather than merely mentioning it.
REGISTRARS = frozenset({"add_argument", "check_argv"})


@dataclass(frozen=True, slots=True)
class Flags:
    """What a tool's source says about flags: the ones it accepts, and every one present."""

    accepted: frozenset[str]
    literals: frozenset[str]

    @property
    def passed_through(self) -> frozenset[str]:
        """Return flags present but not accepted — another program's vocabulary, quoted here."""
        return self.literals - self.accepted


def _flag_value(node: ast.AST) -> str | None:
    """Return a whole-flag string constant's value, or None."""
    text = None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        text = node.value
    return text if text is not None and tool_declaration.FLAG_EXACT.match(text) else None


def is_argv(node: ast.AST, alias: frozenset[str] = frozenset()) -> bool:
    """Report whether an expression resolves to the process argument vector."""
    if isinstance(node, ast.Attribute):
        return node.attr == "argv" or is_argv(node.value, alias)
    if isinstance(node, ast.Name):
        return "argv" in node.id.lower() or node.id in alias
    if isinstance(node, ast.Subscript):
        return is_argv(node.value, alias)
    return False


def argv_aliases(tree: ast.AST) -> frozenset[str]:
    """Return every name bound, transitively, from the argument vector.

    ⚑ THE FIXPOINT IS THE POINT. `args = argv[1:]` then `flag = args[0]` binds two names to the
    vector, and a reader that stopped at the first would treat `flag == "--find"` as a comparison
    against an unrelated string.
    """
    alias: set[str] = set()
    for _pass in range(ALIAS_PASSES):
        before = len(alias)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.value is None:
                continue
            if not any(is_argv(part, frozenset(alias)) for part in ast.walk(node.value)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                alias.update(sub.id for sub in ast.walk(target) if isinstance(sub, ast.Name))
        if len(alias) == before:
            break
    return frozenset(alias)


def _compared_to_argv(node: ast.Compare, alias: frozenset[str]) -> set[str]:
    """Return flags compared against the argument vector — the live dispatch shape."""
    sides: list[ast.expr] = [node.left, *node.comparators]
    if not any(is_argv(side, alias) for side in sides):
        return set()
    return {text for side in sides if (text := _flag_value(side)) is not None}


def _registered(node: ast.Call) -> set[str]:
    """Return flags a call REGISTERS: `add_argument`, or this repo's `check_argv` guard."""
    func = node.func
    name = (
        func.attr
        if isinstance(func, ast.Attribute)
        else func.id
        if isinstance(func, ast.Name)
        else ""
    )
    if name not in REGISTRARS:
        return set()

    out = {text for arg in node.args if (text := _flag_value(arg)) is not None}
    for arg in node.args:
        if isinstance(arg, (ast.Set, ast.List, ast.Tuple)):
            out.update(text for element in arg.elts if (text := _flag_value(element)) is not None)
    return out


def _dispatch_table(node: ast.Dict) -> set[str]:
    """Return the keys of a dict every one of whose keys is a flag."""
    if not node.keys:
        return set()
    keys: list[str] = []
    for key in node.keys:
        text = _flag_value(key) if key is not None else None
        if text is None:
            return set()
        keys.append(text)
    return set(keys)


def _implementation_halves(tree: ast.AST, home: Path, peers: frozenset[str]) -> list[Path]:
    """Return same-directory modules this file imports that are NOT tools in their own right.

    ⚑ TWO GUARDS, BOTH MEASURED. A module the routing table NAMES is a peer tool, censused
    separately; a module with its own ENTRY POINT is a shared utility that is also a CLI. Either
    hop attributes a neighbour's vocabulary to this tool.
    """
    out: list[Path] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        named = (
            [alias.name for alias in node.names]
            if isinstance(node, ast.Import)
            else [node.module or ""]
        )
        for module in named:
            base = module.split(".")[0] + ".py"
            candidate = home.parent / base
            if base in peers or not candidate.exists():
                continue
            if tool_population.has_entry_point(tool_population.read(candidate)):
                continue
            out.append(candidate)
    return out


def flags_of(path: Path, peers: frozenset[str] = frozenset()) -> Flags:
    """Return what a tool accepts and what its source merely mentions.

    ⚑ THE HOP IS ONE LEVEL FROM THE ENTRY MODULE ONLY. A transitive walk would reach the whole
    package, and depth is not what decomposition needs — `pycodemod` dispatches out of exactly one
    private sibling.
    """
    accepted: set[str] = set()
    literals: set[str] = set()
    seen: set[Path] = set()
    todo = [path]

    while todo:
        current = todo.pop()
        if current in seen or not current.exists():
            continue
        seen.add(current)
        try:
            tree = ast.parse(tool_population.read(current))
        except SyntaxError:
            continue

        alias = argv_aliases(tree)
        for node in ast.walk(tree):
            text = _flag_value(node)
            if text is not None:
                literals.add(text)
            if isinstance(node, ast.Compare):
                accepted.update(_compared_to_argv(node, alias))
            elif isinstance(node, ast.Call):
                accepted.update(_registered(node))
            elif isinstance(node, ast.Dict):
                accepted.update(_dispatch_table(node))

        if current == path:
            todo.extend(_implementation_halves(tree, current, peers))

    return Flags(accepted=frozenset(accepted), literals=frozenset(literals))
