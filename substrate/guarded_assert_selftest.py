#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.guarded_assert` — the two guard spellings, and what is NOT a guard.

⚑⚑⚑ THE UNGUARDED CASE IS THE ONE WITH TEETH. A reader that called every `if` inside a
multi-assert arm a guard would pass every other case here and would report the whole population —
a work list identical to `arm_shape`'s multi-assert list, dressed as a finding. The canonical
accumulating arm (`if bad: out.append(...); bad += 1`, twice, no exit) runs BOTH checks on every
invocation, and both already have a place in the declared total. It must read as NOT guarded.

⚑⚑ AND THE NESTED-FUNCTION EXIT IS THE FALSE POSITIVE THAT WOULD BE INVISIBLE. `ast.walk` hands
back the `return` inside an inner helper, which would make every later append in the arm look
conditional on a jump that cannot leave the arm at all. That error runs in exactly one direction —
it manufactures premise edges — so it is the one the reader must be wrong about least.

⚑ THE FIXTURES ARE SOURCE STRINGS, NOT SUITES IN THE TREE. A case reading a real suite reports
that suite's current bodies rather than the reader, and would flip the moment another agent split
an arm underneath it — which is happening concurrently, and is why the reading carries a
denominator at all.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.witness import witness_family

from substrate import guarded_assert

# The `elif` spelling: the second assertion runs only where the first test was false.
_ELIF = '''def two_claims_one_resting(out: list[str]) -> int:
    """An elif-guarded second claim."""
    if first():
        out.append("first failed")
        return 1
    elif second():
        out.append("second failed")
        return 1
    return 0


_ARMS = (two_claims_one_resting,)
'''

# The early-exit spelling: a later sibling append runs only because an earlier check did not fire.
_EARLY_EXIT = '''def a_check_then_another(out: list[str]) -> int:
    """An exit-guarded second claim."""
    if first():
        out.append("first failed")
        return 1
    if second():
        out.append("second failed")
        return 1
    return 0


_ARMS = (a_check_then_another,)
'''

# The accumulating shape — the POSITIVE CONTROL. Both checks run every time; neither guards.
_UNGUARDED = '''def two_independent_claims(out: list[str]) -> int:
    """Two accumulating assertions."""
    bad = 0
    if first():
        out.append("first failed")
        bad += 1
    if second():
        out.append("second failed")
        bad += 1
    return bad


_ARMS = (two_independent_claims,)
'''

# An inner helper whose `return` must NOT be read as this arm's exit.
_NESTED_RETURN = '''def a_helper_returns_inside(out: list[str]) -> int:
    """An accumulating arm that happens to define a helper."""
    def pick(row: int) -> int:
        if row:
            return 1
        return 0

    bad = 0
    if pick(1):
        out.append("first failed")
        bad += 1
    if pick(2):
        out.append("second failed")
        bad += 1
    return bad


_ARMS = (a_helper_returns_inside,)
'''

# A file that declares no arm roster at all.
_NO_ROSTER = '''def looks_like_an_arm(out: list[str]) -> int:
    """No roster names it."""
    out.append("x")
    return 1
'''


def _reading(where: str, text: str) -> guarded_assert.Reading:
    """Write a fixture suite and read it back."""
    path = Path(where) / "fixture_selftest.py"
    path.write_text(text, encoding="utf-8")
    return guarded_assert.read(path)


def an_elif_guarded_assertion_is_found(out: list[str]) -> int:
    """Check the `elif` spelling is reported.

    ⚑ THIS IS THE SPELLING THAT MOVED `case_count_selftest` 9→10. The second branch ran on every
    invocation and had no term in the declared total, because the premise lived in the grammar
    where no count could see it.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _reading(where, _ELIF)
    if len(got.sites) != 1 or got.sites[0].guard != guarded_assert.GUARD_ELIF:
        out.append(f"selftest: the elif spelling read {got.sites!r}")
        return 1
    return 0


def an_early_exit_guarded_assertion_is_found(out: list[str]) -> int:
    """Check the early-`return` spelling is reported.

    ⚑⚑ THE GUARD IS NOT SPELLED AT THE GUARDED SITE. The second `if` reads exactly like an
    independent check; only the earlier branch's `return` says otherwise, which is why this one
    survived a hand reading and the elif did not.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _reading(where, _EARLY_EXIT)
    if len(got.sites) != 1 or got.sites[0].guard != guarded_assert.GUARD_EXIT:
        out.append(f"selftest: the early-exit spelling read {got.sites!r}")
        return 1
    return 0


