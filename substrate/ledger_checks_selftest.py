#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.ledger_checks` — delegation, duplicates, `--invoking`, and retirement.

⚑⚑ `duplicates` IS CASED ON BOTH OUTCOMES. Identical copies must report NO differing field and
differing copies must name exactly the fields that differ — the report was built because an
earlier census could say only that a key appeared twice, which cannot tell a harmless copy from
two claims under one key.

⚑ `invoking` IS CASED ON THE LIVE LEDGER BY PROPERTY, NOT BY COUNT: every row it returns must run
a command (`selftest`/`refuses`), because its count is EXPECTED to move as the pycodemod port
lands, and pinning it would make the suite fail on the repair it tracks.

⚑ EACH RETIRED ROSTER MODE MUST REFUSE AND NAME ITS RECORDED RESULT — a retired spelling that
vanished silently would read to a caller as a mode that never existed.

The tree is the working directory, resolved at this CLI entry; the suite REFUSES without a ledger.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import ledger_checks

# The findings roster, relative to the tree (it names the ledger project, its directory).
_ROSTER = (".claude", "agents", "findings.py")

# The kinds whose first argument is a command.
_COMMAND_KINDS = ("selftest", "refuses")

# The exit a refused invocation returns.
_USAGE_EXIT = 2

ONE = "@misc{K,\n  claim    = {same},\n  note     = {n1}\n}\n\n@misc{S,\n  claim    = {solo}\n}\n"
TWO = "@misc{K,\n  claim    = {same},\n  note     = {n2}\n}\n"
SAME = "@misc{K,\n  claim    = {same},\n  note     = {n1}\n}\n"


def _delegate_cases() -> list[tuple[str, bool]]:
    """Return the cases for `delegates`."""
    return [
        ("item:<own key> delegates", ledger_checks.delegates("K", "item:K")),
        ("item:<another key> does not", not ledger_checks.delegates("K", "item:M")),
        ("a converged spelling does not", not ledger_checks.delegates("K", "standing")),
    ]


def _duplicate_cases(tmp: Path) -> list[tuple[str, bool]]:
    """Return the cases for `duplicates`, over bibs written under `tmp`."""
    one, two, same = tmp / "one.bib", tmp / "two.bib", tmp / "same.bib"
    one.write_text(ONE, encoding="utf-8")
    two.write_text(TWO, encoding="utf-8")
    same.write_text(SAME, encoding="utf-8")
    differing = ledger_checks.duplicates([one, two])
    identical = ledger_checks.duplicates([one, same])
    key, homes, differ = differing[0] if differing else ("", [], {})
    bad = ledger_checks.main(["lc", "--duplicates", str(one), "--summary-only"])
    return [
        ("a key in two bibs is reported once", [row[0] for row in differing] == ["K"]),
        ("a key in one bib is not reported", key != "S"),
        ("both homes are named", homes == ["one.bib", "two.bib"]),
        ("exactly the differing field is named", list(differ) == ["note"]),
        ("each home's value is carried", differ.get("note") == ["n1", "n2"]),
        ("identical copies differ in nothing", bool(identical) and not identical[0][2]),
        ("a flag-shaped operand is REFUSED, not read as a path", bad == _USAGE_EXIT),
    ]


def _field_cases(tmp: Path) -> list[tuple[str, bool]]:
    """Return the cases for `--values` and `--lacking`, over a bib written under `tmp`.

    ⚑ `--lacking` IS CASED ON THE ENTRY `--field` CANNOT SHOW: S carries no `note`, so a census
    listing only holders would never name it — the exact entries a rubric cannot place.
    """
    one = tmp / "fields.bib"
    one.write_text(ONE, encoding="utf-8")
    counted = ledger_checks.values("note", [one])
    missing = ledger_checks.lacking("note", [one])
    homes = counted.get("n1", (0, []))[1]
    return [
        ("--values counts a present value", counted.get("n1", (0, []))[0] == 1),
        ("--values names the absent bucket", counted.get("", (0, []))[0] == 1),
        ("--values carries the bib a value lives in", homes == ["fields.bib"]),
        ("--lacking names the entry without the field", [key for _, key, _ in missing] == ["S"]),
        ("--lacking carries that entry's claim", [c for _, _, c in missing] == ["solo"]),
    ]


def _invoking_cases(root: Path) -> list[tuple[str, bool]]:
    """Return the property cases for `invoking` over the live ledger."""
    roster = root.joinpath(*_ROSTER)
    rows = ledger_checks.invoking(roster, "pycodemod")
    return [
        ("the live ledger has witnesses running pycodemod", bool(rows)),
        ("every such witness runs a command", all(kind in _COMMAND_KINDS for _, kind, _ in rows)),
        ("every command carried names the word", all("pycodemod" in cmd for _, _, cmd in rows)),
        ("a word no command holds finds none", not ledger_checks.invoking(roster, "\x00")),
    ]


def _retired_cases(root: Path) -> list[tuple[str, bool]]:
    """Return one case per retired roster mode: it refuses, and its result is on record."""
    roster = str(root.joinpath(*_ROSTER))
    return [
        (
            f"{mode} refuses (retired) and names its recorded result",
            ledger_checks.main(["lc", mode, roster]) == _USAGE_EXIT and bool(result),
        )
        for mode, result in ledger_checks.RETIRED.items()
    ]


def selftest(root: Path) -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    with tempfile.TemporaryDirectory() as tmp:
        cases = _delegate_cases() + _duplicate_cases(Path(tmp)) + _field_cases(Path(tmp))
    cases += _invoking_cases(root) + _retired_cases(root)
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"ledger-checks selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


def main(argv: list[str]) -> int:
    """Resolve the tree from the working directory, refusing when it holds no roster."""
    if len(argv) > 1 and "--selftest" not in argv:
        return 1
    root = Path.cwd()
    if not root.joinpath(*_ROSTER).is_file():
        sys.stderr.write(f"ledger-checks selftest: no roster under {root}; run from the tree\n")
        return 2
    return selftest(root)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(main(sys.argv))
