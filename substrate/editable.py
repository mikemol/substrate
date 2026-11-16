# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Whether the per-file gate would ACCEPT an edit to a file — the second drain gate.

⚑⚑⚑ TWO INDEPENDENT GATES DECIDE WHETHER A SITE CAN BE DRAINED, AND EITHER ALONE OVERSTATES
THE WORK. `insert_scope` answers whether removing a site preserves BEHAVIOUR; this answers
whether the zero-tolerance per-file gate would let anyone edit the file at all. A site can be
perfectly mechanical and sit in a file that refuses every edit — measured on the eliza subtree,
where forty-six module-level inserts sit in files carrying dozens of findings each. Planning
against scope alone schedules edits that will be refused one at a time.

⚑⚑ AND THE PREDICATE IS "IS IT CLEAN", NOT "HOW MANY FINDINGS". The gate is zero-tolerance:
one finding refuses the write and reverts it, so a file with one is exactly as uneditable as a
file with three hundred. Reporting the count invites ranking by it, which would suggest the
one-finding files are nearly ready when the gate makes no such distinction. The count is
carried only as EVIDENCE for the verdict.

⚑ A CHECKER THAT COULD NOT RUN IS `UNKNOWN`, NEVER CLEAN. ruff and mypy both exit 1 for
"flagged something" and 2 for "could not run" — a config error, an unreadable path, an absent
install. Collapsing the second into zero findings would report a broken instrument as a clean
file, which is the false-green this whole family refuses; `pycheck_show` records a peer
producing exactly that inside a probe written to test an instrument.

⚑ THE HOUSE CONFIG IS PASSED EXPLICITLY, because both checkers discover configuration by
walking up from the file they are given, and a checker pointed at the wrong config is a checker
that agrees with you.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path

#: The verdict for a file whose checkers could not be run at all.
UNKNOWN = "UNKNOWN"

#: The verdict for a file the gate would accept an edit to.
CLEAN = "CLEAN"

#: The verdict for a file the gate would refuse an edit to.
DIRTY = "DIRTY"

# ⚑ A CEILING ON WAITING, NOT A PREDICTION. A file that takes longer than this is reported
# UNKNOWN rather than silently counted clean.
_TIMEOUT_S = 120


@dataclass(frozen=True, slots=True)
class Verdict:
    """One file, and whether the per-file gate would accept an edit to it."""

    path: str
    state: str
    findings: int
    why: str = ""

    @property
    def is_editable(self) -> bool:
        """Whether an edit to this file can land.

        ⚑ `UNKNOWN` IS NOT EDITABLE. A file whose checkers did not run may be clean or may
        not; treating it as editable would schedule work on an unmeasured file, and treating
        it as dirty at least fails toward asking.
        """
        return self.state == CLEAN


def _config() -> Path:
    """Return the house config both checkers must be pointed at."""
    return corpus.ROOT / "pyproject.toml"


def _count(argv: list[str], tool: str) -> tuple[int, str]:
    """Run `argv` and return `(lines, why)`; a non-empty `why` means the run is UNKNOWN.

    ⚑ THE THIRD STATE IS NAMED HERE ONCE, for both checkers. Exit 2 is a broken invocation,
    not an absence of findings, and a reader that folded it into zero would hand back a clean
    bill produced by a checker that never examined the file.
    """
    try:
        proc = subprocess.run(
            argv,
            cwd=corpus.ROOT,
            capture_output=True,  # noqa: S603
            text=True,
            timeout=_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 0, f"{tool} did not run: {exc}"
    if proc.returncode not in (0, 1):
        detail = (proc.stderr or proc.stdout or "").strip()[:200]
        return 0, f"{tool} exited {proc.returncode}: {detail}"
    return len([ln for ln in proc.stdout.splitlines() if ln.strip()]), ""


def ruff_findings(rel: str) -> tuple[int, str]:
    """Return ruff's finding count for one file, or a reason it could not run."""
    return _count(
        [
            "python3",
            "-m",
            "ruff",
            "check",
            "--config",
            str(_config()),
            "--no-cache",
            "--quiet",
            "--output-format",
            "concise",
            rel,
        ],
        "ruff",
    )


def mypy_findings(rel: str) -> tuple[int, str]:
    """Return mypy's error count for one file, or a reason it could not run.

    ⚑ `--no-error-summary` KEEPS THE OUTPUT ONE LINE PER FINDING, so a line count IS the
    finding count. Without it the trailing summary line would inflate every file by one —
    turning every clean file into a dirty one, which is the direction that stops all work.
    """
    return _count(
        [
            "python3",
            "-m",
            "mypy",
            "--config-file",
            str(_config()),
            "--no-error-summary",
            "--no-color-output",
            rel,
        ],
        "mypy",
    )


def verdict_for(rel: str) -> Verdict:
    """Return whether the gate would accept an edit to `rel`.

    ⚑ BOTH CHECKERS, BECAUSE THE GATE RUNS BOTH. A census over ruff alone would call a file
    clean that mypy refuses, and the drain would discover it one refused edit at a time.
    """
    ruff_n, ruff_why = ruff_findings(rel)
    if ruff_why:
        return Verdict(rel, UNKNOWN, 0, ruff_why)
    mypy_n, mypy_why = mypy_findings(rel)
    if mypy_why:
        return Verdict(rel, UNKNOWN, ruff_n, mypy_why)
    total = ruff_n + mypy_n
    return Verdict(rel, CLEAN if total == 0 else DIRTY, total)


def partition(paths: list[str]) -> dict[str, list[Verdict]]:
    """Group files by whether an edit to each would land."""
    out: dict[str, list[Verdict]] = {CLEAN: [], DIRTY: [], UNKNOWN: []}
    for rel in paths:
        got = verdict_for(rel)
        out[got.state].append(got)
    return out
