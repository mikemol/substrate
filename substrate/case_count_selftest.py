#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.case_count` — the floor, and what the reader must not claim.

⚑⚑⚑ THE BELOW-FLOOR CASE IS THE ONE WITH TEETH. Every arm contributes at least one case, so a
declared total under the arm count means an arm was added and the sum was not — and the suite
still prints a green `n/n`, smaller than before, with nothing holding a prior for what it should
be. That is the whole failure mode, and it is one comparison away from being visible.

⚑⚑ AND UNREADABLE MUST NOT COLLAPSE INTO ZERO. A suite computing its total some other way
(`len(_CASES) + 2 + …`, which several do) is not a suite with no total — reading it as 0 would
report every already-derived suite as maximally broken, a false finding pointing at the files
that solved the problem first. `census-green-is-a-fact-about-the-census`, inverted: a false RED is
what an over-eager parser produces here.

⚑ THE FIXTURES ARE SOURCE STRINGS, NOT FILES IN THE TREE. A case reading a real suite passes or
fails on that suite's current arithmetic, so it would report the tree rather than the reader — and
would go green the moment someone edited an unrelated suite.

⚑⚑⚑ AND THE UNREADABLE ARM WAS TWO CLAIMS SCORED AS ONE. Its second branch — that an unreadable
total must not ALSO be reported below floor — sat behind an `elif`, so it ran only once the first
branch had held. That guard is not fusion, it is a PREMISE: the coherence claim is meaningful only
after the classification claim holds. The two are now separate arms with the edge declared in
`FAMILY`, and `_CASE_COUNT` rose by one — not because a split invented an assertion, but because
the original number never counted the second one.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.witness import witness_family

from substrate import case_count

# A suite whose declared total is a literal sum ABOVE its arm count — the normal shape.
_CONSISTENT = """_ARMS = (one, two, three)

_CASE_COUNT = 1 + 2 + 1
"""

# A suite that gained a fourth arm and did not gain a fourth term.
_BELOW_FLOOR = """_ARMS = (one, two, three, four)

_CASE_COUNT = 1 + 1 + 1
"""

# A suite deriving part of its total — several in this tree do exactly this.
_DERIVED = """_ARMS = (one, two)

_CASE_COUNT = len(_CASES) + 1
"""

# A file that is not a suite at all.
_NOT_A_SUITE = """def helper() -> int:
    return 0
"""

_THREE_ARMS = 3
_FOUR_ARMS = 4


def _suite(where: str, text: str) -> case_count.Suite | None:
    """Write a fixture module and read it back."""
    path = Path(where) / "fixture_selftest.py"
    path.write_text(text, encoding="utf-8")
    return case_count.read(path)


def a_literal_sum_is_read(out: list[str]) -> int:
    """Check a declared total spelled as a literal addition is evaluated."""
    with tempfile.TemporaryDirectory() as where:
        got = _suite(where, _CONSISTENT)
    if got is None or got.declared != _FOUR_ARMS:
        out.append(f"selftest: a literal sum read as {got!r}")
        return 1
    return 0


def the_arm_roster_is_counted(out: list[str]) -> int:
    """Check the arm count comes from the roster tuple."""
    with tempfile.TemporaryDirectory() as where:
        got = _suite(where, _CONSISTENT)
    if got is None or got.arms != _THREE_ARMS:
        out.append(f"selftest: the arm roster counted {got!r}")
        return 1
    return 0


def a_total_above_the_arm_count_is_not_a_defect(out: list[str]) -> int:
    """Check the normal shape is left alone.

    ⚑ ARMS ASSERT SEVERAL FACTS, ROUTINELY. A reader treating total > arms as drift would flag
    almost every suite in the tree and train a reader to ignore it — the shape a ratchet over a
    census exists to avoid.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _suite(where, _CONSISTENT)
    if got is None or got.below_floor:
        out.append(f"selftest: a consistent suite was reported below floor: {got!r}")
        return 1
    return 0


def a_total_below_the_arm_count_is_reported(out: list[str]) -> int:
    """Check the drift IS caught — the positive control.

    ⚑⚑ WITHOUT THIS, A READER THAT NEVER FLAGGED ANYTHING would satisfy the case above. The pair
    says the predicate discriminates rather than being permanently quiet.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _suite(where, _BELOW_FLOOR)
    if got is None or not got.below_floor:
        out.append(f"selftest: an arm contributing nothing was not reported: {got!r}")
        return 1
    return 0


def a_derived_total_is_unreadable(out: list[str]) -> int:
    """Check a computed total is reported UNREADABLE rather than parsed as 0.

    ⚑⚑ READING IT AS ZERO WOULD REPORT EVERY ALREADY-DERIVED SUITE AS MAXIMALLY BROKEN — a false
    red pointing at the files that solved this problem before the reader existed. MEASURED: eight
    suites in `substrate/` compute their total this way.

    ⚑ THE CLASSIFICATION CLAIM, AND THE ONE ITS SIBLING RESTS ON. `unreadable` is what the reader
    must say about a total it could not evaluate; whether that verdict is COHERENT with the
    reader's other fields is a separate question, and one that cannot even be posed until this
    holds.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _suite(where, _DERIVED)
    if got is None or not got.unreadable:
        out.append(f"selftest: a derived total was not reported unreadable: {got!r}")
        return 1
    return 0


def an_unreadable_total_is_not_also_below_floor(out: list[str]) -> int:
    """Check a suite reported unreadable is not ALSO reported below floor.

    ⚑⚑ THE TWO FLAGS TOGETHER ARE NOT TWO DEFECTS — THEY ARE ONE DEFECT SURFACING AS AN INCOHERENT
    VERDICT. `below_floor` is a comparison against a declared total, so a reader that could not
    read the total has nothing to compare; asserting both says the suite is simultaneously
    unmeasured and measured-and-wrong, and a reader told both can act on neither.

    ⚑ IT RESTS ON `a_derived_total_is_unreadable`, WHICH IS WHY THAT EDGE IS DECLARED RATHER THAN
    IMPLIED BY AN `elif`. This claim is vacuous on a suite whose total read fine, so it is
    meaningful only where the sibling holds — and while that guard lived as control flow inside
    one arm, the second assertion had neither a name nor a place in the count.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _suite(where, _DERIVED)
    if got is not None and got.unreadable and got.below_floor:
        out.append("selftest: an unreadable total was ALSO reported below floor")
        return 1
    return 0


