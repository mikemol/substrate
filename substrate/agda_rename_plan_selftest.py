#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `agda_rename_plan` - every decision, both spellings, and the recorded Sum case.

NO DIFFERENTIAL AGAINST THE ORIGIN: `cure_collisions` renames files and rebuilds the tree, so a
by-path call is a write, not a comparison. Its decision table is pinned here instead - and one
row of it is a CORRECTION: with no leaf set the origin also skipped, but printed "both sides
are split leaves"; this module skips with the reason that is true.
"""

from __future__ import annotations

import sys

from substrate import agda_rename_plan as rp

_LEAF = "agda/Substrate/Foundation/Sum/Inl.agda"
_OTHER = "agda/Substrate/Algebra/Z/DecInt.agda"
_THIRD = "agda/Substrate/Algebra/Z/Neg.agda"
_LEAF2 = "agda/Substrate/Foundation/Sum/Inr.agda"

Cases = list[tuple[str, bool]]


def _module_of(path: str) -> str:
    """Return a module name from a path the way the caller's authority would."""
    return path.removeprefix("agda/").removesuffix(".agda").replace("/", ".")


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _decision_cases(cases: Cases) -> None:
    """Pin the five decisions."""
    got = rp.plan((_OTHER, "_<_", _LEAF), [_LEAF], _module_of)
    _check(
        cases,
        "the leaf is the previous def: the CONSUMER's def moves, at its own home",
        ok=got == rp.Rename(_OTHER, "Substrate.Algebra.Z.DecInt", "_<_", "_decint-<_"),
    )
    got = rp.plan((_LEAF, "inl", _OTHER), [_LEAF], _module_of)
    _check(
        cases,
        "the leaf is the consumer: the PREVIOUS def moves",
        ok=isinstance(got, rp.Rename) and got.victim == _OTHER and got.new == "decint-inl",
    )
    got = rp.plan((_LEAF, "inl", _LEAF2), [_LEAF, _LEAF2], _module_of)
    _check(
        cases,
        "both sides leaves of this split: skip, needs a human",
        ok=got == rp.Skip("inl", rp.BOTH_SIDES_LEAVES),
    )
    got = rp.plan((_OTHER, "_<_", _THIRD), [_LEAF], _module_of)
    _check(
        cases,
        "the Foundation.Sum case: a clash between two NON-leaves is not this split's",
        ok=got == rp.Skip("_<_", rp.NOT_FROM_THIS_SPLIT),
    )
    got = rp.plan((_OTHER, "_<_", _THIRD), [], _module_of)
    _check(
        cases,
        "no leaf set: skip, with the TRUE reason (the origin said both-sides)",
        ok=got == rp.Skip("_<_", rp.NO_LEAVES),
    )


def _spell_cases(cases: Cases) -> None:
    """Pin the operator-safe and plain spellings."""
    _check(
        cases,
        "an infix operator keeps both holes around the prefixed core",
        ok=rp.spell("x/DecInt.agda", "_<_") == "_decint-<_",
    )
    _check(
        cases,
        "a prefix operator keeps only its trailing hole",
        ok=rp.spell("x/DecInt.agda", "-_") == "decint--_",
    )
    _check(
        cases,
        "a postfix operator keeps only its leading hole",
        ok=rp.spell("x/DecInt.agda", "_!") == "_decint-!",
    )
    _check(
        cases,
        "a plain name is prefixed plainly, stem lowercased",
        ok=rp.spell("x/DecInt.agda", "suc") == "decint-suc",
    )
    _check(
        cases,
        "the stem is the file's own name, not its directory",
        ok=rp.spell("agda/Substrate/Algebra/Z/Neg.agda", "n") == "neg-n",
    )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _decision_cases(cases)
    _spell_cases(cases)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"agda_rename_plan_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
