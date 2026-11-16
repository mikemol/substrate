#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""build_census.py: the CLI over the GENERATED map of this repo's BUILD system.

⚑⚑⚑ THE ORIGIN IS DRAINED (W329). It carried 376 findings, so the per-file gate refused every
edit; each concern moved into a clean `substrate/` module, held value-for-value (and byte-for-byte
on the rendered block) against the origin before this swap:

    the facts (DAG, membudget, ledgers, gates)     substrate/build_census_facts
    the two rendered blocks                        substrate/build_census_render
    markers, splice, sync, drift check, --gates    substrate/build_census_skill
    the cases                                      substrate/build_census_selftest

New work goes in the modules, never here. This file keeps the NAME and the entry points its
consumers bind to: `gen_build_makefiles` loads it BY PATH and calls `cmd_sync()` / `cmd_check()`
with no arguments, catching `BlockError`.

⚑ THE TREE IS RESOLVED HERE, AT CALL TIME, FROM THIS FILE'S LOCATION, and handed to the modules as
a parameter; no module-level constant derives from `__file__`.

Two blocks land in the skill: `build-census` (STRUCTURAL, gated by `--check`) and
`build-observations` (MEASURED from gitignored ledgers, never gated).
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import build_census_selftest, build_census_skill

BlockError = build_census_skill.BlockError

_USAGE = (
    "modes:\n  --sync      rewrite the census blocks in the build-system skill\n"
    "  --check     DRIFT GATE: exit 1 unless the STRUCTURAL block is current\n"
    "  --gates     the DECLARED gate roster, partitioned by phase\n"
    "  --selftest  the guarded cases\n"
    "(the canonical spellings are `gen_build_makefiles.py --sync-census` / `--check-census`)\n"
)
_REFUSED = 2


def _tree() -> tuple[Path, Path]:
    """Return `(repo root, scripts dir)` from this file's location, at call time."""
    scripts = Path(__file__).resolve().parent
    return scripts.parent, scripts


def cmd_sync() -> int:
    """Rewrite the census blocks in the skill."""
    root, scripts = _tree()
    return build_census_skill.cmd_sync(root, scripts)


def cmd_check() -> int:
    """Drift gate: return 1 unless the committed structural block is current."""
    root, scripts = _tree()
    return build_census_skill.cmd_check(root, scripts)


def cmd_gates() -> int:
    """Print the declared gate roster, partitioned by phase."""
    root, _scripts = _tree()
    return build_census_skill.cmd_gates(root)


def selftest() -> int:
    """Run the guarded cases; 0 when every one holds."""
    root, scripts = _tree()
    return 0 if build_census_selftest.selftest(root, scripts) else 1


def main(argv: list[str]) -> int:
    """Dispatch the CLI modes and return the exit code."""
    if "--selftest" in argv:
        return selftest()
    if "--gates" in argv:
        return cmd_gates()
    if "--sync" in argv:
        return cmd_sync()
    if "--check" in argv:
        return cmd_check()
    sys.stderr.write((__doc__ or "") + "\n")
    sys.stderr.write(_USAGE)
    return _REFUSED


if __name__ == "__main__":
    sys.exit(main(sys.argv))
