#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.witness_mode` — every verdict branch, both recorded defects, and LIVE.

⚑ THE TWO DEFECTS THE ORIGIN RECORDS ARE CASED BY THEIR SHAPE: a divergence row with a WIDE
column gap must still be found (the fixed-spacing substring missed it), and a tool named only in
`--find`'s `⚑ NOT on:` list must NOT read as declaring the mode (the tool-name substring did).

⚑⚑ THE LIVE CASES READ THE BIBS. Every `mode` witness in the ledger must produce a DEFINITE verdict
(CLOSED or OPEN — never UNRUNNABLE), proving the instrument runs on the real entries. This suite
once differenced each against the origin `findings.py <KEY>` and all 4 agreed (recorded in the
paths-forward ledger); once `findings.py` is a shim over the bibs that comparison is circular.
The tree is the working directory, resolved at this CLI entry; the suite REFUSES without a ledger.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from mikemol.ledger import finding_kinds

from substrate import ledger_cli, witness_mode, witness_run

if TYPE_CHECKING:
    from collections.abc import Sequence

    from mikemol.ledger.finding_kinds import Runner

# The check-spelling prefix of the kind this suite owns.
_KIND = "mode"

# The verdicts that are a measurement, not a failure to measure.
_DEFINITE = (finding_kinds.CLOSED, finding_kinds.OPEN)

DIVERGENT = "── scratch/foo.py\n  UNDOCUMENTED        --bar     dispatched on argv\n"
QUIET = "── scratch/foo.py\n  UNBACKED  --other  documented, no literal\n"
DECLARED = "   --bar  on scratch/foo.py  [usage]  does bar\n   ⚑ NOT on: scratch/foo.py\n"
NEGATIVE_ONLY = "   --bar  on scratch/baz.py  [usage]  does bar\n   ⚑ NOT on: scratch/foo.py\n"


def _runner(divergence: str | None, find: str | None) -> Runner:
    """Return a runner answering `--divergence` and `--find` with fixed output (None: no start)."""

    def run(cmd: Sequence[str]) -> tuple[int | None, str]:
        out = divergence if "--divergence" in cmd else find
        return (None, "not started") if out is None else (0, out)

    return run


def _exits_two(cmd: Sequence[str]) -> tuple[int | None, str]:
    """Answer every lens as a missing script does: exit 2, no rows."""
    return 2, f"can't open file {cmd[1]!r}"


def _code(divergence: str | None, find: str | None) -> int:
    """Return the verdict code for `--bar` on `scratch/foo.py` under the fixture outputs."""
    return witness_mode.verdict("scratch/foo.py", "--bar", _runner(divergence, find))[0]


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every fixture case."""
    here = witness_mode.diverges(DIVERGENT, "foo.py", "--bar")
    elsewhere = witness_mode.diverges(DIVERGENT, "x.py", "--bar")
    return [
        ("a wide-gap divergence row is found", here),
        ("another tool's block does not count", not elsewhere),
        ("a divergent mode is OPEN", _code(DIVERGENT, DECLARED) == finding_kinds.OPEN),
        ("a declared, quiet mode is CLOSED", _code(QUIET, DECLARED) == finding_kinds.CLOSED),
        ("the NOT-on list is not a declaration", _code(QUIET, NEGATIVE_ONLY) == finding_kinds.OPEN),
        ("a deleted mode is OPEN, never CLOSED", _code(QUIET, "") == finding_kinds.OPEN),
        ("divergence not running is UNRUNNABLE", _code(None, DECLARED) == finding_kinds.UNRUNNABLE),
        ("find not running is UNRUNNABLE", _code(QUIET, None) == finding_kinds.UNRUNNABLE),
        (
            "a lens exiting non-zero is UNRUNNABLE, never GONE",
            witness_mode.verdict("scratch/foo.py", "--bar", _exits_two)[0]
            == finding_kinds.UNRUNNABLE,
        ),
    ]


def _live_cases(root: Path) -> list[tuple[str, bool]]:
    """Return one case per live `mode` witness in the bibs: its verdict must be definite."""
    checks = ledger_cli.checks(root.joinpath(*ledger_cli.PROJECT))
    live = {key: check for key, check in checks.items() if ledger_cli.kind_of(check) == _KIND}
    cases = [("the live ledger carries mode witnesses", bool(live))]
    for key, check in sorted(live.items()):
        code, note = witness_run.verdict(check, root)
        sys.stdout.write(f"  live {key}: {code} — {note[:80]}\n")
        cases.append((f"live {key}: a definite verdict", code in _DEFINITE))
    return cases


def selftest(root: Path) -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    cases = _cases() + _live_cases(root)
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"witness-mode selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


def main(argv: list[str]) -> int:
    """Resolve the tree from the working directory, refusing when it holds no ledger project."""
    if len(argv) > 1 and "--selftest" not in argv:
        return 1
    root = Path.cwd()
    if not root.joinpath(*ledger_cli.PROJECT, "paper.toml").is_file():
        sys.stderr.write(f"witness-mode selftest: no ledger project under {root}\n")
        return 2
    return selftest(root)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(main(sys.argv))
