# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_fixpoint` — the two termination rules that were historically wrong.

⚑⚑⚑ THE PLATEAU ARM AND THE CAP ARM ARE THE SUBJECT, NOT EDGE CASES. Both rules produced confident
false verdicts in the origin: a round cap called `[1340, 899, 561]` divergent when it was
converging, and strict decrease called `[…, 92, 56, 56]` a cycle when it was a plateau on the way
to zero. A suite that only exercised a clean convergence would pass against BOTH broken rules.

⚑⚑ AND THE FIXTURES ARE SEQUENCES, NOT DOCUMENTS, which is what the drain bought. The origin took
a path and shelled to pandoc, so a plateau could only be produced by finding a real document that
plateaus — which is why two wrong rules survived measurement for as long as they did. Here a
normalizer is a function the case chooses, so the exact sequence under test is stated in the case.

⚑ A NORMALIZER THAT REACHES ITS FIXPOINT MUST STOP CHANGING TEXT, or `changed_lines` would keep
reporting and the convergence arm would pass for the wrong reason. Every fixture below is a real
function of its input, never a canned list of numbers.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from substrate import md_fixpoint as mf

if TYPE_CHECKING:
    from collections.abc import Callable

#: The runaway guard the cap arm sets, named because that arm is ABOUT this bound.
GUARD = 2

#: A document long enough that the shrinking normalizer needs more rounds than `GUARD` allows.
LONG = "a\nb\nc\nd\ne\nf\ng\nh"


def _shrinking(step: int = 1) -> Callable[[str], str]:
    """Return a normalizer that removes `step` lines per call until none are left."""

    def normalize(text: str) -> str:
        lines = text.split("\n")
        return "\n".join(lines[:-step] if len(lines) > step else lines[:1])

    return normalize


def _plateauing(hold: int) -> Callable[[str], str]:
    """Return a normalizer that changes exactly one line for `hold` calls, then settles.

    ⚑ THIS IS THE SHAPE STRICT DECREASE MISREAD. The deltas repeat while different regions settle
    — pandoc re-emits a block group at a time — and a rule demanding every step be smaller calls
    that a stall.
    """
    state = {"n": 0}

    def normalize(text: str) -> str:
        state["n"] += 1
        if state["n"] > hold:
            return text
        return text + "\nx"

    return normalize


def _growing() -> Callable[[str], str]:
    """Return a normalizer whose deltas GROW — the one genuinely divergent shape."""
    state = {"n": 1}

    def normalize(text: str) -> str:
        state["n"] += 1
        return text + "\n" + "\n".join("y" for _ in range(state["n"]))

    return normalize


def _stuck() -> Callable[[str], str]:
    """Return a normalizer that changes the same amount forever — a true cycle."""
    state = {"flip": False}

    def normalize(text: str) -> str:
        state["flip"] = not state["flip"]
        base = text.rstrip("\n").split("\n")[0]
        return base + ("\na" if state["flip"] else "\nb")

    return normalize


def _convergence_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a sequence that reaches its fixpoint."""
    out: list[tuple[str, bool]] = []
    got = mf.run("a\nb\nc\nd\ne", _shrinking())

    out.append((f"a shrinking normalizer converges: {got.why}", got.converged))
    out.append((f"and the last delta is zero: {got.deltas}", got.deltas[-1] == 0))
    out.append((f"and the text is the fixpoint: {got.text!r}", _shrinking()(got.text) == got.text))
    out.append(
        (f"and the round count matches the sequence: {got.rounds}", got.rounds == len(got.deltas))
    )
    return out


def _plateau_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving a plateau is NOT read as a cycle.

    ⚑⚑ THE ARM THE ORIGIN FAILED. Strict decrease returned False on the first repeated delta, so a
    document descending in plateaus read as a stall — and a docstring plus a survey were built on
    that false reading before it was measured past the guard.
    """
    out: list[tuple[str, bool]] = []
    got = mf.run("seed", _plateauing(mf.PLATEAU_BUDGET - 1))

    out.append((f"a plateau shorter than the budget still converges: {got.why}", got.converged))
    out.append(
        (
            f"and its deltas repeat before settling: {got.deltas}",
            len(set(got.deltas[:-1])) < len(got.deltas[:-1]),
        )
    )
    return out


def _divergence_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the two shapes that genuinely do not converge."""
    out: list[tuple[str, bool]] = []

    grew = mf.run("seed", _growing())
    out.append(
        (
            f"a growing delta is divergence: {grew.why}",
            not grew.converged and "diverging" in grew.why,
        )
    )

    stuck = mf.run("seed", _stuck())
    out.append(
        (
            f"an unbroken repeat is a cycle: {stuck.why}",
            not stuck.converged and "cycle" in stuck.why,
        )
    )
    out.append(
        (
            f"and the cycle ends at the budget: {stuck.rounds}",
            stuck.rounds <= mf.PLATEAU_BUDGET + GUARD,
        )
    )
    return out


def _guard_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving the round guard is NOT a convergence verdict.

    ⚑⚑⚑ THIS IS THE CAP DEFECT MADE UNREPRESENTABLE. A round cap reporting `converged=False` with
    no distinction is exactly what called `[1340, 899, 561]` divergent. Hitting the guard must say
    so in its own words, so a reader can tell "I stopped looking" from "it does not converge".
    """
    out: list[tuple[str, bool]] = []
    got = mf.run(LONG, _shrinking(), rounds=GUARD)

    out.append((f"the guard stops the run: {got.rounds}", got.rounds == GUARD))
    out.append((f"and says it is NOT a verdict: {got.why}", "NOT a verdict" in got.why))

    # ⚑ THE SENSITIVITY ARM. The same normalizer WITHOUT the guard must converge, or the guard is
    # not what stopped it and this arm proves nothing.
    free = mf.run(LONG, _shrinking())
    out.append((f"removing ONLY the guard converges: {free.why}", free.converged))
    return out


def _delta_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the line-delta measure itself."""
    out: list[tuple[str, bool]] = []
    same = mf.changed_lines("a\nb", "a\nb")
    one = mf.changed_lines("a\nb", "a\nc")
    added = mf.changed_lines("a", "a\nb")
    removed = mf.changed_lines("a\nb", "a")

    out.append((f"identical text has no delta: {same}", same == 0))
    out.append((f"one changed line counts one: {one}", one == 1))
    # ⚑ A LENGTH CHANGE IS A DELTA, and padding is what makes that measurable rather than a crash.
    out.append((f"an added line counts: {added}", added == 1))
    out.append((f"a removed line counts: {removed}", removed == 1))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _convergence_cases()
        + _plateau_cases()
        + _divergence_cases()
        + _guard_cases()
        + _delta_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"md-fixpoint selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
