#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.promote_agree` — and the one property worth pinning in it.

⚑⚑⚑ `rows` IS WHAT THESE CASES ARE ABOUT, BECAUSE IT IS WHERE THE COMPARISON CAN LIE. An arm that
could not run must report UNRUN, never agreement: two absences are not a match, and calling them
one is how a comparison certifies its own blind spot. That is the same defect
`check_mypy_ratchet`'s unrunnable sentinel exists to prevent one layer down, and it is the failure
this module would produce SILENTLY — a green comparison over an implementation nobody executed
reads exactly like a promotion that agreed.

⚑⚑ AND `None` IS DELIBERATELY NOT `set()`. An empty prior population and an ABSENT one are
opposite facts: the first says the old implementation ran and found nothing, the second says it
never spoke. A case distinguishing them is the whole point, so both are asserted — including the
pair that would collapse if `if not prior` replaced `if prior is None`, which is the natural typo
here and the one no other case catches.

⚑⚑ THE SUBPROCESS ARMS ARE NOT WRITTEN, AND THAT IS A DECISION RATHER THAN AN OMISSION.
`_prior_suites`, `_prior_population` and `_prior_census` each run a PRIOR implementation as a
program — the very thing being retired. A case pinning their output would enshrine a corpse's
answer as the authority, inverting the migration this module exists to measure: a promoted module
that FIXES a bug in its ancestor SHOULD differ. Worse, such a case goes red on the DELETION that
is the arc's goal — a case that fails when the work succeeds. What is falsifiable without the
corpse is the comparison logic, and that is what is covered.

⚑⚑ A ROSTER-IS-NON-EMPTY ARM WAS WRITTEN AND WITHDRAWN, the third instance in this batch.
`_ARMS` is a literal tuple of callables, so both the emptiness branch and the not-callable branch
are statically unreachable and mypy refuses the file — the type gate saying, correctly, that the
assertion is about the source text rather than about behaviour. **A case that cannot fail is worse
than an absent one**, so it is recorded here rather than written.

