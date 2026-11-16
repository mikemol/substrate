#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Import one ad-hoc tool from `scratch/`, and say WHY when it will not import.

⚑⚑⚑ THE REASON IS RETURNED, NOT SWALLOWED. A caller that gets a bare `None` has to re-derive
the import by hand to learn anything, which is the reasoning-not-codified shape this repo
refuses. A refusal that cannot say what it hit is a guard degraded to measuring nothing.

⚑⚑ AND IT CATCHES `BaseException`, DELIBERATELY, WHICH IS NORMALLY WRONG. A tool may
`SystemExit` at import time — several in this tree refuse an unstated tenant or an unknown flag
that way — and `SystemExit` does not derive from `Exception`. Catching only `Exception` would
let a tool's own refusal terminate the reader trying to report it.

⚑⚑ LOADING IS BY LOCATION, NOT BY PATH MUTATION. `scratch/` is a directory of scripts rather
than a package, so `import_module("vfs")` raises unless the caller has already arranged the
path. `spec_from_file_location` names the location directly, so the resolution is local to this
call and cannot leak into an unrelated import elsewhere in the run.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import TYPE_CHECKING

from substrate import corpus, sibling_finder

if TYPE_CHECKING:
    from types import ModuleType

# Where the ad-hoc tools live. ⚑ NAMED ONCE, for the same reason `GATE_DIR` is.
SCRATCH_DIR = "scratch"


def tool_path(name: str) -> str:
    """Return the repo-relative path a tool name resolves to."""
    return f"{SCRATCH_DIR}/{name.removesuffix('.py')}.py"


# ⚑⚑⚑ THE PRIVATE FINDER THAT SAT HERE IS GONE, AND ITS REASONING MOVED WITH IT to
# `substrate.sibling_finder`. It resolved a bare sibling name to its file in the tool directory
# — the capability a tool needs because registering the tool under its own stem lets it find
# ITSELF mid-import and does nothing for a tool importing a DIFFERENT sibling (MEASURED:
# `bibstruct` does `import vfs` at module scope, and five tools reach `vfs` that way).
#
# ⚑⚑ TWO IMPLEMENTATIONS OF ONE CAPABILITY IS THE SHAPE THIS REPO RETIRES EVERYWHERE ELSE, and
# `gate_module` already used the shared one for the same job over `scripts/`. Keeping a private
# copy here meant a fix to either could leave the other behind — the `agda_files()`-had-four-
# bodies defect, one directory over.
#
# ⚑ THE CONTEXT MANAGER ALSO REPLACES A HAND-ROLLED `append`/`remove` PAIR whose removal lived
# in a `finally`. That is the same contract expressed once, in a module whose own cases pin the
# removal on the FAILURE path — where a forgotten `finally` hides.


def scratch_module(name: str) -> tuple[ModuleType | None, str | None]:
    """Return `(module, None)` or `(None, why)` for one scratch tool by name.

    ⚑ AN ALREADY-LOADED TOOL IS RETURNED AS-IS, so a second caller does not execute a second copy
    under the same name — two module objects for one tool, differing only in which one holds the
    state a later reader looks at.
    """
    stem = name.removesuffix(".py")
    if stem in sys.modules:
        return sys.modules[stem], None

    path = corpus.ROOT / tool_path(name)
    if not path.exists():
        return None, f"no tool at {tool_path(name)}"

    spec = importlib.util.spec_from_file_location(stem, str(path))
    if spec is None or spec.loader is None:
        return None, f"{tool_path(name)} is not loadable as a module"

    module = importlib.util.module_from_spec(spec)
    # ⚑ REGISTERED BEFORE EXECUTION: a tool importing its own siblings by bare name needs to find
    # itself in `sys.modules` mid-import. The registration is undone on failure, so a
    # half-executed module is never left for the next caller to find and trust.
    sys.modules[stem] = module
    try:
        # ⚑ THE FINDER IS SCOPED TO THIS LOAD. It answers only for bare names with a file in
        # the tool directory and is removed when the block returns — including on the failure
        # path, so a failed load cannot leave the interpreter resolving bare names against a
        # directory nobody asked about.
        with sibling_finder.siblings_of(corpus.ROOT / SCRATCH_DIR):
            spec.loader.exec_module(module)
    except BaseException as exc:  # noqa: BLE001 — a tool may SystemExit at import
        sys.modules.pop(stem, None)
        return None, f"{type(exc).__name__}: {exc}"
    return module, None
