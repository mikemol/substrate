#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.catalog_targets`: the vocabulary is closed, ordered, and refuses.

⚑⚑ THE ORDERING ARM IS A DIFFERENCE CHECK ON PURPOSE. Asserting only that `plan` returns the
right SET would pass on a driver that rendered in argv order, which is precisely what would churn
the diff between two sibling catalogs written in one run. The claim is the sequence, so the case
drives a request in the WRONG order and asserts the declared one comes back.

⚑⚑ THE REFUSAL ARM ASSERTS THE MESSAGE NAMES THE OFFENDER AND THE VALID SET, not merely that
something was raised. The superseded driver surfaces a mistyped target as a bare `KeyError`
from inside a render loop, which also raises — so an arm checking only for an exception would
pass on the exact defect being repaired. What the `KeyError` cannot do is say what was wrong or
what was allowed, and that is what is pinned.

⚑ `KNOWN` IS CHECKED AGAINST `DEFAULT` RATHER THAN AGAINST A TYPED LIST. A second hand-written
listing in the suite would be the same duplication the module avoids by deriving one from the
other, and it would drift in exactly the same way — a case that agrees with a stale copy of the
vocabulary reports the copy, not the module.

⚑ NO CASE TOUCHES A STORE, THE CORES, OR THE FILESYSTEM. The whole point of cutting this
vocabulary out of the renderer module is that it is pure; a suite that needed the `.agdai` tree
built would re-couple the fact to the machinery it was separated from.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_family

from substrate import catalog_targets, suite_emit


def the_vocabulary_and_its_sequence_agree(out: list[str]) -> int:
    """Check that the membership set is exactly the rendered sequence, with no duplicates.

    ⚑ A VOCABULARY THAT ADMITS A NAME IT DOES NOT RENDER IS THE FAILURE. `plan` filters `DEFAULT`
    by membership, so a name in `KNOWN` but absent from `DEFAULT` would be accepted by `unknown`
    and then silently dropped — a request reported as satisfied while one catalog was never
    written.
    """
    bad = 0
    if set(catalog_targets.DEFAULT) != set(catalog_targets.KNOWN):
        out.append("selftest: KNOWN and DEFAULT name different targets")
        bad += 1
    if len(catalog_targets.DEFAULT) != len(set(catalog_targets.DEFAULT)):
        out.append("selftest: DEFAULT lists a target twice")
        bad += 1
    return bad


def the_plan_imposes_the_declared_order(out: list[str]) -> int:
    """Check that a request is returned in `DEFAULT` order, not the order it was made in.

    ⚑⚑ THIS IS THE ARM A REQUEST-ORDER DRIVER FAILS. Two of these targets write sibling files a
    reader diffs together, so a sequence that varied with argv would churn that diff for no
    reason. Driving the request BACKWARDS is what makes the claim testable at all.
    """
    reversed_request = tuple(reversed(catalog_targets.DEFAULT))
    got = catalog_targets.plan(reversed_request)
    if got != catalog_targets.DEFAULT:
        out.append(f"selftest: plan returned {got!r}, not the declared order")
        return 1
    return 0


def a_repeated_target_is_planned_once(out: list[str]) -> int:
    """Check that naming one target twice renders it once.

    ⚑ REDUNDANT IS NOT CONTRADICTORY, so this de-duplicates rather than refusing. Rendering twice
    would write the same file twice; refusing would reject an invocation that stated a coherent
    request clumsily.
    """
    got = catalog_targets.plan((catalog_targets.INDEX, catalog_targets.INDEX))
    if got != (catalog_targets.INDEX,):
        out.append(f"selftest: a repeated target planned as {got!r}")
        return 1
    return 0


def a_subset_request_plans_only_that_subset(out: list[str]) -> int:
    """Check that asking for one catalog plans one catalog.

    ⚑ WITHOUT THIS, A DRIVER IGNORING ITS ARGUMENT AND ALWAYS RENDERING EVERYTHING would pass
    every other arm here. Two of the three consumers ask for exactly one target, so the subset is
    the majority case rather than an edge one.
    """
    bad = 0
    for one in catalog_targets.DEFAULT:
        got = catalog_targets.plan((one,))
        if got != (one,):
            out.append(f"selftest: the subset request {one!r} planned as {got!r}")
            bad += 1
    return bad


