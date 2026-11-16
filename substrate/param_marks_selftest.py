#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.param_marks`: the arity is HONOURED and the paramstyle is ONE.

⚑⚑⚑ THE ARITY ARM IS A DISCRIMINATOR, NOT A SMOKE TEST, AND THAT DISTINCTION IS THE POINT. A
renderer that ignored its argument and always returned a single placeholder would satisfy any
arm asking only "did I get a string back" — and would compose a statement whose placeholder
count silently disagreed with its parameter tuple. So the arms drive SEVERAL counts and assert
the answers DIFFER from each other, which is a property no constant-returning stub has.

⚑⚑ AND ASSERTING THE COUNTS DIFFER IS NOT THE SAME AS ASSERTING EACH COUNT. A renderer emitting
`n + 1` placeholders would satisfy a difference check perfectly while being wrong everywhere. So
each arity is also checked against its own expected rendering. The pair is what pins it.

⚑⚑ THE PARAMSTYLE ARM ASSERTS AN ABSENCE AS WELL AS A PRESENCE, because the measured defect was
the WRONG style rather than a missing one. An arm checking only that `%s` appears would pass on
a renderer that emitted both styles, or that emitted `?` for some arities — so the arm also
asserts the retired sqlite spelling appears nowhere in the output.

⚑⚑ THE BACKEND PARAMETER IS CHECKED TO BE GONE, WHICH IS AN ARM ABOUT A REFUSAL RATHER THAN A
RESULT. The retired signature accepted a backend argument that resolved to an AMBIENT while the
placeholder it returned was bound to a specific connection; four recorded failures came from
those two disagreeing. Passing one must be a `TypeError` — an arm asserting only that the
one-argument call works would pass equally against a signature that still accepted the second
and quietly ignored it, which is the ignored-parameter shape that invites the branch back.

⚑ EVERY CASE RUNS OFFLINE. The renderer is pure over an integer, so no store, driver or
environment is consulted — which is exactly the property that makes a placeholder authority
trustworthy, since an ambient-reading one is the thing being retired.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_family

from substrate import param_marks, suite_emit

# The retired sqlite paramstyle. ⚑ NAMED SO AN ARM CAN ASSERT ITS ABSENCE: the measured defect
# was emitting this one into a psycopg cursor, which is not visible to a check that only looks
# for the style that should be there.
_RETIRED_MARK = "?"

# Arities the arms drive. ⚑ THREE DISTINCT NON-TRIVIAL COUNTS, so a renderer returning a constant
# — or one off by one — fails rather than coincidentally agreeing on a single sampled value.
_ARITIES = (1, 2, 5)

# The count whose rendering must be the empty string.
_EMPTY_ARITY = 0

# An arity no honest caller computes. ⚑ THE REFUSAL CASE: `["%s"] * -1` is the EMPTY list in
# Python, so a negative count renders as a plausible statement with no placeholders at all.
_NEGATIVE_ARITY = -1


def the_arity_is_honoured_and_the_counts_differ(out: list[str]) -> int:
    """Check that distinct arities render distinctly, and that each renders correctly.

    ⚑⚑ THIS IS THE DISCRIMINATOR. A renderer ignoring its argument returns one string for every
    count and would satisfy any arm that merely called it once. Asserting the renderings differ
    kills that stub; asserting each equals its own expansion kills an off-by-one that the
    difference check alone would pass.
    """
    bad = 0
    rendered = [param_marks.marks(n) for n in _ARITIES]
    if len(set(rendered)) != len(_ARITIES):
        out.append(
            f"selftest: {len(_ARITIES)} distinct arities rendered {len(set(rendered))} distinct "
            f"strings — the count is being ignored"
        )
        bad += 1
    for n, got in zip(_ARITIES, rendered, strict=True):
        want = param_marks.SEPARATOR.join([param_marks.MARK] * n)
        if got != want:
            out.append(f"selftest: marks({n}) rendered {got!r}, want {want!r}")
            bad += 1
        if got.count(param_marks.MARK) != n:
            out.append(f"selftest: marks({n}) carries {got.count(param_marks.MARK)} placeholders")
            bad += 1
    return bad


