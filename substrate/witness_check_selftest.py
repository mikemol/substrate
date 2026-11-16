#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.witness_check` — every live witness must round-trip, or be named.

⚑⚑ THE LIVE LEDGER IS THE FIXTURE, READ FROM THE BIBS. Since the convergence each entry's `check`
IS its witness; `witness_bibrows` parses it back to a `Row`, and `emit` must spell that row as
EXACTLY the check it came from. A spelling that does not round-trip would change what the witness
runs while reading as a faithful copy — so every refusal and every mismatch is printed by key.
(This suite read the `WITNESSES` literal until the roster moved into the bibs; the roster-vs-bib
agreement it then established — 850 of 850 — is recorded in the paths-forward ledger.)

⚑ AND THE TWO WAYS A COMMAND BREAKS THE GRAMMAR ARE CASED: a ONE-WORD command holding a space
(no comma, so the parser splits it on spaces), and an argument holding a comma, must each be
REFUSED — emitting them would silently change what the witness runs. ⚑ A space inside one
argument of a MULTI-word command is safe: the words are comma-joined, so the parser splits on
commas and the space survives. The first draft of this case used that safe shape and failed —
the emitter was right and the fixture was wrong.

The tree is the working directory, resolved at this CLI entry; the suite REFUSES without a ledger.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import ledger_cli, witness_bibrows, witness_check
from substrate.witness_source import Row


def _refuses(row: Row) -> bool:
    """Report whether `emit` refuses `row`."""
    check, _ = witness_check.emit(row)
    return not check


def _live_cases(root: Path) -> list[tuple[str, bool]]:
    """Return the round-trip cases over every live bib entry."""
    project = root.joinpath(*ledger_cli.PROJECT)
    checks = ledger_cli.checks(project)
    rows = witness_bibrows.rows(project)
    drift = [row.key for row in rows if witness_check.emit(row)[0] != checks[row.key]]
    for key in drift[:10]:
        sys.stdout.write(f"  does not round-trip: {key}\n")
    unsafe = [(row.key, witness_check.shell_unsafe(checks[row.key])) for row in rows]
    for key, chars in unsafe:
        if chars:
            sys.stdout.write(f"  shell-unsafe: {key} {chars!r}\n")
    sys.stdout.write(f"  {len(rows)} witnesses; {len(rows) - len(drift)} round-trip exactly\n")
    return [
        ("the live ledger is read", bool(rows)),
        ("every live check round-trips exactly", not drift),
    ]


def _grammar_cases() -> list[tuple[str, bool]]:
    """Return the cases for the spellings the grammar must refuse."""
    spaced = Row("fixture-space", "selftest", (["make check"], "n"))
    comma = Row("fixture-comma", "refuses", (["tool", "a,b"], "n"))
    quoted = Row("fixture-quote", "agda_grep_count", ("it's", 1, "n"))
    return [
        ("a one-word command holding a space is refused", _refuses(spaced)),
        ("an argument holding a comma is refused", _refuses(comma)),
        ("a target holding a single quote is refused", _refuses(quoted)),
    ]


def selftest(root: Path) -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    cases = _live_cases(root) + _grammar_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"witness-check selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


def main(argv: list[str]) -> int:
    """Resolve the tree from the working directory, refusing when it holds no ledger project."""
    if len(argv) > 1 and "--selftest" not in argv:
        return 1
    root = Path.cwd()
    if not root.joinpath(*ledger_cli.PROJECT, "paper.toml").is_file():
        sys.stderr.write(f"witness-check selftest: no ledger project under {root}\n")
        return 2
    return selftest(root)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(main(sys.argv))
