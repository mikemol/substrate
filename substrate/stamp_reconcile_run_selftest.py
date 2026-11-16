# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.stamp_reconcile_run` — argv, the report, the tenant check. No store.

⚑ WHAT A CLI THAT DELETES FILES MUST GET RIGHT BEFORE IT CONNECTS: that a malformed invocation is
refused rather than guessed at, that `--apply` is the ONLY way to delete (dry is the default), and
that the report says which it did. The store read itself was measured against the real sandbox
(t109: kept 1 / WOULD drop 1 on a controlled tree); these cases pin the parts no store is needed
to check.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import stamp_reconcile as sr
from substrate import stamp_reconcile_run as run

_USAGE = 2


def _parse_cases() -> list[tuple[str, bool]]:
    """Return the argv cases."""
    walk = run.parse(["_build", "--tenant", "sandbox"])
    applied = run.parse(["_build", "--tenant", "live", "--apply"])
    based = run.parse(["_build", "--tenant", "live", "--base", "elsewhere"])
    return [
        ("a well-formed invocation parses", walk is not None),
        ("dry is the default", walk is not None and not walk.apply),
        ("--apply is what turns deletion on", applied is not None and applied.apply),
        (
            "--base defaults to STAMPDIR/Substrate",
            walk is not None and walk.base == Path("_build") / "Substrate",
        ),
        ("--base overrides it", based is not None and based.base == Path("elsewhere")),
        (
            "the --tenant operand is not read as STAMPDIR",
            walk is not None and walk.stampdir == Path("_build"),
        ),
        ("a missing --tenant is refused", run.parse(["_build"]) is None),
        ("an unknown tenant is refused", run.parse(["_build", "--tenant", "bogus"]) is None),
        (
            "an unknown flag is refused",
            run.parse(["_build", "--tenant", "live", "--force"]) is None,
        ),
        ("two STAMPDIRs are refused", run.parse(["a", "b", "--tenant", "live"]) is None),
        ("a dangling --tenant is refused", run.parse(["_build", "--tenant"]) is None),
    ]


def _report_cases() -> list[tuple[str, bool]]:
    """Return the report-rendering cases."""
    many = [f"M{i}.agdai" for i in range(run.SHOWN + 3)]
    counts = {"ingested": (2, many), "promoted": (0, []), "drained": (1, [])}
    dry = run.report(sr.Walk(Path("s"), Path("s"), "sandbox", apply=False), counts)
    wet = run.report(sr.Walk(Path("s"), Path("s"), "sandbox", apply=True), counts)
    total = 2 + len(many)
    return [
        ("a dry report says WOULD drop", "WOULD drop" in dry),
        ("a dry report says how to apply", "--apply" in dry),
        ("an applied report says dropped, not WOULD", "WOULD" not in wet and " dropped " in wet),
        ("the denominator is printed", f"of {total}" in dry),
        ("the list truncates visibly", f"and {len(many) - run.SHOWN} more" in dry),
        ("it names the tenant", "tenant sandbox" in dry),
    ]


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out = [*_parse_cases(), *_report_cases()]
    refused = False
    try:
        run.target_for("bogus")
    except sr.UnknownTenantError:
        refused = True
    out.append(("target_for refuses an unknown tenant before any connect", refused))
    out.append(("main refuses malformed argv with usage", run.main(["--tenant", "live"]) == _USAGE))
    out.append(
        (
            "main refuses a STAMPDIR that is not a directory",
            run.main(["/nonexistent/stampdir", "--tenant", "live"]) == _USAGE,
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
    sys.stdout.write(f"stamp-reconcile-run selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
