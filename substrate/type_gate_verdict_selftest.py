#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Verdict-path cases for `substrate.type_gate`: is the ruling REACHED, and does dry-run write.

⚑⚑ PORTED FROM `scripts/check_mypy_ratchet`'s SUITE BEFORE RETIRING IT (⟡old-gate-retire).
Comparing the two suites arm by arm found three cases the promoted one lacked, and they are
the three that exercise the VERDICT rather than its inputs. Retiring the old gate without
carrying them would have deleted coverage while the totals stayed green.

⚑⚑⚑ THE FIRST OF THEM EXISTS BECAUSE EVERY OTHER CASE WAS BLIND TO ONE MUTANT. Its origin
note: `pycodemod --discriminates` reported the old suite blind to `empty-census-passes` — a
`return 0` inserted above the `set_ratchet` call. Every other case checked an INPUT predicate;
none checked that the verdict is reached AT ALL, so a gate short-circuited to always-pass
stayed green. **A suite that only tests what goes in cannot see a gate that stopped ruling.**

⚑ A SEPARATE MODULE, NOT THREE MORE ARMS IN `type_gate_selftest` (operator: *"break up the
complicated thing so your writes will be reliable"*). These three share a tempdir baseline and
a fixed-census helper; the existing eight share neither and never touch the filesystem. Two
fixtures in one file is two responsibilities — and the attempt to merge them failed twice on
malformed edits before the split was taken.

⚑ THE CENSUS IS SUBSTITUTED THROUGH `Gate._replace`, NOT BY PATCHING MODULE GLOBALS. The
original rebound `globals()["census"]` and `globals()["BASELINE"]` inside a `try/finally`; a
NamedTuple replacement needs no restoration, and a test that mutates its subject can leave it
mutated when an assertion raises before the finally runs.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import type_gate
from substrate.gate_main import run_gate

if TYPE_CHECKING:
    from collections.abc import Callable

# Exit codes `run_gate` returns.
_PASS = 0
_DEBT_GREW = 1
_CANNOT_MEASURE = 2


def _fixed(*keys: str) -> Callable[[], list[str]]:
    """Return a census that always reports `keys`."""

    def census() -> list[str]:
        return list(keys)

    return census


def verdict_is_reached(out: list[str]) -> int:
    """Check the gate REFUSES a grown census and PASSES one held at baseline.

    ⚑ THE CASE THAT SURVIVES EVERY OTHER ONE BEING GREEN. It is the only arm that would fail
    if the gate stopped ruling — see this module's header for the mutant it was written after.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        baseline = Path(d) / "b.txt"
        baseline.write_text("old::x.py\n", encoding="utf-8")
        grown = type_gate.GATE.__replace__(
            census=_fixed("old::x.py", "NEW::y.py"), baseline_path=str(baseline)
        )
        held = type_gate.GATE.__replace__(census=_fixed("old::x.py"), baseline_path=str(baseline))
        if run_gate(grown, type_gate.REPORT, ["type_gate.py", "--quiet"]) != _DEBT_GREW:
            out.append("selftest: a GROWN census did not refuse")
            bad += 1
        if run_gate(held, type_gate.REPORT, ["type_gate.py", "--quiet"]) != _PASS:
            out.append("selftest: a census AT baseline did not pass")
            bad += 1
    return bad


def dry_run_writes_nothing(out: list[str]) -> int:
    """Check `--dry-run` previews a paydown and leaves the baseline byte-identical.

    ⚑ A PREVIEW THAT WRITES IS NOT A PREVIEW. The baseline IS the debt ledger, so a mode
    advertised as read-only that banked a lowered census would pay down debt nobody approved —
    permanently, since a paydown-only ratchet cannot restore keys it has forgiven.
    """
    with tempfile.TemporaryDirectory() as d:
        baseline = Path(d) / "b.txt"
        baseline.write_text("old::x.py\ngone::z.py\n", encoding="utf-8")
        before = baseline.read_text(encoding="utf-8")
        gate = type_gate.GATE.__replace__(census=_fixed("old::x.py"), baseline_path=str(baseline))
        run_gate(gate, type_gate.REPORT, ["type_gate.py", "--quiet", "--dry-run"])
        if baseline.read_text(encoding="utf-8") != before:
            out.append("selftest: --dry-run rewrote the baseline")
            return 1
    return 0


def dry_run_is_universal(out: list[str]) -> int:
    """Check `--dry-run` is accepted without this gate declaring it per-site.

    ⚑ THE AUTHORITY DECLARES IT FOR EVERY CALLER (`ratchet_flags.UNIVERSAL_FLAGS`). A gate
    restating it would be the ten-call-site duplication this arc retires; a gate omitting it
    would REFUSE a flag the authority implements — and six of eleven gates once did exactly
    that, so the authority's own capability was unreachable through them.
    """
    with tempfile.TemporaryDirectory() as d:
        gate = type_gate.GATE.__replace__(census=_fixed(), baseline_path=str(Path(d) / "b.txt"))
        rc = run_gate(gate, type_gate.REPORT, ["type_gate.py", "--quiet", "--dry-run"])
    if rc == _CANNOT_MEASURE:
        out.append("selftest: --dry-run was refused as an unknown flag")
        return 1
    return 0


_ARMS = (verdict_is_reached, dry_run_writes_nothing, dry_run_is_universal)

_CASE_COUNT = 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"type-gate-verdict selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"type-gate-verdict selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
