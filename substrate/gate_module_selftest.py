#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.gate_module` — a refusal that names what it hit.

⚑⚑⚑ THE `SystemExit` CASE IS THE ONE THAT LOOKS LIKE OVER-CATCHING AND IS NOT. Several gates in
this tree refuse at IMPORT time — an unstated tenant, an unknown flag — by exiting rather than
raising. `SystemExit` does not derive from `Exception`, so catching only `Exception` would let a
gate's own refusal kill the census trying to report it: the process dies while measuring instead
of recording one unmeasurable gate. A case is what keeps that catch from being "tidied up" later.

⚑⚑ AND ITS FIXTURE IS A COMMITTED MODULE, NOT A TEMPFILE. Writing one at test time would need a
`sys.path` insert — the mechanism this repo forbids — so `gate_module_exiting_fixture` lives in
the package and is importable by its real name, which is the same code path a live gate takes.

⚑ THE REASON MUST TRAVEL WITH THE FAILURE. Returning a bare `None` left two gates reporting
`n/a` with no way to ask why, and the only remaining route was re-deriving the import by hand.
"""

from __future__ import annotations

import sys

from substrate import gate_module

# The committed fixture that exits during import.
_EXITING = "substrate.gate_module_exiting_fixture"


def a_real_module_imports(out: list[str]) -> int:
    """Check a module that exists comes back with no reason."""
    mod, why = gate_module.gate_module("json")
    bad = 0
    if mod is None:
        out.append(f"selftest: a real module did not import: {why}")
        bad += 1
    if why is not None:
        out.append(f"selftest: a successful import carried a reason: {why!r}")
        bad += 1
    return bad


def the_extension_is_optional(out: list[str]) -> int:
    """Check both spellings resolve, since call sites use both."""
    with_ext, _why = gate_module.gate_module("json.py")
    if with_ext is None:
        out.append("selftest: a gate named with .py did not resolve")
        return 1
    return 0


def a_missing_module_names_its_error(out: list[str]) -> int:
    """Check a failed import returns the reason rather than a bare None."""
    mod, why = gate_module.gate_module("no_such_module_anywhere")
    bad = 0
    if mod is not None:
        out.append("selftest: a missing module imported")
        bad += 1
    if not why or "ModuleNotFoundError" not in why:
        out.append(f"selftest: the failure reason was {why!r}")
        bad += 1
    return bad


def a_module_that_exits_is_caught(out: list[str]) -> int:
    """Check a gate that `SystemExit`s at import is reported, not propagated.

    ⚑ THE CASE THAT JUSTIFIES `BaseException`. Without that catch this call terminates the whole
    census — which is what several real gates would do, since they refuse an unstated tenant by
    exiting at import.
    """
    # ⚑ THE FIXTURE IS EVICTED FIRST. A module already in `sys.modules` imports from the cache
    # without re-running its body, so a second case (or a second run in one process) would see
    # a successful import and pass while measuring nothing.
    sys.modules.pop(_EXITING, None)

    mod, why = gate_module.gate_module(_EXITING)
    bad = 0
    if mod is not None:
        out.append("selftest: an exiting module reported as imported")
        bad += 1
    if not why or "SystemExit" not in why:
        out.append(f"selftest: an exiting module's reason was {why!r}")
        bad += 1
    return bad


_ARMS = (
    a_real_module_imports,
    the_extension_is_optional,
    a_missing_module_names_its_error,
    a_module_that_exits_is_caught,
)

_CASE_COUNT = 2 + 1 + 2 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"gate-module selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"gate-module selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
