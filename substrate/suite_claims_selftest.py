#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_claims` — the exclusion policy, and its precedence.

⚑⚑ THE PRECEDENCE ARM IS THE ONE THAT PREVENTS A DEADLOCK. A suite that runs the roster will
itself invoke every pg-claiming suite; if it held `claim:pg` for its whole duration it would
block against its own children, which membudget cannot break because both are waiting
legitimately. `roster` must outrank `pg`, and only a case says so.

⚑ AND OVER-DECLARING IS THE SAFE ERROR, WHICH IS WHY THE DECLARATION WINS OVER THE CENSUS. A
false-safe from inference is a corruption — two writers on one baseline; a false-positive from
over-declaring is only slower. The asymmetry is the reason this policy reads a suite's own
pragma first and treats the reach census as a cross-check.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import suite_claims

# A suite declaring a tenant — it opens the store.
_TENANT = "# selftest-tenant: sandbox\n"

# A suite declaring nothing.
_BARE = "print('hi')\n"


def _suite(d: str, name: str, src: str) -> str:
    """Write a fixture suite and return its path."""
    path = Path(d) / name
    path.write_text(src, encoding="utf-8")
    return str(path)


def roster_outranks_pg(out: list[str]) -> int:
    """Check a roster-running suite claims the ROSTER even when it also reaches a store.

    ⚑ THE DEADLOCK CASE. Holding `pg` while invoking children that each want `pg` is a wait
    nobody can break — and it is reachable, because the roster-runner is exactly the suite most
    likely to also declare a tenant.
    """
    with tempfile.TemporaryDirectory() as d:
        path = _suite(d, "both.py", _TENANT)
        got = suite_claims.claim_for(
            "scripts/both.py", path, frozenset({path}), frozenset({"scripts/both.py"})
        )
    if got != suite_claims.ROSTER:
        out.append(f"selftest: a roster-runner claimed {got!r}, not {suite_claims.ROSTER!r}")
        return 1
    return 0


def declared_tenant_claims_pg(out: list[str]) -> int:
    """Check a suite declaring a tenant claims the store."""
    with tempfile.TemporaryDirectory() as d:
        path = _suite(d, "t.py", _TENANT)
        got = suite_claims.claim_for("scripts/t.py", path, frozenset(), frozenset())
    if got != suite_claims.PG:
        out.append(f"selftest: a tenant-declaring suite claimed {got!r}")
        return 1
    return 0


def census_also_claims_pg(out: list[str]) -> int:
    """Check a suite the reach census names claims the store even without a pragma.

    ⚑ THE CENSUS IS THE SECOND LENS, and admitting it here is what makes the policy a UNION
    rather than a declaration-only list. A suite that reaches a store through an import it
    never declared is still a writer.
    """
    with tempfile.TemporaryDirectory() as d:
        path = _suite(d, "u.py", _BARE)
        got = suite_claims.claim_for("scripts/u.py", path, frozenset({path}), frozenset())
    if got != suite_claims.PG:
        out.append(f"selftest: a census-named suite claimed {got!r}")
        return 1
    return 0


def bare_suite_claims_nothing(out: list[str]) -> int:
    """Check a suite touching neither the store nor the roster claims nothing.

    ⚑ MOST SUITES ARE THIS, and if they claimed anything the build would serialize entirely —
    a correct answer that is indistinguishable from a broken one at the wall clock.
    """
    with tempfile.TemporaryDirectory() as d:
        path = _suite(d, "b.py", _BARE)
        got = suite_claims.claim_for("scripts/b.py", path, frozenset(), frozenset())
    if got is not None:
        out.append(f"selftest: a bare suite claimed {got!r}")
        return 1
    return 0


def labels_are_named(out: list[str]) -> int:
    """Check every suite gets a NAMED label, claiming or not.

    ⚑ THE LABEL IS WHAT THE LEASE LEDGER KEYS ON, so `auto` sizing reads that suite's own
    recorded peaks. An unnamed lease would size from nothing and silently take the default —
    a figure that reads as measured while being defaulted.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        bare = _suite(d, "plain.py", _BARE)
        tenant = _suite(d, "store.py", _TENANT)
        plain = suite_claims.label_for("scripts/plain.py", bare, frozenset(), frozenset())
        claimed = suite_claims.label_for("scripts/store.py", tenant, frozenset(), frozenset())
    if not plain.startswith("selftest:") or plain.endswith(":"):
        out.append(f"selftest: a non-claiming suite has no named label: {plain!r}")
        bad += 1
    if claimed != f"claim:{suite_claims.PG}":
        out.append(f"selftest: a claiming suite's label is {claimed!r}")
        bad += 1
    return bad


_ARMS = (
    roster_outranks_pg,
    declared_tenant_claims_pg,
    census_also_claims_pg,
    bare_suite_claims_nothing,
    labels_are_named,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-claims selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-claims selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
