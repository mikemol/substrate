#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Import one ratchet gate, and say WHY when it will not import.

⚑⚑⚑ THE REASON IS RETURNED, NOT SWALLOWED. A first cut caught the failure and returned a bare
`None`, so two gates reported `n/a` with no way to ask why — and the only route left to a reader
was a `python3 -c` re-deriving the import by hand, which is the reasoning-not-codified shape
this repo refuses. **A refusal that cannot say what it hit is a guard degraded to measuring
nothing.**

⚑⚑ AND IT CATCHES `BaseException`, DELIBERATELY, WHICH IS NORMALLY WRONG. A gate may `SystemExit`
at import time — several in this tree refuse an unstated tenant or an unknown flag that way — and
`SystemExit` does not derive from `Exception`. Catching only `Exception` would let a gate's own
refusal terminate the census that is trying to report it, so the process would die while
measuring rather than record an unmeasurable gate.

⚑⚑⚑ IT FALLS BACK TO LOADING BY LOCATION, AND A BARE `import_module` REPORTED SEVEN LIVE GATES AS
UNMEASURABLE. Gates live in `scripts/`, a directory of scripts rather than a package, so
`import_module("check_claims")` raises `ModuleNotFoundError` unless the caller has already
arranged the path. MEASURED: all seven present on disk, every one reporting `UNMEASURABLE — No
module named …`. **That is a fact about the INVOCATION reported as a fact about the gate**, and a
witness built on it banks a false finding across the whole family — worse in this direction, since
an unmeasurable census reads as *nothing to see* rather than as a defect anyone argues with.

⚑⚑ THE REPAIR IS NOT `sys.path`. Path mutation is refused here, and it would be the wrong fix
anyway: it makes an import work by rearranging global interpreter state instead of by saying where
the file is. `spec_from_file_location` names the location directly, so the resolution is local to
this call and cannot leak into an unrelated import elsewhere in the run.

⚑⚑⚑ AND REGISTERING THE GATE UNDER ITS OWN STEM WAS NECESSARY AND INSUFFICIENT. It lets a gate
find ITSELF mid-import and does nothing for a gate importing a DIFFERENT sibling by bare name —
which `scripts/` is full of. MEASURED: `check_public_ratchet` died with `ModuleNotFoundError: No
module named 'ratchet'` on a sibling sitting beside it, so the churn census reported that gate as
UNMEASURABLE when it was merely unreachable. `sibling_finder` closes that: a meta-path finder
scoped to the gate directory, installed for the length of the load and removed after, so the
resolution is an INPUT to this call rather than an ambient change.

⚑ ORDINARY RESOLUTION IS TRIED FIRST AND ITS FAILURE IS KEPT. The location lookup is a FALLBACK
for a package-less directory, never a replacement — and when it also fails, the reason returned is
the IMPORT's, not a claim about a directory the caller never mentioned.

⚑ EXTRACTED FROM `catalog/library/figures.py` (⟡items-n-split), which is dirty and cannot be
edited; every ratchet witness depends on this one function, so it is the first cut.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from typing import TYPE_CHECKING

from substrate import corpus, sibling_finder

if TYPE_CHECKING:
    from types import ModuleType

# Gates are named with or without the extension at different call sites; both resolve here so a
# caller never has to know which spelling the roster used.
_SUFFIX = ".py"

# Where gates live. ⚑ NAMED ONCE: a second spelling at a call site is how a loader starts
# disagreeing with the roster about what exists.
GATE_DIR = "scripts"


def gate_path(name: str) -> str:
    """Return the repo-relative path a gate name resolves to."""
    return f"{GATE_DIR}/{name.removesuffix(_SUFFIX)}{_SUFFIX}"


def _by_name(stem: str) -> tuple[ModuleType | None, str]:
    """Import by ordinary resolution, returning the failure reason rather than raising."""
    try:
        return importlib.import_module(stem), ""
    except BaseException as exc:  # noqa: BLE001 — a gate may SystemExit at import
        return None, f"{type(exc).__name__}: {exc}"


def _by_location(stem: str, path: str) -> tuple[ModuleType | None, str]:
    """Load a module from an explicit file path.

    ⚑ REGISTERED BEFORE EXECUTION, because a gate that imports its own siblings by bare name needs
    to find itself in `sys.modules` mid-import; a module executed without being registered
    re-enters and recurses. The registration is undone on failure so a half-executed module is
    never left behind for the next caller to find.

    ⚑⚑ AND THE SIBLING FINDER COVERS WHAT THAT REGISTRATION CANNOT: a gate importing a DIFFERENT
    bare-named sibling. It is scoped to the gate directory and removed when the load returns, so
    nothing about this call survives into an unrelated import later in the process.
    """
    spec = importlib.util.spec_from_file_location(stem, path)
    if spec is None or spec.loader is None:
        return None, f"{path} is not loadable as a module"

    module = importlib.util.module_from_spec(spec)
    sys.modules[stem] = module
    try:
        with sibling_finder.siblings_of(corpus.ROOT / GATE_DIR):
            spec.loader.exec_module(module)
    except BaseException as exc:  # noqa: BLE001 — a gate may SystemExit at import
        sys.modules.pop(stem, None)
        return None, f"{type(exc).__name__}: {exc}"
    return module, ""


def gate_module(name: str) -> tuple[ModuleType | None, str | None]:
    """Return `(module, None)` or `(None, why)` for one gate by name.

    ⚑ AN ALREADY-IMPORTED GATE IS RETURNED AS-IS. Loading a second copy under the same name would
    give a census one module object while the gate's own state lived in another — two authorities
    for one gate, differing only under concurrency.
    """
    stem = name.removesuffix(_SUFFIX)
    if stem in sys.modules:
        return sys.modules[stem], None

    module, why = _by_name(stem)
    if module is not None:
        return module, None

    # ⚑⚑⚑ THE ORIGINAL REASON SURVIVES THE FALLBACK. A cut of this reported `no gate at
    # scripts/<x>.py` for a module that does not exist anywhere, and for a gate that `SystemExit`s
    # at import — replacing the real diagnosis with a claim about a directory the caller never
    # mentioned. **That is the swallowed-reason defect this module was written to remove**,
    # reintroduced by the repair for a different one: a reader chasing a gate's own refusal would
    # be sent looking for a missing file instead.
    path = corpus.ROOT / gate_path(name)
    if not path.exists():
        return None, why

    found, located = _by_location(stem, str(path))
    if found is not None:
        return found, None
    return None, located
