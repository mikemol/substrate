#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Does a file's LOCAL import closure reach a store-bearing module, and by what route.

⚑⚑⚑ AST, NEVER IMPORT. Several files in this corpus execute at import time — one rewrites files
from module scope — so a reach census that imported them to read `__dict__` would fire exactly
what the suite runner exists to avoid, ninety-nine times, in-process. Names are read from the
syntax tree and never resolved.

⚑⚑⚑ MODULE-LEVEL ONLY BY DEFAULT, AND THAT CORRECTS A MEASURED FALSE POSITIVE. A first cut walked
every `Import` node via `ast.walk`, including function-local ones, and reported **54 of 99** suites
as store-reaching. The routes were the tell: an Agda lexer and a text gate both "reached" a store
through a ten-hop chain ending in a LAZY, cached, exception-swallowed `import store` inside a
function only the EXPLAIN modes call. Importing those modules never executes it.

⚑⚑ A DEFERRED IMPORT IS A DIFFERENT EDGE, AND COLLAPSING THEM ANSWERS THE WRONG QUESTION — the
import GRAPH where the question was about what RUNS. 54 rows of debt that mostly cannot abort is
not a conservative over-report; it is a census nobody can act on, and the first thing it teaches a
reader is to ignore it.

⚑⚑⚑ SO THE TWO READINGS ARE A PARAMETER, NOT A REPLACEMENT. `through_cuts=False` answers *what
does importing this execute*; True also follows deferred seed imports and marks each such hop `~`,
answering *what could this reach if the code runs*. A boolean that silently answers two questions
is the collapse this family records against its own verdict column; keeping both askable and
making the caller say which is the honest form.

⚑⚑ AND A DEFERRED SEED IMPORT IS A CUT IN THE GRAPH, NOT A PROPERTY OF ONE FILE. One instance hid
four suites: a module imported `store` inside a function, so the module-level lens correctly
excluded it — and reach then stopped one hop short, reporting three further suites as reaching NO
store while every one of them did, through that file. Hoisting a single import moved the census
from `0 OWED / 1 STRAY` to `3 OWED / 0 STRAY`. ⚑ A deferred import can be exactly right (an
optional backend, a heavy module one mode needs); what it always is, is a place the census cannot
see past.

⚑ `via` IS RETURNED, NEVER JUST THE BOOLEAN. A bare True cannot be acted on: the reader needs to
know WHICH seed and by what route, because the fix differs — declare a tenant, versus stop
importing a store from a pure analysis tool. A predicate answering yes/no makes the next question
un-askable.

⚑⚑ WHAT THIS CANNOT SEE, STATED RATHER THAN LEFT TO BE DISCOVERED. A tool reaching a store WITHOUT
importing one of the seeds — a raw `psycopg.connect`, or an inlined
`sandbox_connect(...) if sandbox else connect(...)` — is INVISIBLE here. That is measured, not
hypothetical: one query tool's tenant was UNSAYABLE because it declared `--sandbox` and never
`--live`, and every existing probe missed it. **An import-closure census reports the boundary of
the IMPORT GRAPH; it must not be read as reporting the boundary of store ACCESS.**

