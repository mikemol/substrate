#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.witness_bibrows` — one per kind shape, and the live ledger's properties.

⚑⚑ ONCE A DIFFERENTIAL AGAINST THE ROSTER, NOW PROPERTIES OF THE BIBS. The live case read the
`WITNESSES` literal beside the bibs and found 850 rows on each side, 0 differing in kind or
arguments before the note (recorded in the paths-forward ledger). With the roster retiring into
the bibs, what is owed is that the bibs alone yield a complete, well-kinded witness set: one row per
check, under the same keys, and every kind in the roster's own vocabulary (`KIND_ORDER`).

The tree is the working directory, resolved at this CLI entry; the suite REFUSES without a ledger.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import ledger_cli, witness_bibrows
from substrate.witness_roster import KIND_ORDER


def _args(check: str) -> tuple[object, ...]:
    """Return the arguments the bib reader gives `check`, with the note `n`."""
    return witness_bibrows.row_of("k", check, "n").args


def _kind(check: str) -> str:
    """Return the kind the bib reader gives `check`."""
    return witness_bibrows.row_of("k", check, "n").kind


def _fixture_cases() -> list[tuple[str, bool]]:
    """Return one case per kind shape, parsed back from its converged spelling."""
    return [
        ("selftest -> argv list + note", _args("selftest:x,y") == (["x", "y"], "n")),
        ("refuses keeps its kind", _kind("refuses:false") == "refuses"),
        ("mode -> tool, flag, and NO note", _args("mode:t.py:--f") == ("t.py", "--f")),
        ("standing -> note only", _args("standing") == ("n",)),
        ("unwitnessed keeps its kind", _kind("unwitnessed") == "unwitnessed"),
        ("excludes -> three fields + note", _args("excludes:m.py:f:x") == ("m.py", "f", "x", "n")),
        ("agda-grep -> pattern, count, note", _args("agda-grep:2:p") == ("p", 2, "n")),
        ("agda-field keeps its roster kind", _kind("agda-field:M:R:f") == "agda_lacks_field"),
    ]


def _live_cases(root: Path) -> list[tuple[str, bool]]:
    """Return the live properties: every bib entry yields one row, of a kind the roster knew."""
    project = root.joinpath(*ledger_cli.PROJECT)
    checks = ledger_cli.checks(project)
    rows = witness_bibrows.rows(project)
    unknown = sorted({row.kind for row in rows} - set(KIND_ORDER))
    sys.stdout.write(f"  {len(rows)} bib rows over {len(checks)} checks; unknown kinds {unknown}\n")
    return [
        ("the live ledger is read", bool(rows)),
        ("one row per check, same keys", [row.key for row in rows] == sorted(checks)),
        ("every row's kind is in the roster's vocabulary", not unknown),
    ]


def selftest(root: Path) -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    cases = _fixture_cases() + _live_cases(root)
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"witness-bibrows selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


def main(argv: list[str]) -> int:
    """Resolve the tree from the working directory, refusing when it holds no ledger project."""
    if len(argv) > 1 and "--selftest" not in argv:
        return 1
    root = Path.cwd()
    if not root.joinpath(*ledger_cli.PROJECT, "paper.toml").is_file():
        sys.stderr.write(f"witness-bibrows selftest: no ledger project under {root}\n")
        return 2
    return selftest(root)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(main(sys.argv))
