#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Count how many CLAIMS an arm makes — exclusive failure branches are one, sequential are many.

⚑⚑⚑ WHY THIS IS NOT A WIDENING OF `arm_shape` (gate-G6). That module asks whether a
SINGLE-ASSERT REWRITE preserves every assertion, and for that question counting `out.append`
sites is exactly right: two appends means a naive one-`assert` rewrite could drop one, so a
conservative over-count is the safe answer. This module asks a DIFFERENT question — how many
claims does the arm assert — and the same count answers it wrongly.

⚑⚑ THE MEASURED CASE IS AN `if`/`elif`. `arm_shape_selftest.a_multi_append_arm_is_not_mechanical`
appends once if the arm was wrongly called mechanical and once `elif` the append count read
wrong. **Only one branch can ever fire.** That is ONE claim reported two ways, and its own
docstring calls it the positive control for a single property. Reading its two appends as two
claims would have made the claim-per-test bijection report a violation that is not there.

⚑ SO THE PREDICATE IS CONTROL FLOW, NOT CALL COUNT. Appends in mutually exclusive branches of
one `if`/`elif` chain contribute ONE claim between them. Appends in sequence, or in separate
`if` statements, each contribute one. A loop body counts once however many times it runs — the
claim is *every member satisfies P*, asserted once over a population.

⚑⚑⚑ AND WHERE IT CANNOT DECIDE, IT SAYS SO RATHER THAN GUESSING. An arm whose appends sit in a
shape this does not model reports `UNDECIDED`, never a number. A wrong claim count would feed
the bijection directly, and a bijection built on a guessed denominator is worse than one that
names the arms it could not read — that is the three-outcome discipline, at arm grain.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import arm_shape, corpus

if TYPE_CHECKING:
    from pathlib import Path

# What an arm appends to. Shared with `arm_shape` by IMPORT rather than respelled — a second
# spelling of one convention is the defect this toolkit keeps paying for.
OUT_PARAM = arm_shape.OUT_PARAM

# How many rows to spell out before summarising. The count is always stated.
SAMPLE = 12


@dataclass(frozen=True, slots=True)
class Claims:
    """How many claims one arm asserts, or that this reader could not decide."""

    suite: str
    name: str
    count: int | None
    reason: str

    @property
    def decided(self) -> bool:
        """Whether a claim count was established at all."""
        return self.count is not None

    @property
    def single(self) -> bool:
        """Whether this arm asserts exactly one claim — the bijection's happy case."""
        return self.count == 1


def _appends_in(node: ast.AST) -> int:
    """Count `out.append(...)` calls anywhere under `node`."""
    return sum(
        1
        for sub in ast.walk(node)
        if isinstance(sub, ast.Call)
        and isinstance(sub.func, ast.Attribute)
        and sub.func.attr == "append"
        and isinstance(sub.func.value, ast.Name)
        and sub.func.value.id == OUT_PARAM
    )


def _chain_branches(node: ast.If) -> list[list[ast.stmt]]:
    """Return the mutually exclusive bodies of one `if`/`elif`/`else` chain.

    ⚑ AN `elif` IS AN `If` INSIDE `orelse`, WHICH IS WHY THIS RECURSES RATHER THAN READING
    `orelse` AS ONE BRANCH. Python has no elif node — `elif x:` parses as an `else:` whose sole
    statement is another `If` — so a chain of four branches is four nested nodes, and treating
    `orelse` as a leaf would merge three of them into one.
    """
    out = [node.body]
    rest = node.orelse
    while len(rest) == 1 and isinstance(rest[0], ast.If):
        out.append(rest[0].body)
        rest = rest[0].orelse
    if rest:
        out.append(rest)
    return out


