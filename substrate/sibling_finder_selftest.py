# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.sibling_finder` — the scoped bare-name resolver.

⚑ THE LOAD-BEARING CASE IS THE REMOVAL. A finder left installed resolves bare names against
a directory nobody asked about, for the rest of the process — which is the ambient effect
of a path insert wearing different clothes. The case asserts removal on the FAILURE path
too, because that is where a `finally` gets forgotten.

⚑⚑ AND THE DOTTED REFUSAL IS THE OTHER HALF. Answering for a dotted name would put this
finder ahead of the real package owner for every submodule in the process, which is a much
larger blast radius than the problem it solves.

⚑ THE IMPORT CASES GO THROUGH `importlib` RATHER THAN A STATEMENT, because a bare `import`
of a fixture module is unresolvable to the type checker by construction — the module does
not exist until the block installs the finder. Asking the machinery directly is both
honest and typed.
"""

from __future__ import annotations

import importlib
import sys
import tempfile
from pathlib import Path

from substrate import sibling_finder

EXPECTED_VALUE = 41


def _boom() -> None:
    """Fail the way a module raising at import fails."""
    msg = "the load failed"
    raise RuntimeError(msg)


def _import_value(name: str) -> object:
    """Import `name` and return its VALUE attribute, or None when it will not import."""
    sys.modules.pop(name, None)
    try:
        module = importlib.import_module(name)
    except ImportError:
        return None
    finally:
        sys.modules.pop(name, None)
    found: object = getattr(module, "VALUE", None)
    return found


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "a_sibling.py").write_text("VALUE = 41\n", encoding="utf-8")
        finder = sibling_finder.SiblingFinder(tmp)

        # ── what the finder answers for ──────────────────────────────────────
        check("a bare name with a file resolves", passed=finder.find_spec("a_sibling") is not None)
        check(
            "a bare name with no file does not", passed=finder.find_spec("no_such_sibling") is None
        )
        # ⚑ A dotted name is somebody else's to resolve.
        check("a dotted name is refused", passed=finder.find_spec("pkg.a_sibling") is None)

        # ── the context manager installs and removes ─────────────────────────
        before = list(sys.meta_path)
        with sibling_finder.siblings_of(tmp):
            check(
                "the finder is installed inside the block",
                passed=len(sys.meta_path) == len(before) + 1,
            )
        check("and removed after it", passed=sys.meta_path == before)

        # ⚑ REMOVED ON THE FAILURE PATH TOO — where a missing `finally` hides.
        try:
            with sibling_finder.siblings_of(tmp):
                _boom()
        except RuntimeError:
            pass
        check("and removed when the block raises", passed=sys.meta_path == before)

        # ── it actually makes a bare import work ─────────────────────────────
        with sibling_finder.siblings_of(tmp):
            inside = _import_value("a_sibling")
        check("a bare import inside the block resolves", passed=inside == EXPECTED_VALUE)

        # ⚑ AND STOPS WORKING AFTER IT. If the name stayed importable, the finder would
        # be a path insert with extra steps.
        check("and does NOT resolve outside the block", passed=_import_value("a_sibling") is None)

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