def there_is_exactly_one_paramstyle(out: list[str]) -> int:
    """Check that the emitted style is the postgres one and the retired one appears nowhere.

    ⚑ THE ABSENCE IS HALF THE CLAIM. The measured failures were the WRONG style reaching a
    cursor, not a missing one, so an arm looking only for `%s` would pass against a renderer that
    also emitted `?` — which is precisely the two-spellings state this module exists to end.
    """
    bad = 0
    if param_marks.MARK == _RETIRED_MARK:
        out.append("selftest: the module's paramstyle IS the retired sqlite one")
        bad += 1
    for n in _ARITIES:
        got = param_marks.marks(n)
        if _RETIRED_MARK in got:
            out.append(f"selftest: marks({n}) emitted the retired {_RETIRED_MARK!r} style")
            bad += 1
        if param_marks.MARK not in got:
            out.append(f"selftest: marks({n}) emitted no {param_marks.MARK!r} placeholder")
            bad += 1
    return bad


def a_zero_arity_renders_empty_rather_than_refusing(out: list[str]) -> int:
    """Check that asking for no placeholders yields the empty string.

    ⚑ ZERO IS A REAL STATEMENT SHAPE, and refusing it would push the caller into an `if` that
    spells the empty case by hand — reintroducing the per-site branch this module removes, at the
    one arity where a caller is most likely to shrug and inline it.
    """
    bad = 0
    got = param_marks.marks(_EMPTY_ARITY)
    if got != "":
        out.append(f"selftest: marks({_EMPTY_ARITY}) rendered {got!r}, want the empty string")
        bad += 1
    if param_marks.MARK in got:
        out.append("selftest: a zero arity still carried a placeholder")
        bad += 1
    return bad


def a_negative_arity_refuses_rather_than_rendering_empty(out: list[str]) -> int:
    """Check that a negative count raises, instead of silently composing a parameterless statement.

    ⚑⚑ THE FAILURE THIS PREVENTS HAS NO SYMPTOM AT THIS LAYER. A negative count multiplies to the
    empty list, so the caller receives a statement the driver rejects for a reason naming neither
    the arity nor where it came from. The arm asserts a raise AND that the raise is not merely
    the empty string coming back — a renderer returning `""` here would pass a check that only
    asked whether the output was falsy.
    """
    try:
        got = param_marks.marks(_NEGATIVE_ARITY)
    except ValueError:
        return 0
    out.append(
        f"selftest: marks({_NEGATIVE_ARITY}) returned {got!r} instead of refusing — a miscomputed "
        f"arity composes a parameterless statement the driver rejects elsewhere"
    )
    return 1


def the_backend_parameter_is_gone(out: list[str]) -> int:
    """Check that passing a backend is a `TypeError`, not an ignored second argument.

    ⚑⚑ AN IGNORED PARAMETER READS AT EVERY CALL SITE AS THOUGH THE BACKEND WERE SELECTABLE THERE,
    which is how the retired branch gets re-added. An arm asserting only that the one-argument
    call works would pass against a signature still accepting and discarding the second, so this
    arm asserts the REFUSAL — the loud failure at the one place that could reintroduce the
    ambient-versus-connection disagreement.
    """
    try:
        param_marks.marks(1, "sqlite")  # type: ignore[call-arg]
    except TypeError:
        return 0
    out.append(
        "selftest: marks() still ACCEPTS a backend argument — an ignored one reads as though the "
        "paramstyle were selectable per call site, which is the retired defect"
    )
    return 1


FAMILY = witness_family.of(
    key="param_marks",
    apex="a placeholder list matches the arity it was asked for, in the single paramstyle this "
    "store speaks, with no backend selectable at any call site and a miscomputed arity "
    "refused rather than rendered away",
    subject="the placeholder strings `substrate.param_marks` renders, offline",
    members=(
        witness_family.Member(
            name="the_arity_is_honoured_and_the_counts_differ",
            claim="distinct arities render distinctly and each matches its own expansion",
            cases=7,
        ),
        witness_family.Member(
            name="there_is_exactly_one_paramstyle",
            claim="the postgres style is emitted and the retired sqlite one appears nowhere",
            cases=7,
        ),
        witness_family.Member(
            name="a_zero_arity_renders_empty_rather_than_refusing",
            claim="asking for no placeholders yields the empty string",
            cases=2,
        ),
        witness_family.Member(
            name="a_negative_arity_refuses_rather_than_rendering_empty",
            claim="a negative count raises instead of composing a parameterless statement",
            premises=("a_zero_arity_renders_empty_rather_than_refusing",),
        ),
        witness_family.Member(
            name="the_backend_parameter_is_gone",
            claim="passing a backend is a TypeError rather than an ignored argument",
        ),
    ),
)

_ARMS = (
    the_arity_is_honoured_and_the_counts_differ,
    there_is_exactly_one_paramstyle,
    a_zero_arity_renders_empty_rather_than_refusing,
    a_negative_arity_refuses_rather_than_rendering_empty,
    the_backend_parameter_is_gone,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/param_marks_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
