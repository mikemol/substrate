#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.arm_shape` — the three shapes, and the coverage loss they gate.

⚑⚑⚑ THE MULTI-ASSERT CASE IS THE ONE THE CENSUS EXISTS FOR. An arm making several `out.append`
calls asserts several facts, and a transform that rewrote it to ONE `assert` would keep the first
and drop the rest — coverage falling while every suite still reports green. Distinguishing those
arms is what makes a mechanical port safe to attempt at all, so a census that miscounted them
would license exactly the damage it is meant to prevent.

⚑⚑ AND THE ROSTER IS THE AUTHORITY, NOT THE SIGNATURE. A helper taking `out` that no roster
lists asserts nothing; counting it inflates the population and, worse, would put a dead function
into a transform's work list.

⚑ THE FIXTURES ARE SOURCE STRINGS. A case reading a real suite measures that suite's current
bodies, so it would report the tree rather than the reader — and go green the moment someone
edited an unrelated arm.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import arm_shape

# One rostered arm with the canonical shape, and a helper that is NOT rostered.
_ONE_ARM = '''def a_single_fact(out: list[str]) -> int:
    """One assertion."""
    if False:
        out.append("nope")
        return 1
    return 0


def a_helper(out: list[str]) -> int:
    """Takes `out` but is not in the roster."""
    out.append("x")
    return 1


_ARMS = (a_single_fact,)
'''

# An arm asserting two facts by accumulating.
_MULTI = '''def two_facts(out: list[str]) -> int:
    """Two assertions."""
    bad = 0
    if False:
        out.append("first")
        bad += 1
    if False:
        out.append("second")
        bad += 1
    return bad


_ARMS = (two_facts,)
'''

# An arm asserting that something raises.
_RAISES = '''def it_refuses(out: list[str]) -> int:
    """A raises-check."""
    try:
        thing()
    except ValueError:
        return 0
    out.append("did not raise")
    return 1


_ARMS = (it_refuses,)
'''

# A module with no roster at all.
_NO_ROSTER = '''def looks_like_an_arm(out: list[str]) -> int:
    """No roster names it."""
    return 0
'''

_TWO_APPENDS = 2


def _arms(where: str, text: str) -> tuple[arm_shape.Arm, ...]:
    """Write a fixture suite and read its arms back."""
    path = Path(where) / "fixture_selftest.py"
    path.write_text(text, encoding="utf-8")
    return arm_shape.read(path)


def only_rostered_functions_are_arms(out: list[str]) -> int:
    """Check a helper taking `out` is not counted.

    ⚑⚑ A DEAD FUNCTION IN A TRANSFORM'S WORK LIST IS WORSE THAN AN UNCOUNTED ONE. It would be
    rewritten into a pytest case that runs, passes, and asserts nothing — coverage that reads as
    real because it is green.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _arms(where, _ONE_ARM)
    if len(got) != 1 or got[0].name != "a_single_fact":
        out.append(f"selftest: the roster filter read {[a.name for a in got]!r}")
        return 1
    return 0


def a_single_append_arm_is_mechanical(out: list[str]) -> int:
    """Check the canonical shape is classified as portable."""
    with tempfile.TemporaryDirectory() as where:
        got = _arms(where, _ONE_ARM)
    if not got or not got[0].mechanical:
        out.append(f"selftest: the canonical arm is not mechanical: {got!r}")
        return 1
    return 0


def a_multi_append_arm_is_not_mechanical(out: list[str]) -> int:
    """Check an accumulating arm is held back — the POSITIVE CONTROL.

    ⚑ WITHOUT THIS, A CENSUS CALLING EVERYTHING MECHANICAL would pass the case above. The pair
    says the classifier discriminates rather than waving the whole population through.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _arms(where, _MULTI)
    bad = 0
    if not got or got[0].mechanical:
        out.append(f"selftest: a multi-assert arm was called mechanical: {got!r}")
        bad += 1
    elif got[0].appends != _TWO_APPENDS:
        out.append(f"selftest: the append count read {got[0].appends}")
        bad += 1
    return bad


def a_raises_check_is_its_own_shape(out: list[str]) -> int:
    """Check a try/except arm is classified separately.

    ⚑ IT NEEDS `pytest.raises`, A DIFFERENT REWRITE. Folding it in with the mechanical arms would
    produce an assert on a value the arm never computes.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _arms(where, _RAISES)
    if not got or not got[0].raises_check or got[0].mechanical:
        out.append(f"selftest: a raises-check was not held back: {got!r}")
        return 1
    return 0


def a_module_with_no_roster_yields_nothing(out: list[str]) -> int:
    """Check a non-suite contributes no arms."""
    with tempfile.TemporaryDirectory() as where:
        got = _arms(where, _NO_ROSTER)
    if got != ():
        out.append(f"selftest: a rosterless module yielded arms: {got!r}")
        return 1
    return 0


def an_empty_census_says_so(out: list[str]) -> int:
    """Check the render names its own emptiness rather than printing nothing.

    ⚑ SILENCE AND SUCCESS ARE THE SAME BYTES — the false-zero shape every census in this tree
    prints its denominator to avoid.
    """
    if "no arms" not in arm_shape.render(()):
        out.append("selftest: an empty census does not name its emptiness")
        return 1
    return 0


def the_render_states_every_population(out: list[str]) -> int:
    """Check all three shapes are reported, not just the portable one.

    ⚑⚑ REPORTING ONLY THE MECHANICAL COUNT IS THE MEASURED FAILURE THIS CENSUS CORRECTED. A plan
    stated on a sample said the port was a codemod; the full census read 166 of 285 mechanical,
    with 119 arms needing a hand port. A render naming one number would have preserved that error.
    """
    rows = (
        arm_shape.Arm(suite="a.py", name="one", appends=1, returns=2, raises_check=False),
        arm_shape.Arm(suite="a.py", name="two", appends=2, returns=1, raises_check=False),
        arm_shape.Arm(suite="a.py", name="three", appends=1, returns=2, raises_check=True),
    )
    text = arm_shape.render(rows)
    missing = [word for word in ("mechanical", "multi-assert", "raises-check") if word not in text]
    if missing:
        out.append(f"selftest: the render omits {missing!r}:\n{text}")
        return 1
    return 0


def a_truncated_listing_still_states_its_total(out: list[str]) -> int:
    """Check a long population reports its full count, not just the sample.

    ⚑ A CENSUS THAT TRUNCATES SILENTLY reports a smaller population than it measured — which is
    the same class as the sample-generalization this module exists to correct.
    """
    rows = tuple(
        arm_shape.Arm(suite="a.py", name=f"arm{n}", appends=2, returns=1, raises_check=False)
        for n in range(arm_shape.SAMPLE + 5)
    )
    text = arm_shape.render(rows)
    if f"multi-assert (>1 append)                : {len(rows)}" not in text:
        out.append(f"selftest: the truncated listing lost its total:\n{text}")
        return 1
    return 0


_ARMS = (
    only_rostered_functions_are_arms,
    a_single_append_arm_is_mechanical,
    a_multi_append_arm_is_not_mechanical,
    a_raises_check_is_its_own_shape,
    a_module_with_no_roster_yields_nothing,
    an_empty_census_says_so,
    the_render_states_every_population,
    a_truncated_listing_still_states_its_total,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"arm-shape selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"arm-shape selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
