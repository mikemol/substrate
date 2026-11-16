#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""gate_status.py: run every hook-wired gate and report which pass — WITHOUT committing.

⚑⚑⚑ THE ORIGIN IS DRAINED (W330). It carried 351 findings, so the per-file gate refused every
edit; each concern moved into a clean `substrate/` module, held value-for-value against the origin
(parse, verdicts, mode sweep, write-default probe, the `--peaks` report) before this swap:

    the hook's gate list, verdict rule, probe     substrate/gate_status_facts
    the process boundary and its Runner            substrate/gate_status_exec
    one gate / one gate under each flag mode       substrate/gate_status_run
    the `--peaks` memory sweep                     substrate/gate_status_peaks
    the flag dispatch and the report               substrate/gate_status_cli
    the cases                                      substrate/gate_status_selftest

New work goes in the modules, never here. This file keeps the NAME and what consumers bind to:
`catalog/library/figures.py` and `scripts/wg_dispatch.py` import it BARE and call `gates()`.

    gate_status.py             # run them all, report verdicts
    gate_status.py --list      # just enumerate what the hook wires
    gate_status.py --modes <script>   # one gate ACROSS ITS FLAG MODES
    gate_status.py --peaks [--lease=<MB>] [--gate=<name>] [--allow-writes]
    gate_status.py --selftest

⚑ THE GATE LIST IS PARSED FROM THE HOOK, NEVER RESTATED: a gate added to `.githooks/pre-commit`
appears here on the next run with no edit.

⚑ THE TREE IS RESOLVED HERE, AT CALL TIME, FROM THIS FILE'S LOCATION, and handed to the modules as
a parameter; no module-level constant derives from `__file__`. The path is NOT symlink-resolved,
as in the origin: a repo that adopts `scripts/` by symlink sweeps ITS OWN hook.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from substrate import build_settings, gate_status_cli, gate_status_facts, gate_status_selftest
from substrate import gate_status_run as run
from substrate.gate_status_exec import run_process
from substrate.gate_status_facts import (
    CHECK_MODE,
    MODES,
    RUN,
    VERDICT,
    WRITE_DEFAULT_HINT,
    verdict_line,
)

# The names the origin exposed that still mean the same thing; `gates` is defined below.
__all__ = [
    "CHECK_MODE",
    "MODES",
    "RUN",
    "VERDICT",
    "WRITE_DEFAULT_HINT",
    "gates",
    "main",
    "verdict_line",
]


def _root() -> Path:
    """Return the repo root from this file's location (not symlink-resolved), at call time."""
    return Path(__file__).absolute().parent.parent


def _hook(root: Path) -> Path:
    """Return the pre-commit hook of the tree at `root`."""
    return root / ".githooks" / "pre-commit"


def gates(hook: Path | None = None) -> list[gate_status_facts.Gate]:
    """Return `(name, argv, conditional)` for the hook's `run` lines (default: this tree's)."""
    return gate_status_facts.gates(hook if hook is not None else _hook(_root()))


def main(argv: list[str]) -> int:
    """Dispatch the CLI flags and return the exit code."""
    root = _root()
    if "--selftest" in argv:
        return 0 if gate_status_selftest.selftest(root) else 1
    tree = gate_status_facts.Tree(root, _hook(root), build_settings.MEMBUDGET)
    host = run.Host(tree, sys.executable, os.environ)
    return gate_status_cli.main(argv, host, run_process, sys.stdout)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