⚑⚑⚑ EXTRACTED FROM `scripts/run_selftests.py` (1,832 findings) BECAUSE THE DEPENDENCY RAN
BACKWARDS. `store_reach` was DEFINED in that monolith and IMPORTED by three clean `substrate/`
modules — `tenant_census`, `census_show`, and its suite — so gate-clean code depended on a
definition inside a file no edit can touch. ⚑ And the monolith cannot be edited to remove its copy
either: a deletion is an edit, and an edit to a file with findings is refused. It is frozen until
it can be deleted whole.
"""

from __future__ import annotations

import ast
from pathlib import Path  # noqa: TC003 — runtime use in `module_index`
from typing import TYPE_CHECKING, NamedTuple

from substrate import corpus

if TYPE_CHECKING:
    from collections.abc import Iterable

# ⚑⚑⚑ THE STORE-BEARING MODULES, AS SEEDS RATHER THAN AS AN ANSWER. A file reaches a store iff
# its local import closure reaches one of these. Naming the SEEDS — not the reaching files — is
# what keeps this from being a hand-maintained roster: a module that starts importing `store`
# tomorrow joins the population without editing here.
#
# ⚑ `store` IS THE ONLY TRUE SEED; the rest are its established front doors. They are listed
# because reach is computed over LOCAL modules only, and a file importing `schema_diag` gets
# there through modules this walk must also cross. Deriving the set from "whatever imports store"
# would make the seed set a function of the answer.
STORE_SEEDS = (
    "store",
    "schema",
    "schema_rows",
    "schema_decl",
    "schema_diag",
    "schema_queue",
    "query_defs",
    "query_builders",
    "query_registry",
    "query_decl",
    "catalog_db",
)

# Where local modules live, and what a walk never descends into.
DIRS = ("scripts", "scratch", "substrate", "jea/metalanguage", "tests")
SKIP_DIRS = frozenset({".git", ".venv", "__pycache__", "_build", "node_modules"})

# How a deferred hop is marked in a route.
DEFERRED_MARK = "~"


class Reach(NamedTuple):
    """Whether a file reaches a store, and the route that got there."""

    reaches: bool
    via: tuple[str, ...]

    @property
    def through_cut(self) -> bool:
        """Report whether the route crosses a DEFERRED import — reachable only if the code runs.

        ⚑ THE MARK CARRIES INTO EVERY READER FOR FREE. A route reading `scope_fix→~store` says
        both that the file reaches a store and that the last hop is conditional — the
        adjudication a reader previously had to do by hand, once, per row.
        """
        return any(hop.startswith(DEFERRED_MARK) for hop in self.via)


def _parsed(path: Path) -> ast.Module | None:
    """Return the syntax tree of `path`, or None when it cannot be read or parsed."""
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError):
        return None


def _imported_names(node: ast.stmt) -> tuple[str, ...]:
    """Return the top-level module names one import statement binds."""
    if isinstance(node, ast.Import):
        return tuple(alias.name.split(".")[0] for alias in node.names)
    if isinstance(node, ast.ImportFrom) and not node.level and node.module:
        return (node.module.split(".")[0],)
    return ()


def _nested_bodies(node: ast.stmt) -> tuple[list[ast.stmt], ...]:
    """Return the statement lists of `node` that still execute on import.

    ⚑⚑⚑ `match` ON THE TYPE, SO THE NARROWING IS THE LANGUAGE'S RATHER THAN THE AUTHOR'S. This
    is the fourth form of one repair, and each earlier form was wrong in a way the next exposed:

        1. `getattr(node, "orelse", None)`   erasure — `Any` at every access, and the reflex
                                             this session recorded three times
        2. an `isinstance` chain             field-probing WITH A GUARD IN FRONT. The union stays
                                             wider than the attribute set, so the narrowing is
                                             the author's CLAIM: reading `node.orelse` off a
                                             seven-member union was refused because `With` and
                                             `AsyncWith` do not have one
        3. `@functools.singledispatch`       REFUSED HERE, and MEASURED rather than inferred —
                                             `disallow_any_expr` rejects the decorator's own type
                                             expression (`Callable[..., _T]`), independently of
                                             mypy's functools plugin, which does retain the
                                             parameter signature
        4. `match` / `case ast.If()`         the checker narrows each arm to the matched class
                                             and enforces the fields that class declares

    ⚑⚑ A CLASS PATTERN IS NOT A PRETTIER `isinstance`. Inside `case ast.Try():` the binding IS an
    `ast.Try`, so `finalbody` and `handlers` are readable because a `Try` HAS them — not because
    a guard was written correctly above. A new node kind cannot be folded into an existing arm
    without the checker objecting to the fields that arm reads.

    ⚑ THE FALLTHROUGH IS THE HONEST DEFAULT: a statement with no nested body has no imports to
    find, so it contributes nothing rather than being an unhandled case.
    """
    match node:
        case ast.Try():
            return (
                node.body,
                node.orelse,
                node.finalbody,
                *[handler.body for handler in node.handlers],
            )
        case ast.With() | ast.AsyncWith():
            return (node.body,)
        case ast.If() | ast.For() | ast.AsyncFor() | ast.While():
            return (node.body, node.orelse)
        case _:
            return ()


def _module_level(body: Iterable[ast.stmt], out: set[str]) -> None:
    """Collect imports that fire on IMPORT, descending into compound statements only.

    ⚑ THE MODULE BODY, NOT `ast.walk`. A `for`/`if`/`try` at module scope still executes on
    import, so the walk descends into statement bodies — but never into a function or class,
    whose imports fire only when called.
    """
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        out.update(_imported_names(node))
        for nested in _nested_bodies(node):
            _module_level(nested, out)


def local_imports(path: Path) -> frozenset[str]:
    """Return the MODULE-LEVEL module names `path` imports — names only, never resolved."""
    tree = _parsed(path)
    if tree is None:
        return frozenset()
    found: set[str] = set()
    _module_level(tree.body, found)
    return frozenset(found)


def deferred_seed_imports(path: Path, seeds: tuple[str, ...] = STORE_SEEDS) -> frozenset[str]:
    """Return store seeds this file imports from INSIDE a function — the cuts in the graph.

    ⚑ ONLY WHAT THE TOP LEVEL DOES NOT ALREADY IMPORT. A module importing a seed at both scopes
    is already visible to the reach lens; listing it would be noise in a census whose whole value
    is that every row needs adjudicating.
    """
    tree = _parsed(path)
    if tree is None:
        return frozenset()
    top = local_imports(path)
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for inner in ast.walk(node):
            if isinstance(inner, (ast.Import, ast.ImportFrom)):
                found |= {
                    name for name in _imported_names(inner) if name in seeds and name not in top
                }
    return frozenset(found)


def module_index(root: Path | None = None) -> dict[str, Path]:
    """Return `{module_name: path}` for every local `.py` — the walk's resolution table.

    ⚑ FLAT BY BASENAME, BECAUSE THAT IS HOW THESE FILES IMPORT EACH OTHER. A tool says
    `import store`, not `import jea.metalanguage.store`; the directories are inserted on
    `sys.path` at runtime. A package-qualified index would resolve NOTHING and report every file
    as store-free — a false ZERO, which is the direction this repo banks silently.
    """
    base_root = root if root is not None else corpus.ROOT
    index: dict[str, Path] = {}
    for directory in DIRS:
        base = base_root / directory
        if not base.is_dir():
            continue
        for found in sorted(base.rglob("*.py")):
            if SKIP_DIRS & set(found.parts):
                continue
            index.setdefault(found.stem, found)
    return index


def store_reach(
    path: Path,
    index: dict[str, Path] | None = None,
    seeds: tuple[str, ...] = STORE_SEEDS,
    *,
    through_cuts: bool = False,
) -> Reach:
    """Return whether `path`'s local import closure reaches a store, and by what route.

    ⚑ TRANSITIVE, BECAUSE THE INCIDENT WAS. One tool reaches the store through its own imports;
    a direct-import test would have caught that, but another reaches it through a schema shim and
    a degree-1 census reports those as clean. Under-admitting means a suite that WILL abort is
    certified as not needing a tenant — the worse direction every time.
    """
    table = module_index() if index is None else index
    seen: set[Path] = set()
    frontier: list[tuple[Path, tuple[str, ...]]] = [(path, ())]
    while frontier:
        current, route = frontier.pop()
        if current in seen:
            continue
        seen.add(current)
        deferred = deferred_seed_imports(current, seeds) if through_cuts else frozenset()
        for name in sorted(local_imports(current) | deferred):
            mark = DEFERRED_MARK if name in deferred else ""
            if name in seeds:
                return Reach(reaches=True, via=(*route, mark + name))
            nxt = table.get(name)
            if nxt is not None and nxt not in seen:
                frontier.append((nxt, (*route, mark + name)))
    return Reach(reaches=False, via=())
