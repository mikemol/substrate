# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.agdai_shim_path`: routing by an injected environment."""

from __future__ import annotations

import sys
from pathlib import Path

from substrate.agdai_shim_path import REAL_ROOT_VAR, shim_path

_HERE = Path("/snapshot/jea/metalanguage")
_REAL = "/home/me/checkout"


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    named = shim_path(_HERE, {REAL_ROOT_VAR: _REAL})
    return [
        ("unset: the sibling of the importing file", shim_path(_HERE, {}) == _HERE / "agdai_shim"),
        (
            "set: under the real checkout",
            named == Path(_REAL) / "jea" / "metalanguage" / "agdai_shim",
        ),
        (
            "blank counts as unset, never the current directory",
            shim_path(_HERE, {REAL_ROOT_VAR: ""}) == _HERE / "agdai_shim",
        ),
        ("the snapshot path is not returned when a real root is named", _HERE not in named.parents),
    ]


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"agdai-shim-path selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