def an_accumulating_arm_is_not_guarded(out: list[str]) -> int:
    """Check independent sibling checks read as NOT guarded — the positive control.

    ⚑⚑⚑ WITHOUT THIS, A READER CALLING EVERY `if` A GUARD passes every other case in this suite.
    It would report ~100 multi-assert arms as premise edges — a work list identical to the one
    `arm_shape` already prints, and worth nothing. Both checks here run on every invocation and
    both already have a term in the declared total.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _reading(where, _UNGUARDED)
    if got.sites != ():
        out.append(f"selftest: an accumulating arm was reported guarded: {got.sites!r}")
        return 1
    return 0


def a_nested_functions_return_is_not_this_arms_exit(out: list[str]) -> int:
    """Check a helper's `return` does not make later siblings look guarded.

    ⚑⚑ `ast.walk` DESCENDS INTO NESTED FUNCTIONS, so a naive exit search finds a jump that cannot
    leave the arm. The error runs one way — it MANUFACTURES premise edges — and a manufactured
    edge sends someone to split an arm that has nothing to split.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _reading(where, _NESTED_RETURN)
    if got.sites != ():
        out.append(f"selftest: a nested return was read as this arm's exit: {got.sites!r}")
        return 1
    return 0


def a_guarded_site_names_the_line_it_rests_on(out: list[str]) -> int:
    """Check a site carries the earlier line, not just its own.

    ⚑ THE EDGE IS THE FINDING, NOT THE SITE. A report naming only the guarded line hands a reader
    a location and no relation, and re-deriving which sibling it rests on is the hand-judgement
    this reader exists to remove.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _reading(where, _EARLY_EXIT)
    if not got.sites or got.sites[0].guard_line >= got.sites[0].line:
        out.append(f"selftest: a site does not name an EARLIER guard: {got.sites!r}")
        return 1
    return 0


def a_reading_carries_the_arms_it_read(out: list[str]) -> int:
    """Check the denominator travels with the count.

    ⚑⚑ `0 SITES OVER 0 ARMS` AND `0 SITES OVER 300 ARMS` ARE DIFFERENT FACTS. The arm census in
    this tree read 285 → 313 → 326 → 351 across three sittings while suites landed underneath it,
    so a bare count here is a claim about a population nobody recorded.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _reading(where, _UNGUARDED)
    if got.arms != 1 or got.suites != 1:
        out.append(f"selftest: the reading lost its denominator: {got.arms}/{got.suites}")
        return 1
    return 0


def a_module_with_no_roster_yields_nothing(out: list[str]) -> int:
    """Check a non-suite contributes neither sites nor denominator.

    ⚑ A FILE WITH NO ROSTER IS NOT A SUITE WITH ZERO ARMS. Counting it would inflate the
    denominator with every helper module and make the ratio report the directory.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _reading(where, _NO_ROSTER)
    if got != guarded_assert.Reading(sites=(), arms=0, suites=0):
        out.append(f"selftest: a rosterless module was read as a suite: {got!r}")
        return 1
    return 0


def an_empty_reading_says_so(out: list[str]) -> int:
    """Check the render names its own emptiness rather than printing a bare header.

    ⚑ SILENCE AND SUCCESS ARE THE SAME BYTES — the false-zero shape every census in this tree
    prints its denominator to avoid.
    """
    text = guarded_assert.render(guarded_assert.Reading(sites=(), arms=300, suites=40))
    if "no assertion site rests" not in text or "300 arm(s)" not in text:
        out.append(f"selftest: an empty reading does not state itself:\n{text}")
        return 1
    return 0


def the_render_states_what_it_is_not_claiming(out: list[str]) -> int:
    """Check the bound is printed with the reading, not left in a docstring.

    ⚑⚑ A WORK LIST THAT DOES NOT RESTATE ITS BOUND GETS READ AS A DEFECT LIST. Two arms in this
    tree were deliberately left unsplit — *"a count and five memberships over the SAME roster,
    neither guarding the other"* — and a reader handed a bare list would have split them.
    """
    rows = (guarded_assert.Site(suite="a.py", arm="one", line=9, guard="elif", guard_line=5),)
    text = guarded_assert.render(guarded_assert.Reading(sites=rows, arms=2, suites=1))
    if "not a defect" not in text:
        out.append(f"selftest: the render does not bound its own claim:\n{text}")
        return 1
    return 0


def _long() -> guarded_assert.Reading:
    """Return a reading longer than the render's default sample."""
    rows = tuple(
        guarded_assert.Site(suite="a.py", arm=f"arm{n}", line=n, guard="elif", guard_line=1)
        for n in range(guarded_assert.SAMPLE + 4)
    )
    return guarded_assert.Reading(sites=rows, arms=99, suites=1)


