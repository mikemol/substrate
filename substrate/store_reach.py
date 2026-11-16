#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Does a file's local import closure reach a store-bearing module, and by what route.

⚑⚑⚑ TWO READINGS, AS A PARAMETER RATHER THAN A REPLACEMENT. `through_cuts=False` answers
*what does importing this EXECUTE*; True also follows deferred seed imports and marks each such
hop `~`, answering *what could this reach if the code RUNS*. A boolean that answers two
questions is a collapse; keeping both askable and making the caller say which is the honest
move.

⚑⚑ THE NARROW READING IS THE DEFAULT BECAUSE THE WIDE ONE WAS MEASURED WRONG. Following cuts
unconditionally reported **54 of 99** suites as store-reaching, including an Agda LEXER and a
TEXT gate — both via a ten-hop chain ending in a lazy, exception-swallowed `import store` that
only the EXPLAIN modes call. 54 rows of debt that mostly cannot fire is not conservative
over-reporting; it is a census nobody can act on, and the first thing it teaches is to ignore
it.

⚑ TRANSITIVE, BECAUSE THE INCIDENT WAS. `schema.py` reaches the store through its own imports
and a direct-import test would catch it — but `sppf_drain` reaches it through `_schema`, and a
degree-1 census reports those as clean. Under-admitting certifies a suite that WILL abort as
not needing a tenant, which is the worse direction every time.

⚑ AND `via` IS RETURNED, NEVER JUST THE BOOLEAN. A bare True cannot be acted on: the reader
needs to know WHICH seed and by what route, because the fix differs — declare a tenant, versus
stop importing a store from a pure analysis tool. A predicate answering yes/no makes the next
question un-askable.

⚑⚑ WHAT IT CANNOT SEE, STATED RATHER THAN LEFT TO BE DISCOVERED. A tool that reaches a store
WITHOUT importing one of the seeds — a raw driver call, an inlined
`sandbox_connect(...) if ... else connect(...)` — is INVISIBLE here. Measured on `query_defs`,
whose tenant was unsayable and which every existing probe missed. **An import-closure census
reports the boundary of the import graph, never the boundary of store access.** `store_calls`
is the decorrelated second lens for exactly that gap.
"""

from __future__ import annotations

import os
from pathlib import Path

from mikemol.corpus import import_edges

# ⚑⚑⚑ THE STORE-BEARING MODULES, AS SEEDS RATHER THAN AS AN ANSWER. A suite reaches a store iff
# its local import closure reaches one of these. Naming the SEEDS — not the reaching files — is
# what keeps this from being a hand-maintained roster: a module that starts importing `store`
# tomorrow joins the population without editing here.
#
# ⚑ `store` IS THE ONLY TRUE SEED; the rest are its established front doors, listed because
# reach is computed over LOCAL modules only and a suite reaching `schema_diag` gets there
# through modules this walk must also cross. Deriving the set from "whatever imports store"
# would make the seed set a function of the answer.
STORE_SEEDS = frozenset(
    {
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
    }
)

# Directories excluded from the module index — vendored noise and snapshot copies.
SKIP_DIRS = frozenset({".venv", "__pycache__", ".edit-snapshots", "node_modules", ".git"})


def module_index(root: Path, trees: tuple[str, ...]) -> dict[str, str]:
    """Return `{module_name: path}` for every local `.py` — the walk's resolution table.

    ⚑ FLAT BY BASENAME, BECAUSE THAT IS HOW THESE FILES IMPORT EACH OTHER. `sppf_db.py` says
    `import store`, not `import jea.metalanguage.store`; the tools insert each other's
    directories on `sys.path` at runtime. A package-qualified index would resolve NOTHING and
    report every suite as store-free — a false ZERO, the direction this repo banks silently.
    """
    idx: dict[str, str] = {}
    for tree in trees:
        base = root / tree
        if not base.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                if name.endswith(".py"):
                    idx.setdefault(name[:-3], str(Path(dirpath) / name))
    return idx


def eager_prefix(via: tuple[str, ...]) -> tuple[str, ...]:
    """Return the leading hops of a route that ALL execute on import.

    ⚑⚑⚑ THE PREFIX IS THE ANSWERABLE QUESTION, AND ASKING ABOUT THE WHOLE ROUTE WAS THE BUG.
    A route `('~query_defs',)` reaches a seed only if the deferred hop fires; anything found
    BEYOND that hop is conditional on it. Joining a call census against the whole route
    therefore credited openers past a `~` — measured, and it drove ruling agreement from 6/7
    DOWN to 3/7, with all four new disagreements sharing that shape.

    ⚑ SO EAGERNESS IS A PROPERTY OF THE PREFIX, NOT OF THE FINAL HOP. One `~` anywhere makes
    every later hop conditional, which is why this truncates rather than filters: the hops
    after a cut are not "less certain", they are unreached unless the cut fires.
    """
    out: list[str] = []
    for hop in via:
        if hop.startswith("~"):
            break
        out.append(hop)
    return tuple(out)


def reaches(
    path: str, index: dict[str, str], *, through_cuts: bool = False
) -> tuple[bool, tuple[str, ...]]:
    """Return `(reaches, via)` — does this file's import closure hit a store seed.

    ⚑⚑ DEFERRED EDGES ARE MARKED `~` IN THE ROUTE, NOT MERGED INTO IT. A module-level import
    fires on import; a deferred one fires only if the function runs. Marking instead of
    merging keeps both questions askable from ONE walk: an unmarked route is what importing
    executes, a `~` route is what it can reach if the code runs.

    ⚑⚑⚑ AND THE VISITED SET IS KEYED ON `(module, eager)`, NOT ON THE MODULE ALONE — which is
    a defect the first cut carried. A module first reached through a `~` hop was marked seen,
    so a LATER, fully-eager route to the same module was silently discarded and the walk
    reported the conditional route as if it were the only one. That understates what executes,
    which is the direction that certifies a suite as safe when it is not.
    """
    seen: set[tuple[str, bool]] = set()
    frontier: list[tuple[str, tuple[str, ...], bool]] = [(path, (), True)]
    while frontier:
        current, route, eager = frontier.pop()
        if (current, eager) in seen:
            continue
        seen.add((current, eager))
        lazy = import_edges.deferred(current) if through_cuts else frozenset()
        for name in sorted(import_edges.module_level(current) | lazy):
            deferred_hop = name in lazy
            mark = "~" if deferred_hop else ""
            if name in STORE_SEEDS:
                return (True, (*route, mark + name))
            nxt = index.get(name)
            still_eager = eager and not deferred_hop
            if nxt is not None and (nxt, still_eager) not in seen:
                frontier.append((nxt, (*route, mark + name), still_eager))
    return (False, ())
