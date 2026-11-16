#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Census the SHAPES an arm body takes — what a pytest transform must actually handle.

⚑⚑⚑ A TRANSFORM OVER 47 SUITES RESTS ON A SHAPE CLAIM, AND THIS IS THE MEASUREMENT OF IT. The
`_ARMS` convention is `def <name>(out: list[str]) -> int`, and the bodies I have read all spell
`if <bad>: out.append(<msg>); return 1` … `return 0` — which maps to `assert not <bad>, <msg>`
mechanically. **But I have read a handful of 47.** Generalizing from those is exactly the
`plan_notes_are_hypotheses` shape: a sample that agrees is not a population that does.

⚑⚑ THE DANGEROUS ARMS ARE THE ONES THAT ACCUMULATE. An arm returning a running total after
several `out.append` calls asserts SEVERAL facts, and a naive rewrite to one `assert` keeps the
first and silently drops the rest — a transform that REDUCES COVERAGE while every suite still
reports green. So this counts append sites per arm, and more than one means a hand port.

⚑ AND `try/except` ARMS ARE A THIRD SHAPE. Several assert that a call RAISES, spelled as a
try/except whose fall-through returns 1; pytest spells that `pytest.raises`, which is a different
rewrite rather than a harder version of the same one.

⚑ THIS COUNTS; IT DOES NOT REWRITE. What the transform does with each shape is a separate
decision, and making it here would bury the measurement inside the thing it exists to justify.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path

# The parameter every arm takes. ⚑ THE SIGNATURE IS THE PREDICATE: a function in a suite that does
# not take it is a helper, not an arm, and counting helpers would inflate the population.
OUT_PARAM = "out"

# The roster name the convention uses.
ARMS_NAME = "_ARMS"

# How many example rows to name before summarizing the rest. ⚑ NAMED BECAUSE A CENSUS THAT
# TRUNCATES SILENTLY reports a smaller population than it measured — the count is always stated,
# and this bounds only how many are SPELLED OUT.
SAMPLE = 12


@dataclass(frozen=True, slots=True)
class Arm:
    """One arm's measured shape."""

    suite: str
    name: str
    appends: int
    returns: int
    raises_check: bool

    @property
    def mechanical(self) -> bool:
        """Report whether a single-assert rewrite preserves every assertion.

        ⚑ ONE APPEND IS THE CANONICAL SHAPE — one failure branch, one success branch. More
        appends means more facts asserted, and collapsing them loses coverage silently.
        """
        return self.appends <= 1 and not self.raises_check


def _arm_names(tree: ast.Module) -> frozenset[str]:
    """Return the names the suite's roster lists.

    ⚑ THE ROSTER IS THE AUTHORITY ON WHAT RUNS, not the signature. A function taking `out` that
    the roster omits is dead — it looks like an arm and asserts nothing, which is a finding of its
    own and not a member of this census.
    """
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == ARMS_NAME:
                if isinstance(node.value, (ast.Tuple, ast.List)):
                    return frozenset(e.id for e in node.value.elts if isinstance(e, ast.Name))
                return frozenset()
    return frozenset()


def _takes_out(node: ast.FunctionDef) -> bool:
    """Report whether a function has the arm signature."""
    return any(a.arg == OUT_PARAM for a in node.args.args)


def _appends(node: ast.FunctionDef) -> int:
    """Count `out.append(...)` calls in one arm."""
    return sum(
        1
        for sub in ast.walk(node)
        if isinstance(sub, ast.Call)
        and isinstance(sub.func, ast.Attribute)
        and sub.func.attr == "append"
        and isinstance(sub.func.value, ast.Name)
        and sub.func.value.id == OUT_PARAM
    )


def _returns(node: ast.FunctionDef) -> int:
    """Count return statements in one arm."""
    return sum(1 for sub in ast.walk(node) if isinstance(sub, ast.Return))


def _raises_check(node: ast.FunctionDef) -> bool:
    """Report whether the arm asserts that something RAISES.

    ⚑ A DIFFERENT REWRITE, NOT A HARDER ONE. pytest spells this `pytest.raises`, so an arm built
    on try/except needs a structural change rather than a predicate inversion.
    """
    return any(isinstance(sub, ast.Try) for sub in ast.walk(node))


def read(path: Path) -> tuple[Arm, ...]:
    """Return every rostered arm in one suite, with its measured shape."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return ()

    rostered = _arm_names(tree)
    if not rostered:
        return ()

    return tuple(
        Arm(
            suite=path.name,
            name=node.name,
            appends=_appends(node),
            returns=_returns(node),
            raises_check=_raises_check(node),
        )
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in rostered and _takes_out(node)
    )


def census(root: Path | None = None) -> tuple[Arm, ...]:
    """Return every arm across `substrate/`."""
    where = (root if root is not None else corpus.ROOT) / "substrate"
    out: list[Arm] = []
    for path in sorted(where.glob("*.py")):
        out.extend(read(path))
    return tuple(out)


def render(arms: tuple[Arm, ...]) -> str:
    """Return the shape census — what a transform can take and what it cannot."""
    if not arms:
        return "  no arms found\n"

    mechanical = [a for a in arms if a.mechanical]
    multi = [a for a in arms if a.appends > 1 and not a.raises_check]
    raising = [a for a in arms if a.raises_check]
    suites = {a.suite for a in arms}

    lines = [
        f"  {len(arms)} arm(s) across {len(suites)} suite(s)",
        f"    mechanical (<=1 append, no raises-check): {len(mechanical)}",
        f"    multi-assert (>1 append)                : {len(multi)}",
        f"    raises-check (try/except)               : {len(raising)}",
    ]
    lines.extend(
        f"      multi   {a.suite}::{a.name}  ({a.appends} appends)" for a in multi[:SAMPLE]
    )
    if len(multi) > SAMPLE:
        lines.append(f"      … and {len(multi) - SAMPLE} more multi-assert arm(s)")
    lines.extend(f"      raises  {a.suite}::{a.name}" for a in raising[:SAMPLE])
    if len(raising) > SAMPLE:
        lines.append(f"      … and {len(raising) - SAMPLE} more raises-check arm(s)")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.stdout.write(render(census()))
    sys.exit(0)
