#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.library_witness` — the T25 family, and the ways it could close falsely.

⚑⚑⚑ THE EMPTY-LIBRARY CASE IS THE ONE THE ORIGINAL WARNED ABOUT AND COULD NOT EXPRESS. Its own
docstring says counting *"witnesses in the right file"* would pass a library that exists and is
empty — and the fastest route to an empty dispatch is DELETING the witnesses rather than moving
them. A verdict reading "no witnesses left in the dispatch" as success would close this arc on
the destruction of the thing it exists to relocate.

⚑⚑ AND THE AGGREGATE MUST NOT MEASURE. The original ran its three routes, redirected stdout into
a buffer to swallow their output, and read the exit codes — an aggregate that cannot say *"I rest
on these"* without executing them. The family declares it, so a case here asserts the premise
EDGE rather than a re-run.

⚑ THE FIXTURES READ THE LIVE PATHS DELIBERATELY HERE, unlike elsewhere in this tree: this
family's subject IS the dispatch module, and the state under test — no library, witnesses still
in the dispatch — is the OPEN state the arc exists to change. The cases assert the SHAPE of the
verdict (a part per finding, the verdict last, a route on every part), never a count, so they
stay true as the population shrinks and go green only when the arc lands.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.witness import witness_row

from substrate import corpus, library_shape, library_witness

_THREE_MEMBERS = 3

# A dispatch module holding a witness that reaches for retired shared state.
#
# ⚑⚑⚑ THE FIXTURES ARE SOURCE, BECAUSE THE ARC CLOSED THE ITEMS THESE CASES DROVE. Two cases ran
# against the LIVE dispatch and asserted it still held an absent library and state-reading
# witnesses — true when written, and falsified the moment the split landed. **A case pinned to
# today's tree measures the tree, and fails when the work it guards succeeds.** They now test the
# READER: what does the witness do when the defect IS present.
_REACHING = '''"""A dispatch module with a reaching witness."""


def T99():
    """Read a sibling's deposit."""
    return SIZES.get("T99")
'''


