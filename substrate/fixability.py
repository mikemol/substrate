# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""How much of a file's debt a machine can pay — safe-fixable, unsafe-fixable, or by hand.

⚑⚑⚑ A FINDING COUNT SAYS NOTHING ABOUT THE WORK, AND THE THREE KINDS DIFFER BY ORDERS OF
MAGNITUDE. `ruff --fix` rewrites a safe finding with no judgement; an UNSAFE fix may change
behaviour and needs a reader per hunk; a mypy error is usually a type someone must decide.
Planning against a total treats all three as one unit and produces an estimate that is wrong
in whichever direction the file's mix happens to lean.

⚑⚑ AND "UNSAFE" IS RUFF'S WORD FOR "MAY CHANGE BEHAVIOUR", NOT FOR "PROBABLY WRONG". Many are
mechanical in practice — a `%`-format to an f-string, a `dict()` to a literal — so the honest
report is a THIRD BUCKET rather than folding them in with either neighbour. Counting them as
automatic overstates what a sweep achieves; counting them as manual understates it, and this
repo has already retired two plans built on a single undifferentiated number.

⚑ MYPY FINDINGS ARE REPORTED SEPARATELY BECAUSE NOTHING FIXES THEM. There is no `--fix` for a
missing annotation that a machine can infer safely at this repo's strictness, so they are the
floor of what a human must do — and on a large file they can dominate a total that looks like
lint.

⚑ THE COUNTS COME FROM RUFF'S OWN SUMMARY LINE, not from re-deriving fixability per rule. A
local table of which rules are fixable would drift from the version installed, and the tool
already states it.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass

from substrate import corpus, editable

# ruff's trailing summary: "[*] N fixable with the `--fix` option (M hidden fixes …)".
_SAFE = re.compile(r"\[\*\]\s+(\d+)\s+fixable")
_UNSAFE = re.compile(r"\((\d+)\s+hidden fixes")

# "Found N errors." — the ruff total, which the two fixable counts are subsets of.
_FOUND = re.compile(r"Found\s+(\d+)\s+error")

_TIMEOUT_S = 120


@dataclass(frozen=True, slots=True)
class Fixability:
    """One file's debt, split by what can pay it down."""

    path: str
    safe: int
    unsafe: int
    lint_total: int
    types: int

    @property
    def manual_lint(self) -> int:
        """Lint findings no fix exists for."""
        return max(self.lint_total - self.safe - self.unsafe, 0)

    @property
    def total(self) -> int:
        """Every finding the per-file gate would refuse on."""
        return self.lint_total + self.types

    @property
    def mechanical(self) -> int:
        """Findings a machine can rewrite, safely or under review."""
        return self.safe + self.unsafe

    @property
    def by_hand(self) -> int:
        """Findings that need a decision — unfixable lint plus every type error."""
        return self.manual_lint + self.types


def _first_int(pattern: re.Pattern[str], text: str) -> int:
    """Return the first integer `pattern` captures in `text`, or zero."""
    match = pattern.search(text)
    return int(match.group(1)) if match else 0


def lint_fixability(rel: str) -> tuple[int, int, int]:
    """Return `(safe, unsafe, total)` lint findings for one file.

    ⚑ THE SUMMARY LINE IS THE AUTHORITY. ruff states how many of its own findings it can fix
    and how many more it could fix unsafely; re-deriving that from a rule table here would
    drift from the installed version the first time a rule gained a fix.
    """
    argv = [
        "python3",
        "-m",
        "ruff",
        "check",
        "--statistics",
        "--config",
        str(corpus.ROOT / "pyproject.toml"),
        "--no-cache",
        rel,
    ]
    try:
        proc = subprocess.run(
            argv,
            cwd=corpus.ROOT,
            capture_output=True,  # noqa: S603
            text=True,
            timeout=_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return (0, 0, 0)
    if proc.returncode not in (0, 1):
        return (0, 0, 0)
    text = proc.stdout
    return (_first_int(_SAFE, text), _first_int(_UNSAFE, text), _first_int(_FOUND, text))


def fixability_of(rel: str) -> Fixability:
    """Return the fixability split for one file.

    ⚑ THE TYPE COUNT COMES FROM THE SAME READER THE GATE USES, so this and the editability
    verdict cannot disagree about how much debt a file carries.
    """
    safe, unsafe, total = lint_fixability(rel)
    types, why = editable.mypy_findings(rel)
    return Fixability(rel, safe, unsafe, total, 0 if why else types)


def render(rows: list[Fixability]) -> str:
    """Render the fixability split across files, with the aggregate first."""
    safe = sum(r.safe for r in rows)
    unsafe = sum(r.unsafe for r in rows)
    manual = sum(r.manual_lint for r in rows)
    types = sum(r.types for r in rows)
    total = sum(r.total for r in rows)
    out = [f"{len(rows)} file(s), {total} finding(s):", ""]
    for label, n in (
        ("safe-fixable (ruff --fix)", safe),
        ("unsafe-fixable (review per hunk)", unsafe),
        ("lint, no fix available", manual),
        ("type errors (no fixer)", types),
    ):
        share = n * 100 // total if total else 0
        out.append(f"  {label:<34} {n:>7}  ({share}%)")
    # ⚑ THE PLANNING SPLIT, STATED ONCE. Everything above the line is a sweep; everything
    # below is a decision per finding.
    out.append("")
    mech = safe + unsafe
    out.append(f"  mechanical: {mech}  ·  by hand: {manual + types}")
    return "\n".join(out) + "\n"