def an_unknown_target_is_refused_by_name(out: list[str]) -> int:
    """Check that an unknown target raises, naming both the offender and the valid set.

    ⚑⚑ A BARE `KeyError` ALSO RAISES, which is why this asserts the CONTENT of the message. The
    superseded driver's failure mode is an exception that names neither the tool, the wrong
    target, nor what was allowed — so a case checking only that something was raised would pass
    on the defect.
    """
    bad = 0
    try:
        catalog_targets.plan(("sitmap",))
    except ValueError as exc:
        text = str(exc)
        if "sitmap" not in text:
            out.append("selftest: the refusal does not name the unknown target")
            bad += 1
        if catalog_targets.SITEMAP not in text:
            out.append("selftest: the refusal does not name the valid targets")
            bad += 1
    else:
        out.append("selftest: an unknown target was ACCEPTED")
        bad += 1
    return bad


def every_unknown_target_is_reported_not_just_the_first(out: list[str]) -> int:
    """Check that two mistyped targets are both named in one refusal.

    ⚑ STOPPING AT THE FIRST TURNS ONE WRONG INVOCATION INTO TWO ROUND-TRIPS, and the second
    mistake is then discovered only after the first is fixed. `unknown` is checked directly here
    because it is the diagnostic `plan` renders into its message.
    """
    got = catalog_targets.unknown(("sitmap", catalog_targets.INDEX, "usge"))
    if got != ("sitmap", "usge"):
        out.append(f"selftest: the unknown census returned {got!r}")
        return 1
    return 0


def a_wholly_known_request_reports_no_unknowns(out: list[str]) -> int:
    """Check that the full valid request yields an empty unknown census — the positive control.

    ⚑ WITHOUT THIS ARM, AN `unknown` RETURNING EVERY INPUT would satisfy the arm above and refuse
    every legitimate invocation. A census that reports offenders needs a case proving it can also
    report none, or its zero is never established.
    """
    got = catalog_targets.unknown(catalog_targets.DEFAULT)
    if got:
        out.append(f"selftest: the full valid request reported unknowns {got!r}")
        return 1
    return 0


FAMILY = witness_family.of(
    key="catalog_targets",
    apex="the catalog target vocabulary is closed and self-agreeing, plans a request into the "
    "declared order with repeats collapsed, and refuses an unknown target by naming both "
    "the offender and the valid set rather than raising a bare lookup error",
    subject="the target vocabulary `substrate.catalog_targets` declares, planned offline",
    members=(
        witness_family.Member(
            name="the_vocabulary_and_its_sequence_agree",
            claim="the membership set is exactly the rendered sequence, with no duplicates",
            cases=2,
        ),
        witness_family.Member(
            name="the_plan_imposes_the_declared_order",
            claim="a request is returned in declared order, not the order it was made in",
        ),
        witness_family.Member(
            name="a_repeated_target_is_planned_once",
            claim="naming one target twice renders it once",
        ),
        witness_family.Member(
            name="a_subset_request_plans_only_that_subset",
            claim="asking for one catalog plans one catalog",
            cases=5,
        ),
        witness_family.Member(
            name="an_unknown_target_is_refused_by_name",
            claim="an unknown target raises, naming the offender and the valid set",
            cases=2,
        ),
        witness_family.Member(
            name="every_unknown_target_is_reported_not_just_the_first",
            claim="two mistyped targets are both named in one refusal",
        ),
        witness_family.Member(
            name="a_wholly_known_request_reports_no_unknowns",
            claim="the full valid request yields an empty unknown census",
            premises=("every_unknown_target_is_reported_not_just_the_first",),
        ),
    ),
)

_ARMS = (
    the_vocabulary_and_its_sequence_agree,
    the_plan_imposes_the_declared_order,
    a_repeated_target_is_planned_once,
    a_subset_request_plans_only_that_subset,
    an_unknown_target_is_refused_by_name,
    every_unknown_target_is_reported_not_just_the_first,
    a_wholly_known_request_reports_no_unknowns,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/catalog_targets_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
