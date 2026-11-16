#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.witness_agda` — every verdict, the token divergence, and LIVE.

⚑ THE RECORD-AS-TOKEN DIVERGENCE IS CASED: a record whose name occurs only INSIDE another name
must read UNRUNNABLE (not provided), where the origin's substring test read it as present.

⚑⚑ THE LIVE CASES READ THE BIBS. Every `agda-field` / `agda-grep` witness in the ledger must produce
a DEFINITE verdict (CLOSED or OPEN — never UNRUNNABLE), proving the Agda index answers for the real
entries. This suite once differenced against the origin `findings.py <KEY>` and both agreed
(recorded in the paths-forward ledger); once `findings.py` is a shim that comparison is circular.
The tree is the working directory, resolved at this CLI entry; the suite REFUSES without a ledger.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from mikemol.ledger import finding_kinds

from substrate import ledger_cli, witness_agda, witness_run

if TYPE_CHECKING:
    from collections.abc import Sequence

    from mikemol.ledger.finding_kinds import Runner

# The check-spelling prefixes of the kinds this suite owns.
_KINDS = ("agda-field", "agda-grep")

# The verdicts that are a measurement, not a failure to measure.
_DEFINITE = (finding_kinds.CLOSED, finding_kinds.OPEN)

PROVIDES = "Rec\nfield-a\nfield-b\nRecordLike\n"

# The count the `--grep` fixture's footer reports.
GREP_COUNT = 2
GREP = f"  a\n  b\nSubstrate: {GREP_COUNT} name(s) matching 'x'\n"


def _answer(rc: int | None, out: str) -> Runner:
    """Return a runner that answers every command with `(rc, out)`."""

    def run(_cmd: Sequence[str]) -> tuple[int | None, str]:
        return rc, out

    return run


def _field(record: str, field: str, rc: int | None = 0, out: str = PROVIDES) -> int:
    """Return the `agda-field` verdict code for `record`/`field` under a fixed answer."""
    return witness_agda.lacks_field("M", record, field, _answer(rc, out))[0]


def _grep(expected: int, rc: int | None = 0, out: str = GREP) -> int:
    """Return the `agda-grep` verdict code for `expected` under a fixed answer."""
    return witness_agda.grep_holds("x", expected, _answer(rc, out))[0]


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every fixture case."""
    closed, open_, unrun = finding_kinds.CLOSED, finding_kinds.OPEN, finding_kinds.UNRUNNABLE
    return [
        ("an absent field is CLOSED", _field("Rec", "field-c") == closed),
        ("a declared field is OPEN", _field("Rec", "field-a") == open_),
        ("a record only INSIDE another name is not provided", _field("Record", "x") == unrun),
        ("a tool exiting non-zero is UNRUNNABLE", _field("Rec", "x", rc=2) == unrun),
        ("an empty answer is UNRUNNABLE", _field("Rec", "x", out="") == unrun),
        ("the footer count is read", witness_agda.grep_count(GREP) == GREP_COUNT),
        ("an unchanged count is CLOSED", _grep(GREP_COUNT) == closed),
        ("a moved count is OPEN — the repair arriving", _grep(GREP_COUNT + 1) == open_),
        ("a missing footer is UNRUNNABLE", _grep(GREP_COUNT, out="no footer\n") == unrun),
        ("a grep exiting non-zero is UNRUNNABLE", _grep(GREP_COUNT, rc=1) == unrun),
    ]


def _live_cases(root: Path) -> list[tuple[str, bool]]:
    """Return one case per live Agda witness in the bibs: its verdict must be definite."""
    checks = ledger_cli.checks(root.joinpath(*ledger_cli.PROJECT))
    live = {key: check for key, check in checks.items() if ledger_cli.kind_of(check) in _KINDS}
    cases = [("the live ledger carries Agda witnesses", bool(live))]
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
    sys.stdout.write(f"witness-agda selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


def main(argv: list[str]) -> int:
    """Resolve the tree from the working directory, refusing when it holds no ledger project."""
    if len(argv) > 1 and "--selftest" not in argv:
        return 1
    root = Path.cwd()
    if not root.joinpath(*ledger_cli.PROJECT, "paper.toml").is_file():
        sys.stderr.write(f"witness-agda selftest: no ledger project under {root}\n")
        return 2
    return selftest(root)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(main(sys.argv))