def a_truncated_listing_still_states_its_total(out: list[str]) -> int:
    """Check a long work list reports its full count, not just the sample."""
    long = _long()
    text = guarded_assert.render(long)
    if f"{len(long.sites)} guarded site(s)" not in text:
        out.append(f"selftest: the truncated listing lost its total:\n{text}")
        return 1
    return 0


def a_lifted_limit_spells_every_row(out: list[str]) -> int:
    """Check `limit` actually lifts the truncation.

    ⚑⚑ A TRUNCATED WORK LIST IS NOT A WORK LIST. Every row here has to be READ and judged
    individually — a premise edge and one claim checked at two points look identical in a summary
    — so a census that could only ever print its first twenty rows would be an instrument nobody
    could act on. The default keeps a bare run readable; this says the lift is real.
    """
    long = _long()
    text = guarded_assert.render(long, limit=len(long.sites))
    if "more guarded site(s)" in text or f"arm{len(long.sites) - 1}" not in text:
        out.append(f"selftest: a lifted limit still truncated:\n{text}")
        return 1
    return 0


# ⚑⚑ THE FAMILY IS HERE FOR THE PREMISE EDGES — the relation this module exists to FIND, declared
# in the one place a reader of this suite would look for it. Both controls keep a sibling honest,
# and that edge lived only in prose until `witness_family.Member.premises` gave it a field.
FAMILY = witness_family.of(
    key="guarded-assert",
    apex="the guarded-assert reader finds assertions that rest on a sibling's outcome, and "
    "discriminates them from the accumulating siblings that merely look alike",
    subject="control-flow spellings that make one assertion conditional on another",
    members=(
        witness_family.Member(
            name="an_elif_guarded_assertion_is_found",
            claim="the `elif` spelling is reported — the premise the grammar states and no count "
            "could see",
        ),
        witness_family.Member(
            name="an_early_exit_guarded_assertion_is_found",
            claim="the early-`return` spelling is reported, where the guard is not spelled at the "
            "guarded site at all",
        ),
        witness_family.Member(
            name="an_accumulating_arm_is_not_guarded",
            claim="independent sibling checks read as NOT guarded, so the reader discriminates "
            "rather than reporting the whole multi-assert population",
            premises=(
                "an_elif_guarded_assertion_is_found",
                "an_early_exit_guarded_assertion_is_found",
            ),
        ),
        witness_family.Member(
            name="a_nested_functions_return_is_not_this_arms_exit",
            claim="a helper's `return` does not manufacture a premise edge — the one direction "
            "this reader must not be wrong in",
            premises=("an_early_exit_guarded_assertion_is_found",),
        ),
        witness_family.Member(
            name="a_guarded_site_names_the_line_it_rests_on",
            claim="a site carries the EARLIER line, so the finding is the edge and not a bare "
            "location a reader must re-derive",
        ),
        witness_family.Member(
            name="a_reading_carries_the_arms_it_read",
            claim="the denominator travels with the count, since the arm population moves under "
            "this reader between sittings",
        ),
        witness_family.Member(
            name="a_module_with_no_roster_yields_nothing",
            claim="a file with no roster is skipped rather than counted as a suite with no arms",
        ),
        witness_family.Member(
            name="an_empty_reading_says_so",
            claim="the render names its own emptiness, since silence and success are the same "
            "bytes",
        ),
        witness_family.Member(
            name="the_render_states_what_it_is_not_claiming",
            claim="the bound is printed with the reading, so a work list is not acted on as a "
            "defect list",
        ),
        witness_family.Member(
            name="a_truncated_listing_still_states_its_total",
            claim="a truncated listing reports its full count rather than its sample",
        ),
        witness_family.Member(
            name="a_lifted_limit_spells_every_row",
            claim="`limit` really lifts the truncation, since a work list whose rows must each be "
            "judged individually cannot be acted on as a summary",
            premises=("a_truncated_listing_still_states_its_total",),
        ),
    ),
)

_ARMS = (
    an_elif_guarded_assertion_is_found,
    an_early_exit_guarded_assertion_is_found,
    an_accumulating_arm_is_not_guarded,
    a_nested_functions_return_is_not_this_arms_exit,
    a_guarded_site_names_the_line_it_rests_on,
    a_reading_carries_the_arms_it_read,
    a_module_with_no_roster_yields_nothing,
    an_empty_reading_says_so,
    the_render_states_what_it_is_not_claiming,
    a_truncated_listing_still_states_its_total,
    a_lifted_limit_spells_every_row,
)

_CASE_COUNT = FAMILY.count


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"guarded-assert selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"guarded-assert selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
