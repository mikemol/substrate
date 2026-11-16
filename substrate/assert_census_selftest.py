#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.assert_census` — the grading predicate, on LITERAL sources.

⚑⚑ EVERY CASE PINS THE PROPERTY ON A SOURCE STRING, NEVER ON A LIVE FILE. An arm that named a
real module's assert would assert a fact about that module's current text, and this repo has
watched four such arms expire on an unrelated edit. The predicate is what is under test, so the
input belongs to the case.

⚑⚑ AND EVERY GRADING ARM CARRIES ITS DISCRIMINATOR — a source the predicate must grade the OTHER
way. A case proving `narrows` says LOAD passes just as well against a predicate that says LOAD to
everything; the paired case proving an ordinary comparison is NOT LOAD is what makes the first
one mean something.
"""

from __future__ import annotations

import sys

from substrate import assert_census

_NARROWING_SRC = "def f(x):\n    assert isinstance(x, int)\n    return x + 1\n"

_PLAIN_ARM_SRC = "def test_thing():\n    assert 1 + 1 == 2\n"

_PRODUCTION_SRC = "def render(rows):\n    assert rows\n    return len(rows)\n"

_NESTED_SRC = "def test_outer():\n    def helper():\n        assert 1 == 1\n    helper()\n"

_IS_NONE_SRC = "def f(x):\n    assert x is not None\n    return x + 1\n"

_IS_FALSE_SRC = "def test_flag():\n    assert may_write() is False\n"

_SUITE_NAME = "m" + assert_census.SUITE_SUFFIX + ".py"


def _kinds(path: str, text: str) -> list[str]:
    """Return just the grades the census gives one source, in order."""
    return [site.kind for site in assert_census.graded(path, text)]


def a_narrowing_assert_is_load(out: list[str]) -> int:
    """Check an `isinstance` assert grades LOAD, and a plain comparison does NOT.

    ⚑ THE DISCRIMINATOR IS THE SECOND HALF. `_PLAIN_ARM_SRC` holds an assert in a case function
    with no narrowing call; if it also graded LOAD the predicate would be answering `yes` without
    reading its input, and the first check alone could not tell.
    """
    bad = 0
    got = _kinds("m.py", _NARROWING_SRC)
    if got != [assert_census.LOAD]:
        out.append(f"selftest: an isinstance assert graded {got}")
        bad += 1
    got = _kinds("m.py", _PLAIN_ARM_SRC)
    if got != [assert_census.ARM]:
        out.append(f"selftest: a plain comparison in a case graded {got}")
        bad += 1
    return bad


def identity_narrows_only_against_none(out: list[str]) -> int:
    """Check `is None` narrows and `is False` does not.

    ⚑⚑ THIS ARM EXISTS BECAUSE THE CENSUS ONCE REPORTED ITSELF. Reading every `is` as narrowing
    graded five pytest arms LOAD across `tests/` — `assert may_write() is False` checks a return
    value and narrows no name — so the entire must-look-at list was an artifact of the predicate
    rather than a fact about the tree. The discriminator is the pair: without the `is False` half
    a rule that says LOAD to every identity comparison passes this arm.
    """
    bad = 0
    got = _kinds("m.py", _IS_NONE_SRC)
    if got != [assert_census.LOAD]:
        out.append(f"selftest: an `is not None` assert graded {got}")
        bad += 1
    got = _kinds("m.py", _IS_FALSE_SRC)
    if got != [assert_census.ARM]:
        out.append(f"selftest: an `is False` value check graded {got}")
        bad += 1
    return bad


def narrowing_beats_location(out: list[str]) -> int:
    """Check a narrowing assert stays LOAD even inside a suite module.

    ⚑ THE ORDER OF THE GRADES IS ITSELF A CLAIM. A suite module's asserts are arms by location,
    but a narrowing one still leaves the lines after it unguarded under `-O`, so location must
    not be allowed to overwrite it. If it did, every LOAD site in a suite would vanish from the
    reading that exists to find them.
    """
    got = _kinds(_SUITE_NAME, _NARROWING_SRC)
    if got != [assert_census.LOAD]:
        out.append(f"selftest: a narrowing assert in a suite module graded {got}")
        return 1
    return 0


def a_suite_module_grades_by_location(out: list[str]) -> int:
    """Check the suite suffix makes an otherwise-unknown assert an ARM, and only there.

    ⚑ THE DISCRIMINATOR IS THE SAME SOURCE UNDER A NON-SUITE NAME. `_PRODUCTION_SRC`'s assert is
    in no case function and narrows nothing, so it must read UNKNOWN in an ordinary module and
    ARM in a suite — one input, two names, two grades.
    """
    bad = 0
    got = _kinds(_SUITE_NAME, _PRODUCTION_SRC)
    if got != [assert_census.ARM]:
        out.append(f"selftest: an assert in a suite module graded {got}")
        bad += 1
    got = _kinds("m.py", _PRODUCTION_SRC)
    if got != [assert_census.UNKNOWN]:
        out.append(f"selftest: a production-scope assert graded {got}")
        bad += 1
    return bad


def case_scope_reaches_a_nested_function(out: list[str]) -> int:
    """Check containment descends: a helper inside a case function is still case scope.

    ⚑ THE DEFECT THIS PINS IS A WALK THAT ONLY CHECKS THE IMMEDIATE PARENT. A helper defined
    inside a case would then grade UNKNOWN and land in the reader's must-look-at list forever.
    """
    got = _kinds("m.py", _NESTED_SRC)
    if got != [assert_census.ARM]:
        out.append(f"selftest: an assert in a case's helper graded {got}")
        return 1
    return 0


def the_tally_counts_every_kind(out: list[str]) -> int:
    """Check the tally reports all three kinds, including the ones at zero.

    ⚑ A KIND OMITTED AT ZERO IS THE FALSE-ZERO SHAPE. A reader scanning for `load=` must find it
    reading `load=0`, not find nothing and conclude the census does not grade for it.
    """
    counts = assert_census.tally(assert_census.graded("m.py", _PLAIN_ARM_SRC))
    missing = [
        k for k in (assert_census.ARM, assert_census.LOAD, assert_census.UNKNOWN) if k not in counts
    ]
    if missing:
        out.append(f"selftest: the tally omitted {missing}")
        return 1
    if counts[assert_census.ARM] != 1:
        out.append(f"selftest: the tally counted {counts[assert_census.ARM]} arm(s), not 1")
        return 1
    return 0


def the_render_states_its_blind_spots(out: list[str]) -> int:
    """Check every unresolved note reaches the rendered output.

    ⚑ THE ROSTER IS COMPARED, NOT SAMPLED. Checking that the text is non-empty would pass on a
    render that dropped four of the five notes — and the whole point of the roster is that a
    reader sees the complete boundary beside the count.
    """
    text = assert_census.render(assert_census.graded("m.py", _PLAIN_ARM_SRC))
    absent = [note for note in assert_census.unresolved() if note not in text]
    if absent:
        out.append(f"selftest: the render omitted {len(absent)} unresolved note(s)")
        return 1
    if not assert_census.unresolved():
        out.append("selftest: the unresolved roster is empty")
        return 1
    return 0


_ARMS = (
    a_narrowing_assert_is_load,
    identity_narrows_only_against_none,
    narrowing_beats_location,
    a_suite_module_grades_by_location,
    case_scope_reaches_a_nested_function,
    the_tally_counts_every_kind,
    the_render_states_its_blind_spots,
)

_CASE_COUNT = 2 + 2 + 1 + 2 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"assert-census selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"assert-census selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
