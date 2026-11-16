#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.family_roster` — the corpus-wide reading of the declared families.

⚑⚑⚑ THE FIXTURES ARE WRITTEN HERE, NOT READ FROM THE LIVE CORPUS. Measured at the time of
writing: every declared family is readable, no premise dangles, and nothing is declared-but-unrun.
A case built on the live tree could therefore not fail — it would pin today's content and go green
the moment someone edited a module for unrelated reasons, which is the shape
`edge_witness_selftest` records for the same reason.

⚑⚑ AND EVERY POSITIVE PREDICATE HERE CARRIES ITS CONTROL. A roster reporting "no dangling
premise", "no unrun member", "no unreadable declaration" over a corpus it failed to DISCOVER
reports three zeros and looks perfect — the census-green-is-a-fact-about-the-census shape, which
is exactly the defect this module was built to remove one level up. So each clean fixture is
paired with a dirty one that must produce the finding.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import family_roster

# A module declaring a readable family: three members, one with a resolving premise, one unsplit.
_DECLARER = '''"""A fixture module."""
from substrate import witness_family

FAMILY = witness_family.of(
    key="FIX",
    apex="an apex claim",
    subject="the fixture subject",
    members=[
        witness_family.Member(
            name="the_first_thing_holds",
            claim="the first claim",
            cases=3),
        witness_family.Member(
            name="the_second_thing_holds",
            claim="the second claim",
            premises=("the_first_thing_holds",)),
    ])
'''

# Its suite, running exactly the two declared members as arms.
_SUITE = '''"""A fixture suite."""


def the_first_thing_holds(out: list[str]) -> int:
    """Hold."""
    del out
    return 0


def the_second_thing_holds(out: list[str]) -> int:
    """Hold."""
    del out
    return 0


_ARMS = (the_first_thing_holds, the_second_thing_holds)
'''

# The same suite with one arm renamed away — the declared member is now run by nothing.
_SUITE_RENAMED = '''"""A fixture suite whose second arm was renamed."""


def the_first_thing_holds(out: list[str]) -> int:
    """Hold."""
    del out
    return 0


def the_second_thing_was_renamed(out: list[str]) -> int:
    """Hold."""
    del out
    return 0


_ARMS = (the_first_thing_holds, the_second_thing_was_renamed)
'''

# A family naming a premise no member of it holds.
_DANGLES = '''"""A fixture with a dangling premise."""
from substrate import witness_family

FAMILY = witness_family.of(
    key="DANGLE",
    apex="an apex claim",
    subject="the fixture subject",
    members=[
        witness_family.Member(
            name="the_only_member",
            claim="a claim",
            premises=("a_control_that_was_deleted",)),
    ])
'''

# A family whose roster is COMPUTED — the reader has no evaluation of it.
_COMPUTED = '''"""A fixture whose roster is built rather than written."""
from substrate import witness_family

NAMES = ("a", "b")

FAMILY = witness_family.of(
    key="COMPUTED",
    apex="an apex claim",
    subject="the fixture subject",
    members=[witness_family.Member(name=n, claim="a claim") for n in NAMES])
'''

# A family counting its cases off its own fixture lists — the shape two live declarations use.
_FIXTURE_LEN = '''"""A fixture whose cases track its data."""
from substrate import witness_family

KEEP = ("a", "b", "c")
DROP = ("d", "e")

FAMILY = witness_family.of(
    key="LEN",
    apex="an apex claim",
    subject="the fixture subject",
    members=[
        witness_family.Member(
            name="the_summed_thing_holds",
            claim="a claim",
            cases=len(KEEP) + len(DROP)),
        witness_family.Member(
            name="the_single_thing_holds",
            claim="a claim",
            cases=len(DROP)),
    ])
'''

# The same shape over a name bound TWICE — two lengths, so no reading.
_REBOUND = '''"""A fixture whose fixture list is rebound."""
from substrate import witness_family

ROWS = ("a", "b", "c")
ROWS = ("a",)

FAMILY = witness_family.of(
    key="REBOUND",
    apex="an apex claim",
    subject="the fixture subject",
    members=[
        witness_family.Member(name="the_thing_holds", claim="a claim", cases=len(ROWS)),
    ])
'''

# A `cases=` one step outside the grammar: `len()` of a name bound to a call, not to a display.
_UNRESOLVED = '''"""A fixture whose fixture list is computed."""
from substrate import witness_family

ROWS = sorted(("a", "b"))

FAMILY = witness_family.of(
    key="UNRESOLVED",
    apex="an apex claim",
    subject="the fixture subject",
    members=[
        witness_family.Member(name="the_thing_holds", claim="a claim", cases=len(ROWS)),
    ])
'''

# A module that declares nothing.
_PLAIN = '''"""A fixture that declares no family."""

VALUE = 1
'''

