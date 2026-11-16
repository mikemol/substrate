#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.witness_run` — each bound kind in BOTH polarities, and the unbound.

⚑ A kind is cased on the verdict it must give AND the one it must not: a runner that returned
CLOSED for everything passes every "selftest passes" case, so `refuses` is cased on an exit-0
command reading OPEN, and each unbound kind is cased as UNRUNNABLE rather than merely non-CLOSED.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.ledger import finding_kinds

from substrate import witness_run

CLOSED = finding_kinds.CLOSED
OPEN = finding_kinds.OPEN
UNRUNNABLE = finding_kinds.UNRUNNABLE


def _code(check: str, root: Path) -> int:
    """Return only the verdict code for `check` run in `root`."""
    return witness_run.verdict(check, root)[0]


def _cases(root: Path) -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case, run in the scratch tree `root`."""
    return [
        ("selftest: exit 0 is CLOSED", _code("selftest:true", root) == CLOSED),
        ("selftest: exit 1 is OPEN", _code("selftest:false", root) == OPEN),
        ("refuses: exit 1 is CLOSED", _code("refuses:false", root) == CLOSED),
        ("refuses: exit 0 is OPEN — the refusal is gone", _code("refuses:true", root) == OPEN),
        (
            "a command that cannot start is UNRUNNABLE",
            _code("selftest:no-such-binary-anywhere", root) == UNRUNNABLE,
        ),
        ("standing is CLOSED", _code("standing", root) == CLOSED),
        ("unwitnessed is UNRUNNABLE", _code("unwitnessed", root) == UNRUNNABLE),
        (
            "mode in a tree with no toolmodes is UNRUNNABLE, never GONE",
            _code("mode:tool:--flag", root) == UNRUNNABLE,
        ),
        (
            "excludes over an unreadable module is UNRUNNABLE",
            _code("excludes:a:b:c", root) == UNRUNNABLE,
        ),
        (
            "agda-field in a tree with no agda_defs is UNRUNNABLE",
            _code("agda-field:M:R:f", root) == UNRUNNABLE,
        ),
        (
            "agda-grep in a tree with no agda_defs is UNRUNNABLE",
            _code("agda-grep:1:x$", root) == UNRUNNABLE,
        ),
        ("an unparseable check is UNRUNNABLE", _code("nonsense-kind:x", root) == UNRUNNABLE),
        ("the CLI refuses a missing --root", witness_run.main(["w", "standing"]) == UNRUNNABLE),
        (
            "the CLI returns the verdict code",
            witness_run.main(["w", "--root", str(root), "selftest:false"]) == OPEN,
        ),
    ]


def selftest() -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    with tempfile.TemporaryDirectory() as tmp:
        cases = _cases(Path(tmp))
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"witness-run selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 1)
