#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""findings.py — the per-finding WITNESS for the oracle ledger, now a shim over the bibs.

⚑⚑⚑ THE ROSTER MOVED INTO THE BIBS (W40, the roster cleanroom). This file held ~850 witnesses in a
`WITNESSES` Python literal behind a per-file gate that refused every edit. Every witness is now its
bib entry's `check` (operator: *"Converge `check`; roster wins"*), every note moved into the bibs
verbatim (*"move losslessly, then structure"*), and the answers come from `substrate.ledger_cli`.
The recorded proof, in `.claude/paths-forward.ledger`: 850 of 850 checks agreed with the roster,
0 differed; 846 of 846 notes carried. The pre-shim file survives in git history.

⚑ STDLIB ONLY, AND THE TREE IS RESOLVED HERE, AT CALL TIME. Callers run this with whatever
interpreter they have — `witness_resolves` uses its own `sys.executable`, a person types
`python3` — so the shim imports nothing outside the standard library and runs the tree's venv
interpreter. The tree is `git rev-parse --show-toplevel` from the caller's cwd, never a path
derived from this file (the no-module-root rule); outside a checkout it REFUSES.

usage: findings.py <KEY> | --list | --kinds | --selftest
       --register  RETIRED — file a finding with `bibstruct --add`
       --pairing   RETIRED — the roster and the bibs are one thing now
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

# The module that answers every live mode.
_CLI = "substrate.ledger_cli"

# The retired modes, and what each refusal says.
_RETIRED = {
    "--register": (
        "file a finding as a bib entry with `bibstruct --add <key> claim=... check=<kind>:... "
        "--bib .claude/agents/<oracle>.bib --apply`; its `check` IS the witness now"
    ),
    "--pairing": (
        "the roster and the bibs are one thing now; the last pairing census found 850 of 850 "
        "checks agreeing (recorded in .claude/paths-forward.ledger)"
    ),
}

# Exit code for a refusal, matching the ledger's UNRUNNABLE.
_REFUSED = 2


def _tree() -> Path | None:
    """Return the checkout the caller is in, or None when there is none (or no git)."""
    git = shutil.which("git")
    if git is None:
        return None
    done = subprocess.run(
        [git, "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
    )
    top = done.stdout.strip()
    return Path(top) if done.returncode == 0 and top else None


def _refuse(message: str) -> int:
    """Print a refusal and return the refusal exit code."""
    sys.stderr.write(f"findings.py: {message}\n")
    return _REFUSED


def main(argv: list[str]) -> int:
    """Answer one key, list, or census through `ledger_cli`; refuse the retired modes."""
    args = argv[1:]
    if len(args) != 1:
        sys.stderr.write(__doc__ or "")
        return _REFUSED
    mode = args[0]
    if mode in _RETIRED:
        return _refuse(f"{mode} is RETIRED — {_RETIRED[mode]}")
    tree = _tree()
    if tree is None:
        return _refuse("not inside a git checkout (or no git); run from the substrate tree")
    python = tree / ".venv" / "bin" / "python"
    if not python.is_file():
        return _refuse(f"no venv interpreter at {python}; run `uv sync` in {tree}")
    if mode == "--selftest":
        command = [str(python), "-m", "substrate.ledger_cli_selftest"]
    else:
        command = [str(python), "-m", _CLI, "--root", str(tree), mode]
    return subprocess.run(command, cwd=tree, check=False).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