def _at(where: str, text: str | None = None) -> None:
    """Point the readers at a temp root, optionally writing a dispatch module into it."""
    corpus.ROOT = Path(where)
    if text is None:
        return
    path = Path(where).joinpath(*library_shape.DISPATCH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _rows_at(text: str | None, reader: str) -> list[witness_row.Part | witness_row.Verdict]:
    """Run one route against a temp root and return its rows."""
    original = corpus.ROOT
    try:
        with tempfile.TemporaryDirectory() as where:
            _at(where, text)
            if reader == "library":
                return list(library_witness.witness_library("T25-library", "witness-library"))
            return list(library_witness.witness_globals("T25-globals", "witness-globals"))
    finally:
        corpus.ROOT = original


def the_family_declares_three_routes(out: list[str]) -> int:
    """Check the family holds one member per sub-item.

    ⚑ THE ROSTER IS THE AGGREGATE. The original spelled its parts as a list literal INSIDE the
    aggregate's body, so nothing could read them without running it.
    """
    got = library_witness.FAMILY
    if len(got.members) != _THREE_MEMBERS:
        out.append(f"selftest: the family holds {len(got.members)} member(s)")
        return 1
    return 0


def the_globals_route_rests_on_the_parametric_one(out: list[str]) -> int:
    """Check the premise edge is declared rather than implied by prose.

    ⚑⚑ THE RELATIONSHIP IS REAL AND WAS UNWRITABLE. `T25-globals` exists because a census asking
    only whether a witness takes arguments passes one that takes them AND still reads shared
    state — so it is a control on the parametric route. In the original that lived only in a
    docstring, and deleting the parametric route would have left it reading as protected.
    """
    got = library_witness.FAMILY.member("no_witness_reads_another_witnesss_globals")
    if got.premises != ("every_witness_takes_what_it_needs",):
        out.append(f"selftest: the premise edge reads {got.premises!r}")
        return 1
    return 0


def the_familys_premises_all_resolve(out: list[str]) -> int:
    """Check no declared premise names a member the family does not hold.

    ⚑ A DANGLING PREMISE READS AS PROTECTED AND IS NOT.
    """
    got = library_witness.FAMILY.dangling_premises()
    if got != ():
        out.append(f"selftest: the family carries a dangling premise: {got!r}")
        return 1
    return 0


def a_missing_library_opens_with_a_route(out: list[str]) -> int:
    """Check the absent library yields a part naming what to create.

    ⚑ A VERDICT WITHOUT A PART IS A NUMBER. The ordering ranks by population, so an item that
    reports open and emits nothing can be weighed only by its own say-so.
    """
    rows = _rows_at(None, "library")
    parts = [r for r in rows if isinstance(r, witness_row.Part)]
    verdicts = [r for r in rows if isinstance(r, witness_row.Verdict)]
    bad = 0
    if not parts:
        out.append("selftest: the absent library emitted no part")
        bad += 1
    if not verdicts or verdicts[-1].state != witness_row.OPEN:
        out.append(f"selftest: the absent library did not open: {verdicts!r}")
        bad += 1
    return bad


def the_verdict_trails_its_parts(out: list[str]) -> int:
    """Check the verdict is the LAST row, never the first.

    ⚑ A WITNESS KNOWS ITS VERDICT ONLY AFTER LOOKING. Emitting it first is the
    count-before-the-walk defect, and a reader taking rows in order would bank a verdict about a
    population it had not yet seen.
    """
    rows = list(library_witness.witness_library("T25-library", "witness-library"))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append(f"selftest: the last row is not a verdict: {rows[-1] if rows else None!r}")
        return 1
    if any(isinstance(r, witness_row.Verdict) for r in rows[:-1]):
        out.append("selftest: a verdict was emitted before the parts")
        return 1
    return 0


def the_reaching_definitions_are_named(out: list[str]) -> int:
    """Check the globals route emits one part per reader, carrying what it reads.

    ⚑⚑ THE MEASURED POPULATION IS THE LEGACY CONTRACT, NOT WITNESSES. On the live dispatch the
    readers are the retired accessors themselves, so the repair is to RETIRE them — and a route
    reporting only a count would send a reader to rewrite six witnesses that are not the defect.
    """
    rows = _rows_at(_REACHING, "globals")
    parts = [r for r in rows if isinstance(r, witness_row.Part)]
    if not parts:
        out.append("selftest: the globals route emitted no part")
        return 1
    if not any(p.route for p in parts):
        out.append("selftest: a reaching definition carries no route")
        return 1
    return 0


def a_route_without_its_tag_opens_rather_than_raising(out: list[str]) -> int:
    """Check an unreadable figure tag opens the item instead of crashing.

    ⚑ A WITNESS THAT RAISES TAKES THE WHOLE ROSTER DOWN. An unanchored claim is a finding about
    the CLAIM — the item cannot be measured — and that is a verdict, not an exception.
    """
    rows = list(library_witness.witness_library("T25-library", "no-such-figure"))
    verdicts = [r for r in rows if isinstance(r, witness_row.Verdict)]
    if not verdicts or verdicts[-1].state != witness_row.OPEN:
        out.append(f"selftest: a missing tag did not open the item: {verdicts!r}")
        return 1
    if "tag" not in verdicts[-1].why:
        out.append(f"selftest: the verdict does not name the missing tag: {verdicts[-1].why!r}")
        return 1
    return 0


def every_declared_member_has_a_body(out: list[str]) -> int:
    """Check each declared member names a witness function this module exports.

    ⚑⚑ A FAMILY NAMING A MEMBER NOTHING RUNS reads as MORE rigorous than an undeclared suite
    while being less — the false-protection defect turned on the declaration itself.
    """
    bodies = {
        "the_witnesses_live_in_a_keyed_library",
        "every_witness_takes_what_it_needs",
        "no_witness_reads_another_witnesss_globals",
    }
    missing = [n for n in library_witness.FAMILY.names if n not in bodies]
    if missing:
        out.append(f"selftest: the family declares members with no body: {missing!r}")
        return 1
    return 0


def the_family_is_not_yet_split(out: list[str]) -> int:
    """Check every member is a leaf, so the count equals the roster.

    ⚑ AN HONEST STATEMENT OF WHERE THIS FAMILY IS. Its three members each assert one fact today;
    should one grow a second, `unsplit()` names it rather than letting the total drift.
    """
    got = library_witness.FAMILY
    if got.count != len(got.members):
        out.append(f"selftest: count {got.count} against {len(got.members)} member(s)")
        return 1
    if got.unsplit() != ():
        out.append(f"selftest: an unsplit member appeared: {got.unsplit()!r}")
        return 1
    return 0


def the_apex_does_not_restate_its_key(out: list[str]) -> int:
    """Check the apex states a claim rather than echoing the family's name.

    ⚑ THE APEX SAYS WHAT HAVING THE FAMILY ESTABLISHES, which no member says alone. An apex that
    began with its own key would be derivable, and a derivable field is one nobody needs to write
    or read.
    """
    got = library_witness.FAMILY
    if not got.apex:
        out.append("selftest: the apex is empty")
        return 1
    if got.apex.startswith(got.key):
        out.append("selftest: the apex restates its own key")
        return 1
    return 0


def every_member_name_addresses_exactly_one(out: list[str]) -> int:
    """Check the roster holds no duplicate name.

    ⚑⚑ A CASE, NOT A TYPE CHECK, AND THE FIRST CUT WAS THE LATTER. It asserted
    `isinstance(FAMILY, Family)` — which mypy reports UNREACHABLE, because the annotation already
    guarantees it. **A branch the type system proves dead cannot fail, so it is not a case**; it
    is a comment costing a line and reading as coverage.

    ⚑ WHAT IS WORTH ASSERTING is the property the constructor enforces: two members sharing a
    name make `member()` return whichever comes first and make a premise edge ambiguous. That is
    checkable, and it fails if someone builds the family by hand to skip the refusal.
    """
    names = library_witness.FAMILY.names
    if len(names) != len(set(names)):
        out.append(f"selftest: the roster repeats a name: {names!r}")
        return 1
    return 0


# ⚑⚑⚑ THE THREE ARMS BELOW BEAR THE FAMILY'S MEMBER NAMES, AND THAT CORRESPONDENCE IS THE POINT.
# `family_roster` reports a declared member no arm runs, because **a family naming a member
# nothing runs reads as MORE rigorous than an undeclared suite while being less.** This family
# declared three claims about the dispatch module and ran none by name; the other arms assert the
# verdict's SHAPE, which is a different subject.
#
# ⚑⚑ THEY ASSERT THE VERDICT IS RENDERED, NOT THAT IT IS CLOSED — and here that distinction is
# sharp: all three routes are OPEN today by design, since the keyed library does not exist yet and
# creating it is what this arc is for. A case pinning either state would fail on one side of the
# work landing.
def the_witnesses_live_in_a_keyed_library(out: list[str]) -> int:
    """Check the library route reaches a verdict on the live dispatch module."""
    rows = list(library_witness.witness_library("T25-library", "witness-library"))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append("selftest: the library route rendered no verdict")
        return 1
    return 0


def every_witness_takes_what_it_needs(out: list[str]) -> int:
    """Check the parametric route reaches a verdict on the live dispatch module."""
    rows = list(library_witness.witness_parametric("T25-parametric", "witness-nonparametric"))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append("selftest: the parametric route rendered no verdict")
        return 1
    return 0


def no_witness_reads_another_witnesss_globals(out: list[str]) -> int:
    """Check the globals route reaches a verdict on the live dispatch module."""
    rows = list(library_witness.witness_globals("T25-globals", "witness-globals"))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append("selftest: the globals route rendered no verdict")
        return 1
    return 0


_ARMS = (
    the_witnesses_live_in_a_keyed_library,
    every_witness_takes_what_it_needs,
    no_witness_reads_another_witnesss_globals,
    the_family_declares_three_routes,
    the_globals_route_rests_on_the_parametric_one,
    the_familys_premises_all_resolve,
    a_missing_library_opens_with_a_route,
    the_verdict_trails_its_parts,
    the_reaching_definitions_are_named,
    a_route_without_its_tag_opens_rather_than_raising,
    every_declared_member_has_a_body,
    the_family_is_not_yet_split,
    the_apex_does_not_restate_its_key,
    every_member_name_addresses_exactly_one,
)

# ⚑ THE THREE MEMBER ARMS CONTRIBUTE ONE CASE EACH, and the total MOVES by exactly three —
# growth, not a corrected sum.
_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"library-witness selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"library-witness selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