⚑ NOR IS `main` PINNED AGAINST THE LIVE TREE, for the same deletion reason. The reporting contract
below survives that deletion; the arms do not.
"""

from __future__ import annotations

import sys

from substrate import promote_agree


def an_unrunnable_arm_is_reported_as_unrun(out: list[str]) -> int:
    """Check `None` yields UNRUN — THE ARM THIS SUITE EXISTS FOR.

    ⚑⚑⚑ TWO ABSENCES ARE NOT A MATCH. If a prior implementation did not run, the honest report
    is that nothing was compared; calling it agreement makes the comparison certify its own
    blind spot, and the reader who sees `ok` has no way to learn the arm never executed.
    """
    lines = promote_agree.rows("thing", None, {"a"})
    if len(lines) != 1:
        out.append(f"selftest: an unrunnable arm rendered {len(lines)} line(s)")
        return 1
    if "UNRUN" not in lines[0]:
        out.append(f"selftest: an unrunnable arm rendered {lines[0]!r}")
        return 1
    if "ok" in lines[0]:
        out.append(f"selftest: an unrunnable arm reads as agreement: {lines[0]!r}")
        return 1
    return 0


def an_unrunnable_arm_with_an_empty_promoted_side_is_still_unrun(out: list[str]) -> int:
    """Check UNRUN survives the case that would look like a match — THE COLLAPSE ARM.

    ⚑⚑ THIS IS THE PAIR THAT `if not prior` WOULD BREAK. A `None` prior and an empty promoted
    set are the exact inputs under which a falsy test and an identity test diverge: the natural
    typo reports `0 item(s), identical` over a comparison that never happened.
    """
    lines = promote_agree.rows("thing", None, set())
    if "UNRUN" not in lines[0]:
        out.append(f"selftest: an unrunnable arm with an empty result rendered {lines[0]!r}")
        return 1
    return 0


def an_empty_prior_is_not_an_absent_one(out: list[str]) -> int:
    """Check `set()` compares rather than reporting UNRUN — the other side of the distinction.

    ⚑ AN EMPTY PRIOR POPULATION IS A MEASUREMENT. It says the old implementation ran and found
    nothing, which against a non-empty promoted side is a DIFF worth reading — not an absence.
    """
    lines = promote_agree.rows("thing", set(), {"a"})
    if any("UNRUN" in ln for ln in lines):
        out.append(f"selftest: an empty prior population read as unrunnable: {lines!r}")
        return 1
    if "DIFF" not in lines[0]:
        out.append(f"selftest: empty-vs-one rendered {lines[0]!r}")
        return 1
    return 0


def two_empty_sides_agree(out: list[str]) -> int:
    """Check two RUN implementations that both found nothing are a match.

    ⚑ THE CONTRAST WITH THE UNRUN ARMS IS THE WHOLE POINT. Nothing-vs-nothing IS agreement when
    both sides spoke; it is not when one did not.
    """
    lines = promote_agree.rows("thing", set(), set())
    if "ok" not in lines[0]:
        out.append(f"selftest: two empty populations rendered {lines[0]!r}")
        return 1
    if any("UNRUN" in ln for ln in lines):
        out.append("selftest: two ran-and-found-nothing sides read as unrunnable")
        return 1
    return 0


def identical_populations_report_ok_with_a_count(out: list[str]) -> int:
    """Check a match names how many items agreed — a verdict with no size cannot be weighed."""
    members = {"a", "b"}
    lines = promote_agree.rows("thing", set(members), set(members))
    if len(lines) != 1:
        out.append(f"selftest: a match rendered {len(lines)} line(s)")
        return 1
    if "ok" not in lines[0]:
        out.append(f"selftest: identical populations rendered {lines[0]!r}")
        return 1
    if f"{len(members)} item(s)" not in lines[0]:
        out.append(f"selftest: the match does not carry its size: {lines[0]!r}")
        return 1
    return 0


def a_difference_reports_both_counts(out: list[str]) -> int:
    """Check a DIFF names each side's size, so the direction of the drift is readable.

    ⚑ WHICH SIDE SHRANK IS THE ACTIONABLE FACT. Every recorded failure of the predicate this
    compares was a population that silently SHRANK — none showed as a failure, each showed as a
    smaller green total.
    """
    prior = {"a", "b", "c"}
    lines = promote_agree.rows("thing", set(prior), {"a"})
    if "DIFF" not in lines[0]:
        out.append(f"selftest: differing populations rendered {lines[0]!r}")
        return 1
    if f"prior={len(prior)}" not in lines[0] or "promoted=1" not in lines[0]:
        out.append(f"selftest: the DIFF does not carry both counts: {lines[0]!r}")
        return 1
    return 0


def a_difference_names_the_items_on_each_side(out: list[str]) -> int:
    """Check both asymmetries are rendered, and labelled by which side holds them."""
    lines = promote_agree.rows("thing", {"gone"}, {"added"})
    body = "\n".join(lines[1:])
    if "only-prior: gone" not in body:
        out.append(f"selftest: an item lost by the promotion is not named: {body!r}")
        return 1
    if "only-promoted: added" not in body:
        out.append(f"selftest: an item gained by the promotion is not named: {body!r}")
        return 1
    return 0


def a_long_difference_is_bounded(out: list[str]) -> int:
    """Check the item listing is capped — a 400-line diff helps nobody read it.

    ⚑ A DIFF LONGER THAN THE CAP IS A DESIGN DISAGREEMENT rather than a discrepancy, and the
    counts on the header line already state the size. The cap is read from the module's own
    constant rather than typed here, so raising it does not expire this case.
    """
    cap = promote_agree._SHOW  # noqa: SLF001 — the bound under test
    prior = {f"item{n:03d}" for n in range(cap * 3)}
    lines = promote_agree.rows("thing", prior, set())
    listed = [ln for ln in lines if "only-prior:" in ln]
    if len(listed) != cap:
        out.append(
            f"selftest: {len(prior)} differing items rendered {len(listed)} row(s), "
            f"expected the cap of {cap}"
        )
        return 1
    return 0


def the_item_listing_is_ordered(out: list[str]) -> int:
    """Check the named items are sorted, so a capped listing is stable across runs.

    ⚑⚑ THE INPUTS ARE SETS. Without an explicit sort the CAPPED listing would show a different
    arbitrary subset on each run, and a reader comparing two reports would read hash ordering as
    the tree changing.
    """
    prior = {"c", "a", "b"}
    listed = [
        ln.split("only-prior: ")[1]
        for ln in promote_agree.rows("thing", set(prior), set())
        if "only-prior:" in ln
    ]
    if listed != sorted(prior):
        out.append(f"selftest: the item listing is {listed!r}, not sorted")
        return 1
    return 0


def the_label_reaches_every_verdict(out: list[str]) -> int:
    """Check the caller's label appears whichever branch is taken.

    ⚑ THE THREE VERDICTS ARE READ TOGETHER IN ONE REPORT. A row that omitted its label would be
    unattributable — the reader would know something disagreed, not what.
    """
    label = "the-arm-name"
    for prior in (None, {"a"}, set()):
        first = promote_agree.rows(label, prior, {"a"})[0]
        if label not in first:
            out.append(f"selftest: a verdict over {prior!r} omits its label: {first!r}")
            return 1
    return 0


def the_three_verdicts_are_distinguishable(out: list[str]) -> int:
    """Check UNRUN, ok and DIFF render as three different things — the collapse guard.

    ⚑⚑ A RENDERER RETURNING ONE CONSTANT passes several arms above individually. What must hold
    is that the three states are mutually distinguishable in the text a reader sees, since the
    exit code carries only `1 if any differs or could not run` and cannot tell them apart.
    """
    verdicts = (
        promote_agree.rows("x", None, {"a"})[0],
        promote_agree.rows("x", {"a"}, {"a"})[0],
        promote_agree.rows("x", {"a"}, {"b"})[0],
    )
    if len(set(verdicts)) != len(verdicts):
        out.append(f"selftest: the three verdicts do not render distinctly: {verdicts!r}")
        return 1
    return 0


_ARMS = (
    an_unrunnable_arm_is_reported_as_unrun,
    an_unrunnable_arm_with_an_empty_promoted_side_is_still_unrun,
    an_empty_prior_is_not_an_absent_one,
    two_empty_sides_agree,
    identical_populations_report_ok_with_a_count,
    a_difference_reports_both_counts,
    a_difference_names_the_items_on_each_side,
    a_long_difference_is_bounded,
    the_item_listing_is_ordered,
    the_label_reaches_every_verdict,
    the_three_verdicts_are_distinguishable,
)

_CASE_COUNT = 3 + 1 + 2 + 2 + 3 + 2 + 2 + 1 + 1 + 3 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"promote-agree selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"promote-agree selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
