#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.promoted` — and the divergence it currently carries.

⚑⚑ THE LOAD-BEARING ARM IS THE SUPERSET CHECK, NOT THE CONTENTS. Two rosters exist while the
migration runs: this one, and `scripts/check_scratch_independence.ROOTS`, which cannot be
edited to match (360 findings, no partial-credit path). A divergence between two population
declarations is exactly how one census silently answers about a different set than its
sibling — so what must hold is not equality but DIRECTION: this roster is a SUPERSET, always.

⚑ A SUPERSET DIVERGENCE ONLY ADDS COVERAGE; A SUBSET ONE REMOVES IT SILENTLY. If a tree were
ever dropped from here to make the two agree, every consumer that had migrated would stop
gating it — and nothing would report that, because a smaller population reports fewer
findings and fewer findings reads as progress. The first arm is what refuses that.

⚑ `check_mypy_ratchet`'s OWN SUITE CARRIES THE MIRROR OF THIS — *"If someone hand-copies
ROOTS into this file, a future promotion silently escapes the type gate"*. That case guards
its consumer against copying; this one guards the authority against shrinking.

⚑ AND A TUPLE-NESS ARM WAS WRITTEN AND DELETED: mypy proved it statically from the
annotation and reported the assertion body as UNREACHABLE. A runtime case for something the
checker already forbids is not extra safety, it is a case that can never fail — which reads
as coverage while measuring nothing.
"""

from __future__ import annotations

import sys

from substrate import promoted


def superset_of_legacy(out: list[str]) -> int:
    """Check this roster still contains every tree the pre-cut authority declares.

    ⚑ THE LEGACY ROSTER IS READ THROUGH THE STUB, and reaching it needs `scripts/` on the
    path — a stub types an import, it does not make a module importable. When
    ⟡roots-authority-cut finishes and the consumers have moved, this arm is DELETED rather
    than repaired: there will be one roster, and a comparison against a retired one is a
    comparison against a corpse.
    """
    from substrate import corpus  # noqa: PLC0415 - only this arm needs the path

    scripts = str(corpus.ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    try:
        from check_scratch_independence import ROOTS  # noqa: PLC0415 - the arm IS the reach
    except ImportError:
        out.append("selftest: the legacy roster could not be read — divergence UNCHECKED")
        return 1

    missing = [r for r in ROOTS if r not in promoted.ROOTS]
    if missing:
        out.append(
            f"selftest: this roster DROPPED {missing} — a subset divergence silently "
            f"removes those trees from every migrated consumer's scope"
        )
        return 1
    return 0


def population_derives(out: list[str]) -> int:
    """Check POPULATION is ROOTS plus the gate layer, spelled once.

    ⚑ `check_mypy_ratchet` COMPUTES `list(ROOTS) + ["scripts"]` INLINE and `promote_agree`
    once computed it differently, as a prefix tuple. Two spellings of one population is the
    defect; this asserts the derivation rather than the literal.
    """
    bad = 0
    if not all(r in promoted.POPULATION for r in promoted.ROOTS):
        out.append("selftest: POPULATION does not contain every ROOT")
        bad += 1
    if "scripts" not in promoted.POPULATION:
        out.append("selftest: POPULATION omits the gate layer")
        bad += 1
    if len(promoted.POPULATION) != len(promoted.ROOTS) + 1:
        out.append(f"selftest: POPULATION is not ROOTS + one: {promoted.POPULATION}")
        bad += 1
    return bad


def excludes_scratch(out: list[str]) -> int:
    """Check `scratch/` is absent — residence there IS the not-yet-promoted status.

    ⚑ THE EXCLUSION IS THE POPULATION'S JOB, NOT A FILTER'S. `check_mypy_ratchet` carries the
    same case for the same reason: a filter that can rot is a filter that will, and a
    population that never admits the tree cannot leak it.
    """
    if "scratch" in promoted.POPULATION:
        out.append("selftest: scratch/ entered the promoted population")
        return 1
    return 0


def target_is_gated(out: list[str]) -> int:
    """Check the promotion TARGET is itself in the population.

    ⚑ ⟡substrate-in-population's WHOLE POINT. Until `substrate` was admitted, everything
    promoted into it landed BESIDE the gates: a module left `scratch/` (ungated by design)
    and arrived somewhere no gate looked, so the migration's success state went unmeasured.
    """
    if "substrate" not in promoted.ROOTS:
        out.append("selftest: the promotion target is not in the promoted roster")
        return 1
    return 0


_ARMS = (superset_of_legacy, population_derives, excludes_scratch, target_is_gated)

_CASE_COUNT = 1 + 3 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"promoted selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"promoted selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
