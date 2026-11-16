# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.schema_stamp` — the version is READ from its authority, never guessed.

⚑ NO CASE CONNECTS. What this module decides — which number, and what a stamp would do — is
checkable on fixture files and plain values; the write itself is exercised against the sandbox.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import schema_stamp as ss


def _refuses(text: str) -> bool:
    """Report whether reading the authority from a file holding `text` refuses."""
    with tempfile.TemporaryDirectory() as where:
        path = Path(where) / "authority.py"
        path.write_text(text, encoding="utf-8")
        try:
            ss.authority_version(path)
        except ss.NoAuthorityError:
            return True
    return False


def _read(text: str) -> int:
    """Return the version read from a file holding `text`."""
    with tempfile.TemporaryDirectory() as where:
        path = Path(where) / "authority.py"
        path.write_text(text, encoding="utf-8")
        return ss.authority_version(path)


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    seven = 7
    check("a module-level int constant is read", passed=_read("SCHEMA_VERSION = 7\n") == seven)
    check(
        "a constant nested in a function is NOT the authority",
        passed=_refuses("def f():\n    SCHEMA_VERSION = 3\n"),
    )
    check("a non-int value refuses rather than guessing", passed=_refuses("SCHEMA_VERSION = '2'\n"))
    check("an absent constant refuses", passed=_refuses("OTHER = 2\n"))
    # ⚑ THE LIVE AUTHORITY IS READABLE: a positive control on the real file.
    check(
        "the real sppf_db declares an int SCHEMA_VERSION",
        passed=isinstance(ss.authority_version(), int),
    )
    check(
        "an empty table plans EMPTY → target",
        passed=ss.plan(None, 2) == "schema_version EMPTY → 2\n",
    )
    check("a current table plans nothing", passed="nothing to stamp" in ss.plan(2, 2))
    check("a stale version plans old → new", passed=ss.plan(1, 2) == "schema_version 1 → 2\n")
    usage = 2
    check("--live is refused", passed=ss.main(["--live", "--apply"]) == usage)
    check("no tenant is refused", passed=ss.main(["--apply"]) == usage)
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"schema-stamp selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
