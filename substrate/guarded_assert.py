#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Find assertion sites inside an arm whose EXECUTION is guarded by a sibling assertion's outcome.

⚑⚑⚑ THE SHAPE IS A `rests-on` EDGE WEARING CONTROL FLOW. Splitting six multi-assert arms into
thirteen moved two suites' declared totals — `case_count_selftest` 9→10, `case_lens_selftest`
8→12 — and that was not a broken invariant. Both were arms whose second assertion sat behind an
`elif` or an early `return`, so it ran on every invocation and had no place in `_CASE_COUNT`.
The operator's reading is the rule this reader mechanizes: *"a second claim that rests on the
first"*. Applying it by hand caught two uncounted assertions; there are ~100 multi-assert arms and
doing the rest by hand is judgement in the turn.

⚑⚑ WHAT THIS FINDS IS A SHAPE, NOT A DEFECT — AND THE NAMING IS DELIBERATE. `arm_shape` already
reports which arms assert several facts; this says which of those facts run CONDITIONALLY on an
earlier one. Whether a given instance should be SPLIT is a judgement this reader must not pretend
to make, and two arms were deliberately left unsplit for exactly that reason: *"a count and five
memberships over the SAME roster, neither guarding the other"*. A guarded site can equally be one
claim checked at two points, where the guard is only an early exit avoiding a cascade of noise. So
the output is a WORK LIST to read, never a list of defects; nothing here is called one.

⚑⚑ TWO SPELLINGS, MEASURED, AND THEY ARE NOT THE SAME MECHANISM. An `elif` makes the second test
run only when the first was FALSE — the premise is explicit in the grammar. An early `return` /
`continue` / `break` inside an appending branch makes every LATER sibling site conditional, and
that one is invisible at the site: the guarded append reads like an independent check, and only
the earlier statement's exit tells you otherwise. The second is why a reader is needed at all.

⚑ AND A NAIVE READER WOULD CALL EVERY `if` A GUARD. The canonical multi-assert arm is a run of
independent `if <bad>: out.append(...); bad += 1` blocks that ACCUMULATE — every one of them runs
on every invocation, and every one already has a place in the total. A reader flagging those would
report the whole population and be worth nothing. The suite's positive control holds it to that.

⚑ THE ROSTER COMES FROM `arm_shape.read`, NOT FROM A SECOND PARSER. That reader already owns what
counts as an arm (the roster is the authority, not the signature), and re-deriving it here would
give the tree two answers to one question — the drift shape this repo gates elsewhere.

⚑ THIS REPORTS; IT DOES NOT REWRITE. Splitting is a separate, hand-read step, and doing it here
would bury the measurement inside the thing it exists to justify.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import arm_shape, corpus

if TYPE_CHECKING:
    from pathlib import Path

# How many rows to spell out before summarizing. ⚑ THE TOTAL IS ALWAYS STATED; this bounds only
# how many are NAMED, so a truncated listing never reads as a smaller population.
SAMPLE = 20

# The guard spellings, as this reader reports them.
GUARD_ELIF = "elif"
GUARD_EXIT = "early-exit"

# ⚑ THE BOUND IS PRINTED WITH EVERY READING, not left to the reader's docstring. A work list that
# does not restate what it is NOT claiming gets acted on as a defect list.
BOUND = "  a guarded site is a SHAPE to read, not a defect — some are one claim checked twice"


@dataclass(frozen=True, slots=True)
class Site:
    """One assertion site whose execution rests on an earlier one in the same arm."""

    suite: str
    arm: str
    line: int
    guard: str
    guard_line: int


def _appends_here(node: ast.AST) -> list[ast.Call]:
    """Return the `out.append(...)` calls anywhere under one node."""
    return [
        sub
        for sub in ast.walk(node)
        if isinstance(sub, ast.Call)
        and isinstance(sub.func, ast.Attribute)
        and sub.func.attr == "append"
        and isinstance(sub.func.value, ast.Name)
        and sub.func.value.id == arm_shape.OUT_PARAM
    ]


