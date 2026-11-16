#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.cone_blindness` — a shared rank over unshared measurements.

⚑⚑⚑ THE SAME-RANK-DIFFERENT-SIZE CASE IS THE ITEM. Two items at one declared leverage whose
discovered sizes differ by orders of magnitude mean the rank is uninformed by the measurement —
the live shape being `T23-sibling` at 218 and `T23-local` at 12, both `lev 1`. The arms below pin
that this reads as a finding and that a class in agreement does not.

⚑⚑ THE ORDER-INDEPENDENCE CASE IS WHY THE SIGNATURE LOOKS LIKE THIS. The origin's first shape read
a shared memo holding only items that had already run, so the answer moved with the witness's
position in the sweep — it saw 1 of 20 sizes when it fired first, and the ordering then ranked the
highest-leverage item BLOCKED off that. Taking both populations as arguments is what makes the
answer the same whether it runs first, last, or alone, and a case asserts exactly that.

⚑ THE FIXTURES ARE DICTS. A case reading the live bib measures today's warrant graph and today's
sizes — both of which move every time an item lands, which is every step of this arc.
"""

from __future__ import annotations

import sys

from substrate import cone_blindness

_SPAN = cone_blindness.SPAN

# The live shape: one rank, two sizes an order of magnitude apart. ⚑ THE TWO SIZES ARE NAMED so
# the bounds arm asserts against a declaration rather than repeating a literal the fixture already
# states — a number typed twice is how a case starts checking itself instead of the reader.
_BIG = 218
_SMALL = 12

_LEVERAGE = {"big": 1, "small": 1, "alone": 2}
_SIZES = {"big": _BIG, "small": _SMALL, "alone": 4}


def a_spanning_class_is_blind(out: list[str]) -> int:
    """Check a class whose members differ by an order of magnitude is a finding — THE ITEM.

    ⚑⚑⚑ THE RANK SAYS EQUAL AND THE MEASUREMENT SAYS OTHERWISE. Nothing in the ordering table
    surfaces this; the two items sit adjacent at one rank and the difference is invisible.
    """
    rows = cone_blindness.classes(_LEVERAGE, _SIZES)
    found = cone_blindness.blind(rows)
    if len(found) != 1 or found[0].leverage != 1:
        out.append(f"selftest: the blind classes read as {found!r}")
        return 1
    return 0


def an_agreeing_class_is_not_blind(out: list[str]) -> int:
    """Check members within the span are not reported — the POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS, A READER CALLING EVERY CLASS BLIND passes the case above and reports the
    whole table as debt. The pair says the threshold discriminates.
    """
    rows = cone_blindness.classes({"a": 1, "b": 1}, {"a": 20, "b": 15})
    if cone_blindness.blind(rows):
        out.append("selftest: an agreeing class was reported blind")
        return 1
    return 0


def a_singleton_class_is_never_blind(out: list[str]) -> int:
    """Check a class with one member is not a finding.

    ⚑ ONE MEMBER MEANS THE RANK HAS NOTHING TO BE WRONG ABOUT. Counting it would report every
    unique leverage value as debt — a census whose findings scale with the number of ranks.
    """
    rows = cone_blindness.classes({"only": 3}, {"only": 5000})
    if cone_blindness.blind(rows):
        out.append("selftest: a singleton class was reported blind")
        return 1
    return 0


def the_threshold_is_the_declared_span(out: list[str]) -> int:
    """Check the boundary is where the declared constant says.

    ⚑ A THRESHOLD TYPED TWICE would let the report claim one bar while applying another.
    """
    at = cone_blindness.classes({"a": 1, "b": 1}, {"a": _SPAN, "b": 1})
    under = cone_blindness.classes({"a": 1, "b": 1}, {"a": _SPAN - 1, "b": 1})
    if not cone_blindness.blind(at):
        out.append(f"selftest: a {_SPAN}x span was not reported blind")
        return 1
    if cone_blindness.blind(under):
        out.append(f"selftest: a {_SPAN - 1}x span was reported blind")
        return 1
    return 0


def a_zero_size_item_is_excluded(out: list[str]) -> int:
    """Check an unmeasured item does not join a class as a small member.

    ⚑⚑ FOLDING A ZERO IN AS SMALL would make every class it joins span infinitely — an item that
    has not been measured against its rank at all, reported as the strongest evidence the rank is
    wrong.
    """
    rows = cone_blindness.classes({"a": 1, "b": 1}, {"a": 5, "b": 0})
    if cone_blindness.blind(rows):
        out.append("selftest: a zero-size item produced a blind class")
        return 1
    members = [key for row in rows for key, _size in row.members]
    if "b" in members:
        out.append(f"selftest: a zero-size item joined a class: {members!r}")
        return 1
    return 0


def the_answer_does_not_depend_on_call_order(out: list[str]) -> int:
    """Check the same populations give the same answer in any insertion order.

    ⚑⚑⚑ THE DEFECT THE SIGNATURE EXISTS TO REMOVE. The origin read a memo holding only items that
    had already run, so its figure moved with its position in the sweep — 1 of 20 sizes when it
    fired first, and a downstream reader ranked the highest-leverage item BLOCKED off that.
    """
    forward = cone_blindness.classes(_LEVERAGE, dict(_SIZES))
    backward = cone_blindness.classes(
        dict(reversed(list(_LEVERAGE.items()))), dict(reversed(list(_SIZES.items())))
    )
    if forward != backward:
        out.append(f"selftest: the answer moved with order:\n{forward!r}\n{backward!r}")
        return 1
    return 0


def a_partial_population_is_not_silently_smaller(out: list[str]) -> int:
    """Check a subset of sizes yields a class count matching that subset.

    ⚑ THE DENOMINATOR IS WHAT WAS PASSED IN, and it is visible in the result. A reader handed
    half the population gets half the classes, not a quiet claim about the whole tree.
    """
    whole = cone_blindness.classes(_LEVERAGE, _SIZES)
    part = cone_blindness.classes(_LEVERAGE, {"big": 218})
    if len(part) >= len(whole):
        out.append(f"selftest: a partial population yielded {len(part)} class(es)")
        return 1
    return 0


def an_unknown_key_ranks_at_zero(out: list[str]) -> int:
    """Check a size with no declared leverage is still grouped.

    ⚑ DROPPING IT WOULD HIDE THE SHARPEST CASE: an item nothing declares a rank for, carrying a
    large discovered size, is exactly the cone the ordering cannot see.
    """
    rows = cone_blindness.classes({}, {"orphan": 90, "other": 4})
    if not rows or rows[0].leverage != 0:
        out.append(f"selftest: an undeclared key grouped as {rows!r}")
        return 1
    return 0


def the_members_are_largest_first(out: list[str]) -> int:
    """Check the report leads with the size that makes the case."""
    rows = cone_blindness.classes(_LEVERAGE, _SIZES)
    found = cone_blindness.blind(rows)
    if not found or found[0].members[0][0] != "big":
        out.append(f"selftest: the members read as {found!r}")
        return 1
    return 0


def the_span_bounds_are_reported(out: list[str]) -> int:
    """Check a class carries both ends of its range."""
    rows = cone_blindness.classes(_LEVERAGE, _SIZES)
    found = cone_blindness.blind(rows)
    if not found or found[0].low != _SMALL or found[0].high != _BIG:
        out.append(f"selftest: the bounds read as {found!r}")
        return 1
    return 0


def an_empty_population_is_unmeasured(out: list[str]) -> int:
    """Check no discovered sizes renders as unmeasured, not as clean."""
    text = cone_blindness.render(())
    if "UNMEASURED" not in text:
        out.append(f"selftest: an empty population renders as {text!r}")
        return 1
    return 0


def the_render_names_every_member(out: list[str]) -> int:
    """Check the finding lists the items whose rank disagrees.

    ⚑ A CLASS COUNT IS NOT ACTIONABLE — the reader needs the two keys to see which rank to trust.
    """
    text = cone_blindness.render(cone_blindness.classes(_LEVERAGE, _SIZES))
    if f"big={_BIG}" not in text or f"small={_SMALL}" not in text:
        out.append(f"selftest: the render omits a member:\n{text}")
        return 1
    return 0


def a_clean_census_states_its_denominator(out: list[str]) -> int:
    """Check the closed reading says how many classes it examined."""
    text = cone_blindness.render(cone_blindness.classes({"a": 1, "b": 1}, {"a": 20, "b": 15}))
    if "class(es)" not in text:
        out.append(f"selftest: the clean render states no denominator: {text!r}")
        return 1
    return 0


_ARMS = (
    a_spanning_class_is_blind,
    an_agreeing_class_is_not_blind,
    a_singleton_class_is_never_blind,
    the_threshold_is_the_declared_span,
    a_zero_size_item_is_excluded,
    the_answer_does_not_depend_on_call_order,
    a_partial_population_is_not_silently_smaller,
    an_unknown_key_ranks_at_zero,
    the_members_are_largest_first,
    the_span_bounds_are_reported,
    an_empty_population_is_unmeasured,
    the_render_names_every_member,
    a_clean_census_states_its_denominator,
)

_CASE_COUNT = 1 + 1 + 1 + 2 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"cone-blindness selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"cone-blindness selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