_FIXTURE_MEMBERS = 2
_FIXTURE_CASES = 4

# What `_FIXTURE_LEN` must derive: (3 + 2) + 2 over its two fixture lists.
_LEN_CASES = 7


def _tree(where: str, files: dict[str, str]) -> Path:
    """Write a fixture `substrate/` package under `where` and return the root."""
    root = Path(where)
    (root / "substrate").mkdir()
    for name, text in files.items():
        (root / "substrate" / name).write_text(text, encoding="utf-8")
    return root


def a_declared_family_is_discovered_without_importing_it(out: list[str]) -> int:
    """Check a module's `FAMILY` is read from source, with its members and derived count.

    ⚑⚑⚑ THE WHOLE MODULE RESTS ON THIS. Discovery by IMPORT would fire whatever a candidate
    module executes at module scope — and a roster is the reader that must touch every file, so
    it would fire the most. Asserting the values come back CORRECT from a parse is what says the
    `ast` route is a real reading rather than a safer way to learn less.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(_tree(where, {"fix.py": _DECLARER}))
    if len(rows) != 1 or rows[0].family is None:
        out.append(f"selftest: the declaration was not read: {rows!r}")
        return 1
    bad = 0
    if rows[0].family.key != "FIX":
        out.append(f"selftest: the family key is {rows[0].family.key!r}")
        bad += 1
    if len(rows[0].family.members) != _FIXTURE_MEMBERS:
        out.append(f"selftest: the roster is {rows[0].family.names!r}")
        bad += 1
    if rows[0].family.count != _FIXTURE_CASES:
        out.append(f"selftest: the derived count is {rows[0].family.count}, want {_FIXTURE_CASES}")
        bad += 1
    return bad


def a_module_declaring_no_family_is_not_a_row(out: list[str]) -> int:
    """Check the census counts declarers, not files — the POSITIVE CONTROL on the denominator.

    ⚑ WITHOUT THIS, A READER THAT RETURNED A ROW PER FILE would pass the case above and report a
    corpus-wide total inflated by every module in the package. The denominator is the half of a
    census that is never checked, and an inflated one makes every derived figure wrong quietly.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(_tree(where, {"fix.py": _DECLARER, "plain.py": _PLAIN}))
    if len(rows) != 1:
        out.append(f"selftest: a module declaring no family became a row: {rows!r}")
        return 1
    return 0


def a_computed_roster_is_reported_unreadable_not_dropped(out: list[str]) -> int:
    """Check a family this reader cannot evaluate is a row carrying its reason.

    ⚑⚑ DROPPING IT WOULD LET A FAMILY LEAVE THE CENSUS BY BECOMING CLEVERER, and the census would
    report itself getting cleaner while its coverage shrank. `case_count` records the same rule
    for its literal-sum parse: unreadable is UNREADABLE, never zero.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(_tree(where, {"fix.py": _COMPUTED}))
    if len(rows) != 1:
        out.append(f"selftest: the computed declaration is not a row: {rows!r}")
        return 1
    if rows[0].readable or not rows[0].reason:
        out.append(f"selftest: the computed declaration read as {rows[0]!r}")
        return 1
    return 0


def an_unreadable_declaration_is_outside_the_totals(out: list[str]) -> int:
    """Check the totals count only what was evaluated.

    ⚑ A TOTAL THAT COUNTED AN UNEVALUABLE DECLARATION AS ZERO CASES would fold a gap into the
    denominator as if it were a measurement, and the family count would agree with the file count
    while the case count silently under-reported.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(_tree(where, {"a.py": _DECLARER, "b.py": _COMPUTED}))
    families, members, cases = family_roster.totals(rows)
    if (families, members, cases) != (1, _FIXTURE_MEMBERS, _FIXTURE_CASES):
        out.append(f"selftest: totals are {(families, members, cases)!r} over {len(rows)} row(s)")
        return 1
    return 0


def a_dangling_premise_is_reported_corpus_wide(out: list[str]) -> int:
    """Check a premise naming no member of its own family is named, with its file.

    ⚑⚑ THIS IS `Family.dangling_premises()` WITH A DENOMINATOR. A positive control declared as a
    premise and then deleted leaves the protected member reading as protected; the per-family
    reader could only find that in a file someone already opened.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(_tree(where, {"fix.py": _DANGLES}))
    got = family_roster.dangling(rows)
    if len(got) != 1 or got[0].premise != "a_control_that_was_deleted":
        out.append(f"selftest: the dangling premise was not reported: {got!r}")
        return 1
    if got[0].path != "fix.py":
        out.append(f"selftest: the finding names file {got[0].path!r}")
        return 1
    return 0


def a_resolving_premise_is_not_reported(out: list[str]) -> int:
    """Check a premise that names a real member is silent — the POSITIVE CONTROL.

    ⚑ WITHOUT THIS, A READER THAT FLAGGED EVERY PREMISE would pass the case above. The pair says
    the corpus-wide reader discriminates rather than reporting every edge as broken.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(_tree(where, {"fix.py": _DECLARER}))
    got = family_roster.dangling(rows)
    if got != ():
        out.append(f"selftest: a resolving premise was reported dangling: {got!r}")
        return 1
    return 0