def _exits(node: ast.stmt) -> bool:
    """Report whether a statement contains a jump that leaves THIS arm's flow.

    ⚑ A NESTED FUNCTION'S `return` IS NOT THIS ARM'S EXIT, and `ast.walk` would hand one over.
    Arms in this tree do define inner helpers, so the descent stops at a function boundary — a
    false exit here would report an independent sibling as guarded, which is the one direction
    this reader must not be wrong in.
    """
    stack: list[ast.AST] = [node]
    while stack:
        cur = stack.pop()
        if isinstance(cur, (ast.Return, ast.Continue, ast.Break)):
            return True
        if cur is not node and isinstance(
            cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)
        ):
            continue
        stack.extend(ast.iter_child_nodes(cur))
    return False


def _is_elif(head: ast.If) -> bool:
    """Report whether an `If`'s else-branch is an `elif` rather than a nested `else: if`.

    ⚑ THE COLUMN IS THE DISCRIMINATOR the grammar does not give. `ast` spells both the same way;
    an `elif` keeps the parent's indentation, an `else:` containing an `if` does not.
    """
    return (
        len(head.orelse) == 1
        and isinstance(head.orelse[0], ast.If)
        and head.orelse[0].col_offset == head.col_offset
    )


def _elif_sites(node: ast.If, suite: str, arm: str) -> list[Site]:
    """Return the sites in an `elif` chain that rest on an earlier branch's test.

    ⚑ THE GRAMMAR IS THE WITNESS. A branch reached only where the previous test was FALSE asserts
    something the earlier assertion's absence made reachable — the premise is spelled in the
    control flow and nowhere in the count.
    """
    found: list[Site] = []
    head = node
    while _is_elif(head):
        nxt = head.orelse[0]
        if not isinstance(nxt, ast.If):
            break
        found.extend(
            Site(suite=suite, arm=arm, line=call.lineno, guard=GUARD_ELIF, guard_line=head.lineno)
            for stmt in nxt.body
            for call in _appends_here(stmt)
        )
        head = nxt
    return found


def _exit_sites(body: list[ast.stmt], suite: str, arm: str) -> list[Site]:
    """Return sites in one statement block made conditional by an earlier branch's exit.

    ⚑⚑ THE ORDER IS THE MECHANISM. Once a statement earlier in this block both APPENDS and EXITS,
    every later append in the block runs only because that earlier check did not fire. The guard
    is not spelled at the guarded site, which is exactly why reading these by hand missed them.
    """
    found: list[Site] = []
    guard_at: int | None = None
    for stmt in body:
        appends = _appends_here(stmt)
        if guard_at is not None:
            found.extend(
                Site(suite=suite, arm=arm, line=call.lineno, guard=GUARD_EXIT, guard_line=guard_at)
                for call in appends
            )
        elif appends and _exits(stmt):
            guard_at = stmt.lineno
    return found


def _blocks(node: ast.AST) -> list[list[ast.stmt]]:
    """Return every statement block under a node, so a nested body is read like a top-level one.

    ⚑ THE KINDS ARE SPELLED OUT, NOT REACHED VIA `getattr`. A reflective read of `body`/`orelse`
    infers `Any` and the per-file gate refuses the file for it — and the enumeration is the better
    artefact anyway: a statement kind this reader cannot descend into is then a visible omission
    rather than a silently-empty result.
    """
    out: list[list[ast.stmt]] = []
    for sub in ast.walk(node):
        if isinstance(
            sub,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
                ast.With,
                ast.AsyncWith,
                ast.ExceptHandler,
            ),
        ):
            out.append(sub.body)
        elif isinstance(sub, (ast.If, ast.For, ast.AsyncFor, ast.While)):
            out.append(sub.body)
            out.append(sub.orelse)
        elif isinstance(sub, ast.Try):
            out.append(sub.body)
            out.append(sub.orelse)
            out.append(sub.finalbody)
    return [block for block in out if block]


