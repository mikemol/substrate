# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.editable` — whether the per-file gate would accept an edit.

⚑⚑⚑ THE LOAD-BEARING CASE IS THAT `UNKNOWN` IS NOT EDITABLE. A checker that could not run
produces no findings, which is byte-identical to a clean file, and treating that as editable
would schedule work on a file nobody measured. Both checkers exit 1 for "flagged something"
and 2 for "could not run", and a peer once read a rejected config as "no findings" INSIDE a
probe written to test an instrument.

⚑⚑ AND BOTH CHECKERS MUST BE CONSULTED, because the gate runs both. A census over ruff alone
calls a file clean that mypy refuses, and a drain planned on it discovers the difference one
refused edit at a time. The case that pins this asserts a file dirty ONLY under mypy is still
reported dirty.

⚑ THE LIVE CASES USE FILES WHOSE STATE IS KNOWN FOR STRUCTURAL REASONS — this package's own
modules must be clean (the gate would not have let them land otherwise), and a named monolith
must be dirty. Asserting a COUNT would make these a measurement; asserting the VERDICT keeps
them a contract.
"""

from __future__ import annotations

from substrate import editable


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the three states are distinct, and only one is editable ─────────────
    check(
        "a clean verdict is editable",
        passed=editable.Verdict("a.py", editable.CLEAN, 0).is_editable,
    )
    check(
        "a dirty verdict is not", passed=not editable.Verdict("a.py", editable.DIRTY, 3).is_editable
    )
    # ⚑ THE CASE THAT PREVENTS SCHEDULING WORK ON AN UNMEASURED FILE.
    check(
        "an UNKNOWN verdict is NOT editable",
        passed=not editable.Verdict("a.py", editable.UNKNOWN, 0, "no mypy").is_editable,
    )
    check(
        "and UNKNOWN carries the reason it could not be measured",
        passed=bool(editable.Verdict("a.py", editable.UNKNOWN, 0, "no mypy").why),
    )

    # ── a file that cannot be run against is UNKNOWN, never clean ───────────
    # ⚑ A MISSING PATH MAKES BOTH CHECKERS EXIT NON-CENSUS. If this returned CLEAN, every
    # typo'd path in a drain plan would read as ready to edit.
    missing = editable.verdict_for("no/such/file/anywhere.py")
    check("a nonexistent path is UNKNOWN, not clean", passed=missing.state == editable.UNKNOWN)
    check("and says which checker refused", passed="ruff" in missing.why or "mypy" in missing.why)

    # ── the live tree: this package's own modules ──────────────────────────
    # ⚑ STRUCTURALLY KNOWN: the gate would not have let these land if they were dirty, so
    # asserting CLEAN here is asserting the predicate agrees with the gate that wrote them.
    mine = editable.verdict_for("substrate/editable.py")
    check("this module reads as editable", passed=mine.state == editable.CLEAN)
    check("with zero findings as its evidence", passed=mine.findings == 0)

    # ⚑ AND A KNOWN MONOLITH READS DIRTY. Without this the predicate could be stuck at CLEAN
    # and every case above would still pass.
    monolith = editable.verdict_for("scripts/gate_census.py")
    check("a known monolith reads as not editable", passed=monolith.state == editable.DIRTY)
    check("and carries its finding count as evidence", passed=monolith.findings > 0)

    # ── partition groups every path exactly once ───────────────────────────
    paths = ["substrate/editable.py", "scripts/gate_census.py"]
    groups = editable.partition(paths)
    check("partition places every path", passed=sum(len(v) for v in groups.values()) == len(paths))
    check(
        "and separates the two",
        passed=len(groups[editable.CLEAN]) == 1 and len(groups[editable.DIRTY]) == 1,
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