def an_unsplit_member_is_listed_as_work(out: list[str]) -> int:
    """Check a member with several cases and no sub-family is on the split work list.

    ⚑ A CENSUS, NOT A DEFECT — which is why it must carry the COUNT. A row saying only that a
    member is unsplit tells a reader nothing about whether the facts under it deserve names.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(_tree(where, {"fix.py": _DECLARER}))
    got = family_roster.unsplit(rows)
    want_cases = 3
    if len(got) != 1 or got[0].member != "the_first_thing_holds":
        out.append(f"selftest: the unsplit member was not listed: {got!r}")
        return 1
    if got[0].cases != want_cases:
        out.append(f"selftest: the unsplit member reports {got[0].cases} case(s)")
        return 1
    return 0


def a_member_no_arm_runs_is_reported(out: list[str]) -> int:
    """Check a declared member the owning suite does not dispatch is named.

    ⚑⚑⚑ THE ROSTER'S WHOLE POINT. A family naming a member nothing runs reads as MORE rigorous
    than an undeclared suite while being less — and the per-suite arm that checks this can only
    ever cover a family whose author already thought to write it, which is the population that
    needs the check least.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(
            _tree(where, {"fix.py": _DECLARER, "fix_selftest.py": _SUITE_RENAMED})
        )
        got = family_roster.unrun(rows, Path(where))
    if len(got) != 1 or got[0].member != "the_second_thing_holds":
        out.append(f"selftest: the unrun member was not reported: {got!r}")
        return 1
    return 0


def a_member_every_arm_runs_is_not_reported(out: list[str]) -> int:
    """Check a family whose members are all dispatched reports nothing — the POSITIVE CONTROL.

    ⚑ WITHOUT THIS, A READER THAT REPORTED EVERY MEMBER AS UNRUN would pass the case above and
    make the roster's loudest finding unconditional — which trains a reader to ignore it, the one
    outcome worse than not checking.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(_tree(where, {"fix.py": _DECLARER, "fix_selftest.py": _SUITE}))
        got = family_roster.unrun(rows, Path(where))
    if got != ():
        out.append(f"selftest: a dispatched member was reported unrun: {got!r}")
        return 1
    return 0


def a_family_with_no_readable_suite_is_not_reported_unrun(out: list[str]) -> int:
    """Check a missing suite yields NO READING, never an empty arm set.

    ⚑⚑ NO READING AND NO ARMS ARE OPPOSITE, and collapsing them declares EVERY member of that
    family unrun — a loud false positive about a file the reader never found. The report-presence
    rule turned on the roster: an absent suite is a fact about the discovery, not about the family.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(_tree(where, {"fix.py": _DECLARER}))
        got = family_roster.unrun(rows, Path(where))
    if got != ():
        out.append(f"selftest: a family with no suite reported unrun members: {got!r}")
        return 1
    return 0


def an_empty_corpus_says_so_rather_than_rendering_clean(out: list[str]) -> int:
    """Check a corpus declaring no family renders as such, not as a green zero.

    ⚑⚑ `0 famil(ies), 0 member(s), 0 case(s)` READS AS A CLEAN SWEEP of a population that was
    never found — the exact false-zero shape this module exists to remove. It has to name the
    absence instead.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(_tree(where, {"plain.py": _PLAIN}))
    text = family_roster.render(rows, Path(where))
    if "no module declares" not in text:
        out.append(f"selftest: an empty corpus rendered as {text!r}")
        return 1
    return 0


def the_live_corpus_declares_at_least_one_family(out: list[str]) -> int:
    """Check the reader finds families in the real tree — the POSITIVE CONTROL on discovery.

    ⚑⚑⚑ EVERY OTHER CASE HERE RUNS ON A FIXTURE TREE, so all of them would still pass if the walk
    over the LIVE corpus found nothing: the roster would report three empty defect lists and a
    zero denominator, and read as a clean corpus. This is the one case that fails if discovery is
    pointed at the wrong place — and it asserts only NON-EMPTINESS, never a count, because a count
    pins today's tree and goes red on an unrelated edit.
    """
    families, _members, _cases = family_roster.totals(family_roster.census())
    if not families:
        out.append("selftest: the live corpus reported no declared family — discovery is blind")
        return 1
    return 0


def a_cases_counted_off_a_fixture_list_is_read(out: list[str]) -> int:
    """Check `cases=len(FIXTURE)` and sums of them evaluate to the fixture's real size.

    ⚑⚑⚑ THE WIDENING'S WHOLE JUSTIFICATION, AND IT IS ABOUT WHICH SHAPE THE CENSUS REWARDS. A
    count written `len(_DROP)` TRACKS its data — add a path and the member's count grows with the
    assertions the arm makes — while a literal `9` under-reports from the moment the fixture moves.
    Refusing to read the tracking form would push declarations toward the drifting one to stay in
    the census, which inverts what the census is for.

    ⚑ IT ASSERTS THE VALUE, NOT MERELY THAT IT READ. A reader that returned any integer would make
    this row readable while putting a wrong count into the corpus total — the readable-but-wrong
    direction, which is worse than the refusal it replaced.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(_tree(where, {"fix.py": _FIXTURE_LEN}))
    if len(rows) != 1 or rows[0].family is None:
        out.append(f"selftest: the len()-counted declaration did not read: {rows!r}")
        return 1
    if rows[0].family.count != _LEN_CASES:
        out.append(
            f"selftest: the len()-counted family derives {rows[0].family.count} case(s), "
            f"want {_LEN_CASES}"
        )
        return 1
    return 0


