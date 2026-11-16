# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.build_compat` — the origin's shapes, and the origin's cycle exit.

⚑ THE LIVE CASE COMPARES AGAINST THE ORIGIN, not against itself: `parse_tree` here must return
what `gen_build_makefiles.parse_tree` returns, in the same types, over the real tree.
"""

from __future__ import annotations

import contextlib
import io
import sys

from substrate import build_compat, flat_origin

_CYCLE_EXIT = 2


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    origin = flat_origin.load()
    o_disk, o_deps = origin.parse_tree()
    disk, deps = build_compat.parse_tree(flat_origin.load_agdatext().strip)
    depth, order = build_compat.kahn_depth(disk, deps)

    chain_disk = {"A": "A.agda", "B": "B.agda"}
    chain_deps: dict[str, set[str]] = {"A": set(), "B": {"A"}}
    cdepth, corder = build_compat.kahn_depth(chain_disk, chain_deps)

    exited: int | None = None
    with contextlib.redirect_stderr(io.StringIO()):
        try:
            build_compat.kahn_check({"X": "X.agda", "Y": "Y.agda"}, {"X": {"Y"}, "Y": {"X"}})
        except SystemExit as stop:
            exited = stop.code if isinstance(stop.code, int) else None
    return [
        ("parse_tree equals the origin's disk map", disk == o_disk),
        ("parse_tree equals the origin's deps", deps == o_deps),
        (
            "deps values are mutable sets, as the origin's are",
            all(isinstance(v, set) for v in deps.values()),
        ),
        ("kahn_depth orders every module", len(order) == len(disk) and depth >= 1),
        ("a chain's depth is its length", cdepth == len(chain_disk)),
        ("a dependency precedes its dependent", corder.index("A") < corder.index("B")),
        ("a cycle exits 2, as fix_notinscope expects", exited == _CYCLE_EXIT),
        (
            "IMPRE is the model's import pattern",
            build_compat.IMPRE.pattern.startswith(r"^\s*(?:open\s+import|import)"),
        ),
    ]


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"build-compat selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
