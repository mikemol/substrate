# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.luthen_resolver` — answer or refuse, never fall back to loopback.

⚑ THE RESOLVER-REPLY CASES ARE DATA, NOT CODE (substrate:W320): `luthen_resolver_cases.CASES` is the
table luthen receives as the acceptance suite for its own client, so this suite and theirs run the
same rows. Only the argv case below is substrate's own.

⚑ EVERY CASE RUNS ON A FIXTURE RUNNER, so the suite never reaches the real resolver and a luthen
change cannot be reported as our defect.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import luthen_resolver as lr
from substrate.luthen_resolver_cases import CASES, Case

if TYPE_CHECKING:
    from collections.abc import Callable


def _fixed(code: int, out: str) -> Callable[[list[str]], tuple[int, str]]:
    """Return a runner that always answers `(code, out)`."""

    def runner(_argv: list[str]) -> tuple[int, str]:
        return code, out

    return runner


def _holds(case: Case) -> bool:
    """Report whether `lr.resolve` reaches the outcome the table row states."""
    runner = _fixed(case.code, case.stdout)
    try:
        got = lr.resolve("postgres", runner)
    except lr.UnusableAnswerError as exc:
        return case.kind == "unusable" and case.quotes in str(exc)
    except lr.ResolverError as exc:
        return case.kind == "no-answer" and case.quotes in str(exc)
    return case.kind == "answer" and (got.host, got.port, got.as_of) == (
        case.host,
        case.port,
        case.as_of,
    )


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every table row, then substrate's own argv case."""
    out = [(case.label, _holds(case)) for case in CASES]
    expected = ["/x/.venv/bin/python", "/x/checks/endpoints_query.py", "postgres", "--side", "host"]
    out.append(
        (
            "the argv is by absolute path with the name and side",
            lr.argv("postgres", Path("/x")) == expected,
        )
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"luthen-resolver selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