def a_non_suite_is_not_a_suite(out: list[str]) -> int:
    """Check a module with no arm roster is skipped, not counted as an empty one.

    ⚑ A FILE WITH NO ROSTER IS NOT A SUITE WITH ZERO ARMS. Counting it would put every helper
    module in the denominator and make the census report the directory rather than the suites.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _suite(where, _NOT_A_SUITE)
    if got is not None:
        out.append(f"selftest: a non-suite was read as a suite: {got!r}")
        return 1
    return 0


def an_empty_census_says_so(out: list[str]) -> int:
    """Check the render names its own emptiness.

    ⚑ A BARE EMPTY STRING CANNOT DISTINGUISH *no suites* FROM *nothing read* — the false-zero
    shape every census in this tree prints its denominator to avoid.
    """
    if "no suite" not in case_count.render(()):
        out.append("selftest: an empty census does not name its emptiness")
        return 1
    return 0


def a_clean_census_says_it_checked(out: list[str]) -> int:
    """Check a census with no findings reports the comparison, not silence.

    ⚑ SILENCE AND SUCCESS ARE THE SAME BYTES. A reader that printed nothing on a clean tree
    cannot be distinguished from one that failed to run.
    """
    clean = (case_count.Suite(path="a.py", arms=2, declared=3),)
    if "at or above" not in case_count.render(clean):
        out.append("selftest: a clean census does not say what it checked")
        return 1
    return 0


def the_render_surfaces_a_below_floor_suite(out: list[str]) -> int:
    """Check the defect is marked, not listed as one more row."""
    broken = (case_count.Suite(path="a.py", arms=4, declared=3),)
    if "BELOW FLOOR" not in case_count.render(broken):
        out.append("selftest: the render does not surface a below-floor suite")
        return 1
    return 0


# ⚑⚑ THE FAMILY EXISTS FOR THE PREMISE EDGES, NOT FOR THE ROSTER. Two of these arms are positive
# controls and one is a coherence claim guarded by a sibling's outcome; all three relationships
# lived in prose, where deleting the arm they protect leaves the protected claim green and silent.
FAMILY = witness_family.of(
    key="case-count",
    apex="the case-count reader states a floor it can defend: what it read, what it could NOT "
    "read, and which of those two a finding rests on",
    subject="declared-total spellings a suite in this tree can use",
    members=(
        witness_family.Member(
            name="a_literal_sum_is_read", claim="a total spelled as a literal addition is evaluated"
        ),
        witness_family.Member(
            name="the_arm_roster_is_counted", claim="the arm count comes from the roster tuple"
        ),
        witness_family.Member(
            name="a_total_above_the_arm_count_is_not_a_defect",
            claim="the normal shape — arms asserting several facts — is left alone",
        ),
        witness_family.Member(
            name="a_total_below_the_arm_count_is_reported",
            claim="drift IS caught, so the predicate discriminates rather than being quiet",
            premises=("a_total_above_the_arm_count_is_not_a_defect",),
        ),
        witness_family.Member(
            name="a_derived_total_is_unreadable",
            claim="a computed total reads UNREADABLE rather than parsing as 0, which would "
            "report every already-derived suite as maximally broken",
        ),
        witness_family.Member(
            name="an_unreadable_total_is_not_also_below_floor",
            claim="a verdict cannot say a suite is both unmeasured and measured-and-wrong — the "
            "same defect surfacing twice, which a reader can act on neither way",
            premises=("a_derived_total_is_unreadable",),
        ),
        witness_family.Member(
            name="a_non_suite_is_not_a_suite",
            claim="a module with no arm roster is skipped, not counted as an empty suite",
        ),
        witness_family.Member(
            name="an_empty_census_says_so",
            claim="the render names its own emptiness rather than printing nothing",
        ),
        witness_family.Member(
            name="a_clean_census_says_it_checked",
            claim="a census with no findings reports the comparison, since silence and success "
            "are the same bytes",
        ),
        witness_family.Member(
            name="the_render_surfaces_a_below_floor_suite",
            claim="the defect is marked, not listed as one more row",
        ),
    ),
)

_ARMS = (
    a_literal_sum_is_read,
    the_arm_roster_is_counted,
    a_total_above_the_arm_count_is_not_a_defect,
    a_total_below_the_arm_count_is_reported,
    a_derived_total_is_unreadable,
    an_unreadable_total_is_not_also_below_floor,
    a_non_suite_is_not_a_suite,
    an_empty_census_says_so,
    a_clean_census_says_it_checked,
    the_render_surfaces_a_below_floor_suite,
)

# ⚑ 9 → 10, AND THAT IS A FINDING ABOUT THE OLD NUMBER, NOT A BROKEN INVARIANT. The `elif` branch
# was an assertion this suite ran and never counted; naming it gives it a place in the total.
_CASE_COUNT = FAMILY.count


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"case-count selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"case-count selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
