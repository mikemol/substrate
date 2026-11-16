#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Load a `catalog/library/` module by name without putting its directory on the import path.

⚑⚑⚑ `catalog` IS UNPACKAGED BY DECISION, NOT BY OVERSIGHT. `pyproject.toml` declares
`packages = ["substrate", "scripts"]`, and its own comment says why `scratch` is absent —
*"residence there IS the not-yet-promoted status"*. The same holds here: the worklist library is
read BY the dispatch, not distributed with the tooling, so `from catalog.library import concepts`
raises `ModuleNotFoundError` — measured, in a suite that otherwise type-checked clean.

⚑⚑ AND NAMING IT WOULD HAVE BEEN THE WRONG REPAIR ANYWAY, for the reason that file states at
length: **type the callee, THEN name it.** Adding `catalog` to `packages` makes mypy follow the
edge, and the declarer then eats every finding in the followed module — paperkit measured one
suite going from 3 own findings to 231 when a single edge became followable. The injection is not
what creates the debt; it is what hides it.

⚑ SO THIS IS THE THIRD LOADER, AND THE FAMILY IS NOW COMPLETE: `gate_module` for `scripts/`,
`scratch_module` for `scratch/`, this for `catalog/library/`. One per unpackaged directory,
directory-specific by construction — reaching for the wrong one reports a present module as
absent, which is a diagnosis the refusal itself makes because it names the path it tried.

⚑ THE SIBLING FINDER IS REUSED, NOT REWRITTEN. `scratch_module` already resolves a bare sibling
import from a tool's own directory; the library's modules import from `substrate`, which is
packaged, so they need only the location load — and duplicating the finder to say so would be the
rival implementation this family keeps refusing.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from types import ModuleType

# Where the worklist library lives.
LIBRARY_DIR = "catalog/library"


def module_path(name: str) -> str:
    """Return the repo-relative path a library module name resolves to."""
    return f"{LIBRARY_DIR}/{name.removesuffix('.py')}.py"


def library_module(name: str) -> tuple[ModuleType | None, str | None]:
    """Return `(module, None)` or `(None, why)` for one library module by name.

    ⚑ AN ALREADY-LOADED MODULE IS RETURNED AS-IS, so a second caller does not execute a second
    copy under the same name — two module objects for one library, differing only in which one
    holds the state a later reader looks at.
    """
    stem = name.removesuffix(".py")
    if stem in sys.modules:
        return sys.modules[stem], None

    path = corpus.ROOT / module_path(name)
    if not path.exists():
        return None, f"no module at {module_path(name)}"

    spec = importlib.util.spec_from_file_location(stem, str(path))
    if spec is None or spec.loader is None:
        return None, f"{module_path(name)} is not loadable as a module"

    module = importlib.util.module_from_spec(spec)
    # ⚑ REGISTERED BEFORE EXECUTION: a module importing its own siblings by bare name needs to
    # find itself in `sys.modules` mid-import. The registration is undone on failure, so a
    # half-executed module is never left for the next caller to find and trust.
    sys.modules[stem] = module
    try:
        spec.loader.exec_module(module)
    except BaseException as exc:  # noqa: BLE001 — a module may SystemExit at import
        sys.modules.pop(stem, None)
        return None, f"{type(exc).__name__}: {exc}"
    return module, None


if __name__ == "__main__":
    _found, _why = library_module("concepts")
    sys.stdout.write(f"  concepts: {'loaded' if _found else _why}\n")
    sys.exit(0)
