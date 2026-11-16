#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run a ratchet gate read-only and report what it would pay down.

Split from `paydown_census` because RUNNING the gates and REPORTING on them are different
responsibilities — and it is the running half that needs the subprocess exemption, so
keeping them together would grant it to the reporting too.

⚑⚑ READ-ONLY BY CONSTRUCTION, NOT BY INTENT. `SUBSTRATE_RATCHET_WRITE` is not set here,
so `may_write` resolves False and no baseline can be banked by a census that only wanted
to look. That is the read-mutates-state defect the ratchet itself was measured committing
TWICE — a plain `--quiet` run rewrote a baseline 48 -> 45, and the second time it was a
read-only auditor that had been explicitly forbidden to write and could not avoid it.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

_ROOT = Path(__file__).absolute().parent.parent
_VENV_PY = _ROOT / ".venv" / "bin" / "python3"
_CENSUS = _ROOT / "scripts" / "gate_census.py"

# The two lines every set-ratchet gate prints, whatever its census is about.
_PAID_RE = re.compile(r"baseline (?:would lower|LOWERED) (\d+) -> (\d+) \((\d+) ")
_ADDED_RE = re.compile(r"BROKEN — (\d+) NEW ")

# Some censuses walk the whole Agda tree.
_TIMEOUT_S = 600


class Row(NamedTuple):
    """One gate's paydown standing.

    ⚑ `paid` AND `added` ARE BOTH REPORTED, NEVER NETTED. A single number cannot
    distinguish "8,516 paid, 375 added" from "8,141 paid" — and the first is a gate one
    edit away from recording enormous progress while the second is steady state.
    """

    gate: str
    paid: int
    added: int
    before: int
    after: int
    ran: bool

    @property
    def blocked(self) -> bool:
        """Report whether real paydown is held hostage by additions."""
        return self.paid > 0 and self.added > 0


def gates() -> list[str]:
    """Return the gate scripts that call a set ratchet, derived from the tree.

    ⚑ DERIVED, NEVER TYPED. `gate_census --baselines` owns the roster; a second
    hand-written list here would be the roster-beside-a-roster shape this repo keeps
    retiring, and it would go stale the next time a gate is added.
    """
    p = subprocess.run(
        [str(_VENV_PY), str(_CENSUS), "--baselines"], capture_output=True, text=True, check=False
    )
    out: list[str] = []
    for line in p.stdout.splitlines():
        parts = line.split()
        head = parts[0] if parts else ""
        if head.startswith("scripts/check_") and head.endswith(".py") and head not in out:
            out.append(head)
    return out


def measure(gate: str) -> Row:
    """Run one gate read-only and extract its paydown standing."""
    try:
        p = subprocess.run(
            [str(_VENV_PY), str(_ROOT / gate), "--quiet"],
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_S,
            check=False,
            cwd=str(_ROOT),
        )
    except (OSError, subprocess.SubprocessError):
        return Row(gate=gate, paid=0, added=0, before=0, after=0, ran=False)
    text = p.stdout + p.stderr
    paid = _PAID_RE.search(text)
    added = _ADDED_RE.search(text)
    return Row(
        gate=gate,
        paid=int(paid.group(3)) if paid else 0,
        added=int(added.group(1)) if added else 0,
        before=int(paid.group(1)) if paid else 0,
        after=int(paid.group(2)) if paid else 0,
        ran=True,
    )


if __name__ == "__main__":
    for g in gates():
        sys.stdout.write(f"{measure(g)}\n")
