# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The `mode:` witness — OPEN while a tool's mode dispatches with no self-description (W40).

⚑⚑ CLEANROOMED FROM `.claude/agents/findings.py:_mode_undocumented`, whose recorded lessons are
the design:

- THE READER IS `toolmodes`, never a grep of a usage block — re-deriving roster-vs-dispatch here
  would be a second authority for one relation.
- TWO DECORRELATED LENSES. `--divergence` answers *does this mode diverge*; `--find <mode>`
  answers *is it declared, and by which tool*. Absence from the first alone is ambiguous between
  DOCUMENTED and DELETED, and the origin once reported both as one green.
- A DELETED MODE IS OPEN, NOT CLOSED: a finding is not closed by deleting its subject.
- ⚑ A LENS THAT EXITS NON-ZERO DID NOT MEASURE (a divergence from the origin, deliberately). Both
  toolmodes modes exit 0 when healthy, `--find` included at zero hits. The origin tested only
  for a process that never STARTED, so a missing `toolmodes.py` — python exits 2 with no rows —
  read as "no divergence, no declaration" and reported the mode GONE: an absent instrument read
  as a measurement, the three-senders-on-exit-2 class. Here it is UNRUNNABLE.
- PARSE THE ROWS, NEVER SUBSTRING THE BLOCK. The first cut matched a fixed-spacing substring and
  returned a false zero on every finding it held; a tool-name substring over `--find` matches the
  `⚑ NOT on:` NEGATIVE list.

The two parsers are pure over tool output, so the suite cases them on fixtures; `verdict` wires
them to a runner.
"""

from __future__ import annotations

from pathlib import PurePath
from typing import TYPE_CHECKING

from mikemol.ledger import finding_kinds

if TYPE_CHECKING:
    from mikemol.ledger.finding_kinds import Runner

# The toolmodes invocation, relative to the tree.
TOOLMODES = ("python3", "scratch/toolmodes.py")

# The prefix `--divergence` opens each tool's block with.
_BLOCK = "── "

# A `--find` declaration row has at least the flag, `on`, and the path.
_DECL_FIELDS = 3


def diverges(divergence: str, stem: str, mode: str) -> bool:
    """Report whether `--divergence` output lists `mode` UNDOCUMENTED under the tool `stem`."""
    in_tool = False
    for line in divergence.splitlines():
        if line.startswith(_BLOCK):
            in_tool = line[len(_BLOCK) :].strip().endswith(stem)
            continue
        parts = line.split()
        if in_tool and parts[:2] == ["UNDOCUMENTED", mode]:
            return True
    return False


def declared(found: str, stem: str, mode: str) -> str | None:
    """Return the declaration source `--find` output gives `mode` on the tool `stem`, else None."""
    for line in found.splitlines():
        parts = line.split()
        if len(parts) < _DECL_FIELDS or parts[0] != mode or parts[1] != "on":
            continue
        if PurePath(parts[2]).name == stem:
            return parts[3] if len(parts) > _DECL_FIELDS else "(source unstated)"
    return None


def verdict(tool: str, mode: str, run: Runner) -> finding_kinds.Verdict:
    """Return the `mode:` verdict for `mode` on `tool`, reading toolmodes through `run`."""
    stem = PurePath(tool).name
    rc, out = run([*TOOLMODES, "--divergence"])
    if rc != 0:
        return finding_kinds.UNRUNNABLE, f"toolmodes --divergence did not run ({rc}): {out[:120]}"
    if diverges(out, stem, mode):
        return finding_kinds.OPEN, f"{stem} {mode} still dispatches with no self-description"
    rc2, found = run([*TOOLMODES, "--find", mode])
    if rc2 != 0:
        return finding_kinds.UNRUNNABLE, (
            f"{stem} {mode} has no divergence row, but toolmodes --find did not run, so "
            f"DOCUMENTED cannot be distinguished from DELETED: {found[:100]}"
        )
    source = declared(found, stem, mode)
    if source is not None:
        return finding_kinds.CLOSED, f"{stem} {mode} is DOCUMENTED — declared {source}"
    return finding_kinds.OPEN, (
        f"{stem} {mode} is GONE — no divergence row AND no declaration in toolmodes --find. "
        "A finding is not closed by deleting its subject: re-key or retire it deliberately."
    )
