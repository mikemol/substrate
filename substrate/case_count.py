#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Compare a suite's DECLARED case total against what its arms actually assert.

⚑⚑⚑ FORTY-SEVEN SUITES HAND-SUM THEIR OWN TOTAL and nothing checks any of them. The convention is
`_CASE_COUNT = 1 + 1 + 2 + 1 + …`, one term per arm, maintained by hand — so a suite that gains an
arm, or an arm that gains a second assertion, reports a total that no longer describes it. The
number then reads as a measurement while being arithmetic nobody re-derived.

⚑⚑ AND THE FAILURE IS ONE-SIDED, WHICH IS WHY IT SURVIVES. A total that is too LOW still prints a
green `n/n` — the suite passes, the number is smaller, and nothing has a prior for what it should
be. `census-green-is-a-fact-about-the-census`: the total measures the author's addition, not the
population, and only a comparison against the arms tells them apart.

⚑ THE DERIVATION IS A FLOOR, NOT AN EQUALITY, AND SAYING SO IS THE POINT. An arm returns a FAILURE
COUNT, so how many assertions it makes is not statically decidable — an arm with two `out.append`
sites may return 1 on one path and 2 on another. This counts arms and reports the declared total
beside it: a total BELOW the arm count is a hard defect (an arm contributing nothing), while a
total above it is the normal case (arms asserting several facts).

⚑ SO THIS IS AN INSTRUMENT, NOT A GATE. It reports; it does not refuse. Gating would need the
per-arm count DECLARED rather than inferred — which is exactly what `witness_family.Member.cases`
holds, and why the family shape is the fix and this reader is only the measurement of the damage.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path

# The names the convention uses. ⚑ READ FROM HERE, so a suite spelling them differently is
# reported as UNREADABLE rather than silently counted as zero.
ARMS_NAME = "_ARMS"
COUNT_NAME = "_CASE_COUNT"


@dataclass(frozen=True, slots=True)
class Suite:
    """One suite's declared total against its arm roster."""

    path: str
    arms: int
    declared: int | None

    @property
    def unreadable(self) -> bool:
        """Report whether the total is not a literal sum this reader can compare."""
        return self.declared is None

    @property
    def below_floor(self) -> bool:
        """Report whether the declared total is less than the number of arms.

        ⚑ A HARD DEFECT. Every arm contributes at least one case, so a total below the arm count
        means an arm was added and the sum was not — the exact drift this reader exists for.
        """
        return self.declared is not None and self.declared < self.arms


def _int_of(node: ast.expr) -> int | None:
    """Return the value of an integer-literal sum, or None if it is not one.

    ⚑ THE CONVENTION IS A SUM OF LITERALS (`1 + 1 + 2`), so this evaluates exactly that shape and
    refuses anything else. A suite computing its total another way is reported UNREADABLE rather
    than mis-parsed — a wrong number here would BE the defect being reported.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _int_of(node.left), _int_of(node.right)
        if left is None or right is None:
            return None
        return left + right
    return None


def _arm_count(node: ast.expr) -> int | None:
    """Return how many arms a roster names, or None if it is not a literal sequence."""
    if isinstance(node, (ast.Tuple, ast.List)):
        return len(node.elts)
    return None


def _label(path: Path) -> str:
    """Return a repo-relative label, or the absolute path when it is outside the corpus.

    ⚑ A READER MUST NOT CRASH ON A PATH IT WAS HANDED. A bare `relative_to(corpus.ROOT)` raises
    `ValueError` for anything outside the tree — which its own suite is, since fixtures are
    written to a tempdir. Caught by that suite on the first run: an instrument that only works on
    paths inside one directory cannot be tested without putting fixtures in the tree, and fixtures
    in the tree are what make a case report the corpus instead of the reader.
    """
    try:
        return str(path.relative_to(corpus.ROOT))
    except ValueError:
        return str(path)


def read(path: Path) -> Suite | None:
    """Return one file's arm/total pair, or None if it declares no arm roster."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None

    arms: int | None = None
    declared: int | None = None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if target.id == ARMS_NAME:
                arms = _arm_count(node.value)
            elif target.id == COUNT_NAME:
                declared = _int_of(node.value)

    if arms is None:
        return None
    return Suite(path=_label(path), arms=arms, declared=declared)


def census(root: Path | None = None) -> tuple[Suite, ...]:
    """Return every suite in `substrate/` that declares an arm roster."""
    where = (root if root is not None else corpus.ROOT) / "substrate"
    found = [read(path) for path in sorted(where.glob("*.py"))]
    return tuple(got for got in found if got is not None)


def render(suites: tuple[Suite, ...]) -> str:
    """Return the census as text, surfacing the defects rather than listing every row."""
    if not suites:
        return "  no suite declares an arm roster\n"

    below = [s for s in suites if s.below_floor]
    unreadable = [s for s in suites if s.unreadable]
    lines = [f"  {len(suites)} suite(s) declare an arm roster"]
    lines.extend(
        f"  ⚑ BELOW FLOOR: {s.path} declares {s.declared} for {s.arms} arm(s) — "
        f"an arm contributes nothing"
        for s in below
    )
    lines.extend(
        f"  unreadable total: {s.path} ({s.arms} arm(s)) — the sum is not a literal "
        f"addition, so it cannot be compared"
        for s in unreadable
    )
    if not below and not unreadable:
        lines.append("  every declared total is at or above its arm count")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.stdout.write(render(census()))
    sys.exit(0)
