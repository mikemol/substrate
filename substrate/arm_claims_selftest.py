#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the claim counter, against the arm whose miscount motivated it.

⚑⚑⚑ THE LOAD-BEARING CASE IS THE LIVE `if`/`elif`.
`arm_shape_selftest.a_multi_append_arm_is_not_mechanical` appends twice in exclusive branches,
and `arm_shape` counts it as two — correctly, for its own question. This reader must count it
as ONE, read off the real file rather than a fixture, because that arm is the measured instance
that showed a claim count and a rewrite cost are different numbers.

⚑⚑ THE `elif` FIXTURE IS THE ONE MOST LIKELY TO PASS FOR THE WRONG REASON. Python has no elif
node: `elif` parses as an `else` whose sole statement is another `If`. A reader that took
`orelse` as one branch would merge a four-branch chain into two and still report a plausible
small number. So a THREE-branch chain is cased explicitly, not just a two.

⚑ AND UNDECIDED IS ASSERTED AS ITS OWN OUTCOME, not folded into a count. An arm this reader
cannot model must report None with a reason — a bijection fed a guessed denominator is worse
than one that names what it could not read.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from substrate import arm_claims, arm_shape

ROOT = Path(__file__).resolve().parent.parent

_SEQUENTIAL = """
def an_arm(out: list[str]) -> int:
    bad = 0
    if x:
        out.append("first")
        bad += 1
    if y:
        out.append("second")
        bad += 1
    return bad
"""

_EXCLUSIVE = """
def an_arm(out: list[str]) -> int:
    if x:
        out.append("first")
    elif y:
        out.append("second")
    return 0
"""

_THREE_WAY = """
def an_arm(out: list[str]) -> int:
    if x:
        out.append("first")
    elif y:
        out.append("second")
    elif z:
        out.append("third")
    else:
        out.append("fallback")
    return 0
"""

_LOOP = """
def an_arm(out: list[str]) -> int:
    for item in things:
        if item.bad:
            out.append(f"bad: {item}")
    return 0
"""

_SILENT = """
def an_arm(out: list[str]) -> int:
    return 0
"""

# ⚑ THE SHAPE THAT READ UNDECIDED. A raises-check arm appends in the HANDLER and in the `else`,
# and those are mutually exclusive — exactly one path runs. The first cut read only `Try.body`
# and so found no appends at all, reporting UNDECIDED for every arm of this family.
_TRY_HANDLER = """
def an_arm(out: list[str]) -> int:
    try:
        thing()
    except ValueError as exc:
        if "x" not in str(exc):
            out.append("no x")
        if "y" not in str(exc):
            out.append("no y")
    else:
        out.append("it was ACCEPTED")
    return 0
"""

_TRY_FINALLY = """
def an_arm(out: list[str]) -> int:
    try:
        thing()
    except ValueError:
        out.append("raised")
    finally:
        out.append("always")
    return 0
"""

_TWO = 2

Case = tuple[str, bool]


def _one(src: str) -> arm_claims.Claims:
    """Return the claim reading for a single-function fixture."""
    node = ast.parse(src).body[0]
    if not isinstance(node, ast.FunctionDef):  # pragma: no cover - fixture shape
        msg = "fixture is not a function"
        raise TypeError(msg)
    return arm_claims.read_arm(node, "fixture.py")


def _within(claim: arm_claims.Claims, appends: int) -> bool:
    """Whether a claim count merges appends rather than inventing them.

    ⚑ NAMED RATHER THAN INLINED because the `None` arm has to be handled before the
    comparison — a reader that could not decide makes no claim about the relation, and folding
    that into a comprehension hides which of the two facts the row is asserting.
    """
    if claim.count is None:
        return True
    return claim.count <= appends


def _exclusive_cases() -> list[Case]:
    """Return the cases pinning that exclusive branches are ONE claim."""
    two = _one(_EXCLUSIVE)
    three = _one(_THREE_WAY)
    return [
        # ⚑ THE CASE gate-G6 RESTS ON. Two appends, one claim.
        ("an if/elif pair is ONE claim", two.count == 1),
        ("it is decided, not undecided", two.decided),
        ("it counts as single", two.single),
        # ⚑ THREE-WAY: an elif is a nested If inside orelse, so a reader treating orelse as a
        #   leaf merges branches and still returns a plausible number.
        ("a three-way chain with else is ONE claim", three.count == 1),
        ("the three-way chain is decided", three.decided),
    ]


def _sequential_cases() -> list[Case]:
    """Return the cases pinning that sequential appends are SEVERAL claims."""
    seq = _one(_SEQUENTIAL)
    loop = _one(_LOOP)
    silent = _one(_SILENT)
    return [
        ("two separate ifs are TWO claims", seq.count == _TWO),
        ("two separate ifs are not single", not seq.single),
        # ⚑ A LOOP ASSERTS ONE CLAIM OVER A POPULATION, however many members fail.
        ("a loop body is ONE claim", loop.count == 1),
        ("an arm that appends nothing asserts nothing", silent.count == 0),
        ("asserting nothing is DECIDED, not undecided", silent.decided),
        ("asserting nothing is not single", not silent.single),
    ]