def _claims_of(stmts: list[ast.stmt]) -> int:
    """Return the claim count for a statement list — the recursion the whole module is.

    ⚑ AN `if`/`elif` CHAIN CONTRIBUTES THE MAXIMUM OVER ITS BRANCHES, NOT THE SUM. Only one
    branch runs, so the arm asserts one claim however many messages it can produce. Taking the
    max rather than 1 keeps a branch that itself makes several sequential claims honest.
    """
    total = 0
    for stmt in stmts:
        if isinstance(stmt, ast.If):
            branches = _chain_branches(stmt)
            total += max((_claims_of(b) for b in branches), default=0)
        elif isinstance(stmt, (ast.For, ast.While)):
            # ⚑ A LOOP ASSERTS ONE CLAIM OVER A POPULATION, however many members fail it.
            inner = _claims_of(stmt.body)
            total += 1 if inner else 0
        elif isinstance(stmt, ast.With):
            total += _claims_of(stmt.body)
        elif isinstance(stmt, ast.Try):
            # ⚑⚑ A try/except/else IS AN EXCLUSIVE CHAIN, and reading only `body` made every
            # raises-check arm UNDECIDED — all five the first census could not model. The
            # handlers and the `else` are mutually exclusive with each other: exactly one path
            # runs, so the arm asserts the MAXIMUM over them, not the sum. `finally` always
            # runs, so it adds.
            arms = [stmt.body, *[h.body for h in stmt.handlers], stmt.orelse]
            total += max((_claims_of(a) for a in arms), default=0)
            total += _claims_of(stmt.finalbody)
        else:
            total += _appends_in(stmt)
    return total


def read_arm(node: ast.FunctionDef, suite: str) -> Claims:
    """Return the claim count for one arm, or UNDECIDED with a reason."""
    appends = _appends_in(node)
    if appends == 0:
        return Claims(suite, node.name, 0, "asserts nothing")
    counted = _claims_of(node.body)
    if counted == 0:
        return Claims(
            suite, node.name, None, "appends exist but sit in a shape this reader does not model"
        )
    return Claims(suite, node.name, counted, "")


def read(path: Path) -> tuple[Claims, ...]:
    """Return the claim count for every rostered arm in one suite.

    ⚑ THE ROSTER COMES FROM `arm_shape`, NOT FROM A SECOND WALK. Which functions are arms is
    that module's question and it already answers it — re-deriving the roster here would be a
    rival authority for one relation, and the two would drift.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return ()
    known = {a.name for a in arm_shape.read(path)}
    if not known:
        return ()
    return tuple(
        read_arm(node, path.name)
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in known
    )


def census(root: Path | None = None) -> tuple[Claims, ...]:
    """Return the claim count for every arm across `substrate/`."""
    where = (root if root is not None else corpus.ROOT) / "substrate"
    out: list[Claims] = []
    for path in sorted(where.glob("*.py")):
        out.extend(read(path))
    return tuple(out)


def render(found: tuple[Claims, ...]) -> str:
    """Render the claim census: how many arms are one claim, how many are several.

    ⚑ THE UNDECIDED ROW IS PRINTED EVEN AT ZERO. A reader that could not decide is a different
    fact from an arm that asserts nothing, and a bijection built on a silent zero would treat
    an unread arm as a satisfied one.
    """
    if not found:
        return "  no arms found — a fact about the WALK, not the tree\n"

    single = [c for c in found if c.single]
    several = [c for c in found if c.decided and c.count is not None and c.count > 1]
    silent = [c for c in found if c.count == 0]
    undecided = [c for c in found if not c.decided]
    suites = {c.suite for c in found}

    lines = [
        f"  {len(found)} arm(s) across {len(suites)} suite(s)",
        f"    one claim (the bijection's happy case) : {len(single)}",
        f"    several claims (needs splitting)       : {len(several)}",
        f"    asserts nothing                        : {len(silent)}",
        f"    UNDECIDED (a fact about this reader)   : {len(undecided)}",
    ]
    lines.extend(
        f"      several  {c.suite}::{c.name}  ({c.count} claims)" for c in several[:SAMPLE]
    )
    if len(several) > SAMPLE:
        lines.append(f"      … and {len(several) - SAMPLE} more multi-claim arm(s)")
    lines.extend(
        f"      ⚑ undecided  {c.suite}::{c.name}  — {c.reason}" for c in undecided[:SAMPLE]
    )
    if len(undecided) > SAMPLE:
        lines.append(f"      … and {len(undecided) - SAMPLE} more undecided arm(s)")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    """Print the claim census for every arm in the promoted package."""
    if argv:
        sys.stderr.write("usage: arm_claims.py\n")
        return 2
    sys.stdout.write(render(census()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