def _by_line(site: Site) -> int:
    """Return a site's line, as a sort key.

    ⚑ A NAMED FUNCTION, NOT A `lambda` — a lambda sort key infers `Any`, and the per-file gate
    refuses the whole file for it.
    """
    return site.line


def sites(node: ast.FunctionDef, suite: str) -> tuple[Site, ...]:
    """Return every guarded assertion site in one arm, both spellings, deduplicated by line.

    ⚑ ONE SITE CAN BE REACHED BY BOTH SPELLINGS — an `elif` branch that also sits after an
    exiting sibling. Reporting it twice would inflate a work list whose whole value is that its
    count is readable, so the first guard found for a line is the one kept.
    """
    found: list[Site] = []
    for block in _blocks(node):
        found.extend(_exit_sites(block, suite, node.name))
    for sub in ast.walk(node):
        if isinstance(sub, ast.If):
            found.extend(_elif_sites(sub, suite, node.name))

    seen: set[int] = set()
    kept: list[Site] = []
    for site in sorted(found, key=_by_line):
        if site.line not in seen:
            seen.add(site.line)
            kept.append(site)
    return tuple(kept)


@dataclass(frozen=True, slots=True)
class Reading:
    """One point-in-time census: the sites found, and the population they were found in.

    ⚑⚑ THE DENOMINATOR TRAVELS WITH THE COUNT, ALWAYS. The arm census in this tree read 285 → 313
    → 326 → 351 over three sittings because other agents were landing suites underneath it.
    `0 sites over 0 arms` and `0 sites over 300 arms` are different facts, and a bare count cannot
    tell them apart.
    """

    sites: tuple[Site, ...]
    arms: int
    suites: int


def read(path: Path) -> Reading:
    """Return the guarded sites in one suite, with the arm count they were read over."""
    rostered = {arm.name for arm in arm_shape.read(path)}
    if not rostered:
        return Reading(sites=(), arms=0, suites=0)
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return Reading(sites=(), arms=0, suites=0)

    found: list[Site] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in rostered:
            found.extend(sites(node, path.name))
    return Reading(sites=tuple(found), arms=len(rostered), suites=1)


def census(root: Path | None = None) -> Reading:
    """Return the reading over every suite in `substrate/`."""
    where = (root if root is not None else corpus.ROOT) / "substrate"
    found: list[Site] = []
    arms = 0
    suites = 0
    for path in sorted(where.glob("*.py")):
        one = read(path)
        found.extend(one.sites)
        arms += one.arms
        suites += one.suites
    return Reading(sites=tuple(found), arms=arms, suites=suites)


def render(reading: Reading, *, limit: int = SAMPLE) -> str:
    """Return the work list, with its denominator and its own bound on what it claims.

    ⚑ `limit` EXISTS BECAUSE A TRUNCATED WORK LIST IS NOT A WORK LIST. The default keeps a bare
    run readable; `--all` lifts it, because the whole point of this census is that someone reads
    every row and decides, per row, whether it is a premise edge. A summary cannot be acted on.
    """
    head = (
        f"  {len(reading.sites)} guarded site(s) over {reading.arms} arm(s) "
        f"in {reading.suites} suite(s)"
    )
    lines = [head, BOUND]
    if not reading.sites:
        lines.append("  no assertion site rests on a sibling's outcome in this reading")
        return "\n".join(lines) + "\n"

    lines.extend(
        f"    {site.guard:<10} {site.suite}::{site.arm}  "
        f"line {site.line} rests on line {site.guard_line}"
        for site in reading.sites[:limit]
    )
    if len(reading.sites) > limit:
        lines.append(f"    … and {len(reading.sites) - limit} more guarded site(s)")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    _READING = census()
    sys.stdout.write(render(_READING, limit=len(_READING.sites) if "--all" in sys.argv else SAMPLE))
    sys.exit(0)