def _try_cases() -> list[Case]:
    """Return the cases pinning the raises-check family, which first read UNDECIDED.

    ⚑ A `try/except/else` IS AN EXCLUSIVE CHAIN. Exactly one of body-completes, a handler, or
    the `else` runs, so the arm asserts the MAXIMUM over them. The handler here makes two
    sequential claims and the `else` one, so the arm is TWO — not three, and not one.
    """
    handler = _one(_TRY_HANDLER)
    always = _one(_TRY_FINALLY)
    return [
        ("a try/except/else arm is DECIDED, not undecided", handler.decided),
        ("the exclusive chain takes the maximum branch", handler.count == _TWO),
        ("it is therefore not single", not handler.single),
        # ⚑ `finally` ALWAYS RUNS, so it ADDS rather than competing.
        ("a finally clause adds rather than competing", always.count == _TWO),
        ("the finally arm is decided", always.decided),
    ]


def _live_cases() -> list[Case]:
    """Read the real arm whose miscount motivated this reader."""
    probe = ROOT / "substrate" / "arm_shape_selftest.py"
    if not probe.is_file():
        return [("arm_shape_selftest.py is present to read", False)]
    found = {c.name: c for c in arm_claims.read(probe)}
    target = found.get("a_multi_append_arm_is_not_mechanical")
    shapes = {a.name: a for a in arm_shape.read(probe)}
    counted = shapes.get("a_multi_append_arm_is_not_mechanical")
    return [
        # ⚑ TWO DEAD ROWS REMOVED HERE (gate-G21, gate-G22). One asserted a literal True after
        # the early return had already handled absence, and one asserted the roster was
        # non-empty — implied by `target is not None` on the line above it. Neither could fail
        # for any reason connected to this module, and both occupied case slots.
        ("the motivating arm is rostered and read", target is not None),
        # ⚑ THE WHOLE POINT: arm_shape counts this arm's appends as 2, and it is 1 claim.
        ("the live if/elif arm counts as ONE claim", target is not None and target.count == 1),
        # ⚑⚑ AND THE DIFFERENTIAL IS WHAT MAKES THAT A FINDING RATHER THAN A READING. The claim
        # is not *this arm has one claim* but *this arm has one claim WHERE arm_shape counts
        # two* — only a comparison carries it, and it goes red if the two readers ever agree.
        (
            "arm_shape counts the same arm's appends as TWO",
            counted is not None and counted.appends == _TWO,
        ),
    ]


def _agreement_cases() -> list[Case]:
    """Assert the two readers disagree in the DIRECTION gate-G6 predicts.

    ⚑ A DIFFERENTIAL, NOT A DUPLICATE. `arm_shape` over-counts by design for its own question,
    so claims must never EXCEED appends — if they did, this reader would be inventing
    assertions rather than merging them.
    """
    probe = ROOT / "substrate" / "arm_shape_selftest.py"
    if not probe.is_file():
        return [("both readers can read the same suite", False)]

    shapes = {a.name: a for a in arm_shape.read(probe)}
    claims = {c.name: c for c in arm_claims.read(probe)}
    both = set(shapes) & set(claims)
    return [
        ("both readers can read the same suite", len(both) > 0),
        ("both readers see the SAME arms", set(shapes) == set(claims)),
        # ⚑ THE DIRECTION IS THE ASSERTION. Claims merge appends, never invent them.
        (
            "a claim count never EXCEEDS the append count",
            all(_within(claims[n], shapes[n].appends) for n in both),
        ),
    ]


def _render_cases() -> list[Case]:
    """Return the cases pinning that the census states what it could not decide."""
    made = (
        arm_claims.Claims("a.py", "one", 1, ""),
        arm_claims.Claims("a.py", "many", 3, ""),
        arm_claims.Claims("a.py", "unread", None, "a shape this reader does not model"),
    )
    out = arm_claims.render(made)
    empty = arm_claims.render(())
    return [
        ("the render names the UNDECIDED row", "UNDECIDED" in out),
        (
            "the undecided arm is spelled out with its reason",
            "unread" in out and "does not model" in out,
        ),
        ("the multi-claim arm is spelled out", "many" in out),
        # ⚑ AN EMPTY CENSUS IS A FACT ABOUT THE WALK, not a clean tree.
        ("an empty census says so", "fact about the WALK" in empty),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = (
        _exclusive_cases()
        + _sequential_cases()
        + _try_cases()
        + _live_cases()
        + _agreement_cases()
        + _render_cases()
    )
    bad = [label for label, holds in cases if not holds]
    print(f"arm_claims: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