def a_cases_over_a_rebound_name_is_refused(out: list[str]) -> int:
    """Check a fixture list bound twice makes its `len()` UNREADABLE rather than picking one.

    ⚑⚑ TWO BINDINGS ARE TWO LENGTHS AND NO READING. Taking the first would report a count off a
    fixture the declaration does not use — a WRONG number wearing a readable shape, which no
    downstream reader can tell from a right one. This is the boundary case that says the evaluator
    refuses where it cannot decide, rather than where it happens not to have a branch.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(_tree(where, {"fix.py": _REBOUND}))
    if len(rows) != 1:
        out.append(f"selftest: the rebound declaration is not a row: {rows!r}")
        return 1
    if rows[0].readable:
        out.append(f"selftest: a rebound fixture list was read anyway: {rows[0]!r}")
        return 1
    return 0


def a_cases_over_a_computed_name_is_refused(out: list[str]) -> int:
    """Check `len()` of a name bound to a CALL is unreadable — the stated floor, one step out.

    ⚑⚑ THIS IS WHERE THE EVALUATOR STOPS, AND THE STOP HAS TO BE CASED OR IT IS A PREFERENCE. The
    admitted grammar is literal / `len(<literal display>)` / `+`; `sorted(...)` needs EXECUTION to
    have a length, and a reader that started running expressions to find out would be a second
    Python, wrong somewhere no case looks. Without this arm, nothing distinguishes a bounded reader
    from one that has merely not met the input that breaks it.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = family_roster.census(_tree(where, {"fix.py": _UNRESOLVED}))
    if len(rows) != 1:
        out.append(f"selftest: the computed-fixture declaration is not a row: {rows!r}")
        return 1
    if rows[0].readable:
        out.append(f"selftest: a computed fixture list was read anyway: {rows[0]!r}")
        return 1
    return 0


_ARMS = (
    a_declared_family_is_discovered_without_importing_it,
    a_module_declaring_no_family_is_not_a_row,
    a_computed_roster_is_reported_unreadable_not_dropped,
    an_unreadable_declaration_is_outside_the_totals,
    a_dangling_premise_is_reported_corpus_wide,
    a_resolving_premise_is_not_reported,
    an_unsplit_member_is_listed_as_work,
    a_member_no_arm_runs_is_reported,
    a_member_every_arm_runs_is_not_reported,
    a_family_with_no_readable_suite_is_not_reported_unrun,
    an_empty_corpus_says_so_rather_than_rendering_clean,
    the_live_corpus_declares_at_least_one_family,
    a_cases_counted_off_a_fixture_list_is_read,
    a_cases_over_a_rebound_name_is_refused,
    a_cases_over_a_computed_name_is_refused,
)

# ⚑ HAND-SUMMED, AND DELIBERATELY SO. `witness_family.Family.count` derives a total from a
# DECLARED roster; this suite declares no family of its own, and inventing one to satisfy a count
# is the shape ⟡family-count-adoption forbids outright. The three arms with a second assertion are
# spelled out rather than folded.
#
# ⚑⚑ THE THREE ARMS ADDED FOR THE `len(FIXTURE)` GRAMMAR ARE 2 + 2 + 2 — each reads a row and then
# asserts what the row SAYS. Reading and verdict are one claim through two comparisons over the
# same subject, neither guarding the other, so they are counted and left fused.
_CASE_COUNT = 3 + 1 + 1 + 1 + 2 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 2 + 2 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"family-roster selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"family-roster selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
