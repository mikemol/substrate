#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.witness_excludes` — every verdict, both divergences, and LIVE.

⚑ THE PATH-NEEDLE DIVERGENCE IS CASED: a needle that occurs in the module's PATH and not in the
function must read CLOSED — the origin searched a rendering whose header named the path.

⚑⚑ THE LIVE CASES READ THE BIBS. Every `excludes` witness in the ledger must produce a DEFINITE
verdict (CLOSED or OPEN — never UNRUNNABLE), proving the reader resolves the real definition.
This suite once differenced against the origin `findings.py <KEY>` and it agreed (recorded in the
paths-forward ledger); once `findings.py` is a shim over the bibs that comparison is circular.
The tree is the working directory, resolved at this CLI entry; the suite REFUSES without a ledger.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.ledger import finding_kinds

from substrate import ledger_cli, witness_excludes, witness_run

# The check-spelling prefix of the kind this suite owns.
_KIND = "excludes"

# The verdicts that are a measurement, not a failure to measure.
_DEFINITE = (finding_kinds.CLOSED, finding_kinds.OPEN)

MODULE = '''
def walk(root):
    """Walk the tree."""
    return sorted(root.glob("src/**/*.py"))


def twice():
    return 1


def twice():
    return 2
'''


def _code(root: Path, mod: str, func: str, needle: str) -> int:
    """Return only the verdict code."""
    return witness_excludes.verdict(mod, func, needle, root)[0]


def _cases(root: Path) -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every fixture case, over a module written under `root`."""
    root.joinpath("scratchdir").mkdir()
    root.joinpath("scratchdir", "gate.py").write_text(MODULE, encoding="utf-8")
    mod = "scratchdir/gate.py"
    return [
        ("an absent needle is CLOSED", _code(root, mod, "walk", "agda/") == finding_kinds.CLOSED),
        ("a reached needle is OPEN", _code(root, mod, "walk", "src/") == finding_kinds.OPEN),
        (
            "a needle only in the PATH is CLOSED, not OPEN",
            _code(root, mod, "walk", "scratchdir") == finding_kinds.CLOSED,
        ),
        (
            "a missing function is UNRUNNABLE",
            _code(root, mod, "gone", "x") == finding_kinds.UNRUNNABLE,
        ),
        (
            "two definitions of one name are UNRUNNABLE",
            _code(root, mod, "twice", "x") == finding_kinds.UNRUNNABLE,
        ),
        (
            "an unreadable module is UNRUNNABLE",
            _code(root, "no/such.py", "walk", "x") == finding_kinds.UNRUNNABLE,
        ),
    ]


def _live_cases(root: Path) -> list[tuple[str, bool]]:
    """Return one case per live `excludes` witness in the bibs: its verdict must be definite."""
    checks = ledger_cli.checks(root.joinpath(*ledger_cli.PROJECT))
    live = {key: check for key, check in checks.items() if ledger_cli.kind_of(check) == _KIND}
    cases = [("the live ledger carries excludes witnesses", bool(live))]
    for key, check in sorted(live.items()):
        code, note = witness_run.verdict(check, root)
        sys.stdout.write(f"  live {key}: {code} — {note[:80]}\n")
        cases.append((f"live {key}: a definite verdict", code in _DEFINITE))
    return cases


def selftest(root: Path) -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    with tempfile.TemporaryDirectory() as tmp:
        cases = _cases(Path(tmp))
    cases += _live_cases(root)
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"witness-excludes selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


def main(argv: list[str]) -> int:
    """Resolve the tree from the working directory, refusing when it holds no ledger project."""
    if len(argv) > 1 and "--selftest" not in argv:
        return 1
    root = Path.cwd()
    if not root.joinpath(*ledger_cli.PROJECT, "paper.toml").is_file():
        sys.stderr.write(f"witness-excludes selftest: no ledger project under {root}\n")
        return 2
    return selftest(root)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(main(sys.argv))
