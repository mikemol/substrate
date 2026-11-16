#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the relation classifier, and pin its REACH as a first-class fact.

⚑⚑⚑ THE LOAD-BEARING CASES ARE THE THREE MEASURED ARMS (gate-G36). This module exists because a
mechanical split of the multi-claim arms would destroy content, and the evidence was three arms of
`module_trim_selftest.py`. Two of them are read here against the LIVE suite rather than a fixture,
because a fixture would only prove the classifier agrees with my transcription of the arms — and
my reading of those arms is the claim under test.

⚑⚑ AND THE UNDECIDED REACH IS ASSERTED, NOT FOOTNOTED. The live census classifies a small minority
and reports the rest UNDECIDED. That is honest and it is also the property most likely to rot: a
later widening that silently classified the unread arms as INDEPENDENT would license exactly the
destructive split this reader exists to prevent. So the suite asserts that unread arms are never
called independent, in both directions.

⚑ THE NEGATIVE CONTROL IS AN ARM WHOSE CLAIMS PROBE DIFFERENT PREDICATES. Without it a classifier
hard-wired to "relation" satisfies every positive row here and would freeze the whole paydown.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from substrate import relation_arm

ROOT = Path(__file__).resolve().parent.parent

Case = tuple[str, bool]

_RELATION = """
def an_arm(out):
    if not conserved(a, b):
        out.append("first")
        return 1
    if conserved(c, d):
        out.append("second")
        return 1
    return 0
"""

_INDEPENDENT = """
def an_arm(out):
    if not parses(a):
        out.append("first")
        return 1
    if renders(b):
        out.append("second")
        return 1
    return 0
"""

_INLINE = """
def an_arm(out):
    if a != b:
        out.append("first")
        return 1
    if c != d:
        out.append("second")
        return 1
    return 0
"""

_PLUMBING = """
def an_arm(out):
    if not probe.is_file():
        return 1
    if not conserved(a, b):
        out.append("first")
        return 1
    if conserved(c, d):
        out.append("second")
        return 1
    return 0
"""

# ⚑ THE DOMINANT UNDECIDED SHAPE, transcribed from `assert_census_selftest`: assign from a
# shared predicate, then compare the local. The guard's test is a bare Name, so a reader that
# stopped at the comparison could not see the predicate one line up.
_ASSIGNED = """
def an_arm(out):
    got = _kinds("m.py", FIRST)
    if got != [LOAD]:
        out.append("first")
        bad += 1
    got = _kinds("m.py", SECOND)
    if got != [ARM]:
        out.append("second")
        bad += 1
    return bad
"""

# The same shape where the two locals come from DIFFERENT predicates — independent, not related.
_ASSIGNED_DIFFERENT = """
def an_arm(out):
    parsed = parses("m.py")
    if not parsed:
        out.append("first")
        bad += 1
    rendered = renders("m.py")
    if not rendered:
        out.append("second")
        bad += 1
    return bad
"""

# ⚑ CONSTRUCT-THEN-READ-ATTRIBUTE: a record built twice, one field probed each time. The
# populated and degenerate instances are one law at two points, which is the relation form.
_ATTRIBUTE = """
def an_arm(out):
    got = Bucket(kind="as", keys=("a",), providers=1)
    if got.n != len(got.keys):
        out.append("first")
        bad += 1
    empty = Bucket(kind="hiding", keys=(), providers=0)
    if empty.n:
        out.append("second")
        bad += 1
    return bad
"""

# The same construction where the two guards read DIFFERENT fields — two questions, not one law.
_ATTRIBUTE_DIFFERENT = """
def an_arm(out):
    got = Bucket(kind="as", keys=("a",), providers=1)
    if got.n:
        out.append("first")
        bad += 1
    if got.shape:
        out.append("second")
        bad += 1
    return bad
"""

# ⚑ A BOOLOP GUARD IS THE MEASURED BOUNDARY. `a not in x.f or b not in x.f` is a real relation
# arm this reader CANNOT decide, and it must say so rather than guess — undecided withholds a
# split, independent licenses one, so the unread case has to land on the withholding side.
_BOOLOP = """
def an_arm(out):
    got = Bucket(kind="as", keys=("a",), providers=35)
    if "x" not in got.shape or "y" not in got.shape:
        out.append("first")
        bad += 1
    blind = Bucket(kind="as", keys=("a",), providers=0)
    if blind.shape:
        out.append("second")
        bad += 1
    return bad
"""

# ⚑ THE DISAGREEING BOOLOP — the refusal case for the widening above. Two operands naming two
# predicates are two questions joined by an operator, not one property of one probe.
_BOOLOP_MIXED = """
def an_arm(out):
    got = Bucket(kind="as", keys=("a",), providers=35)
    if "x" not in got.shape or "y" not in got.n:
        out.append("first")
        bad += 1
    blind = Bucket(kind="as", keys=("a",), providers=0)
    if blind.shape:
        out.append("second")
        bad += 1
    return bad
"""

# ⚑ TWO GUARDS SHARING A BUILTIN ARE NOT RELATED. `len(a)` and `len(b)` over different objects
# record the same wrapper name, which fuses unrelated guards in the FREEZING direction.
_BUILTIN_WRAPPED = """
def an_arm(out):
    left = parses("m.py")
    right = renders("m.py")
    if len(left) != 3:
        out.append("first")
        bad += 1
    if len(right) != 4:
        out.append("second")
        bad += 1
    return bad
"""

# ⚑ AN `except ... as` BINDS THE EXCEPTION THE CALL UNDER TEST RAISED, so the probe is that call.
# Missing this made the builtin fix REGRESS a verified relation to undecided.
_HANDLER_BOUND = """
def an_arm(out):
    try:
        plan(("sitmap",))
    except ValueError as exc:
        text = str(exc)
        if "sitmap" not in text:
            out.append("first")
            bad += 1
        if SITEMAP not in text:
            out.append("second")
            bad += 1
    return bad
"""

_TWO = 2
_THREE = 3


def _classify(src: str) -> tuple[str, tuple[str, ...]]:
    """Classify a single-function fixture."""
    node = ast.parse(src).body[0]
    if not isinstance(node, ast.FunctionDef):  # pragma: no cover - fixture shape
        msg = "fixture is not a function"
        raise TypeError(msg)
    return relation_arm.classify(node)


def _verdict_cases() -> list[Case]:
    """Return the cases pinning the three verdicts."""
    relation, probes = _classify(_RELATION)
    independent, _ = _classify(_INDEPENDENT)
    inline, _ = _classify(_INLINE)
    return [
        # ⚑ THE MEASURED SHAPE: one predicate, several inputs — a positive and its control.
        ("claims probing ONE predicate are a relation", relation == "relation"),
        ("the probe is named so a reader can audit it", probes == ("conserved", "conserved")),
        # ⚑ THE CONTROL: without this a classifier stuck at "relation" passes every row above
        #   and would freeze the entire paydown as undoable.
        ("claims probing DIFFERENT predicates are independent", independent == "independent"),
        # ⚑ AN UNREADABLE GUARD IS UNDECIDED, NEVER INDEPENDENT — the safe direction, because
        #   independent licenses a split and undecided does not.
        ("an inlined comparison is UNDECIDED", inline == "undecided"),
    ]


def _binding_cases() -> list[Case]:
    """Return the cases pinning that a local bound from a call resolves to its predicate.

    ⚑⚑ THIS IS THE WIDENING, AND THE UNREAD ARMS NAMED IT. `assert_census_selftest`'s arms assign
    `got = _kinds(...)` and then compare the local, twice, over different fixtures — and both
    docstrings say the discriminator IS the pair. Before this, the guard's bare `Name` yielded no
    predicate and the arms read UNDECIDED, so the reader called two self-described relations
    unclassifiable.

    ⚑ THE CONTROL IS THE SAME SHAPE OVER DIFFERENT PREDICATES. Without it, resolving bindings
    could report every assign-then-compare arm as a relation and freeze that whole family as
    unsplittable.
    """
    same, probes = _classify(_ASSIGNED)
    different, _ = _classify(_ASSIGNED_DIFFERENT)
    return [
        ("assign-then-compare on ONE predicate is a relation", same == "relation"),
        ("the shared predicate is named", probes == ("_kinds", "_kinds")),
        # ⚑ REBINDING ONE NAME MUST NOT COLLAPSE TO THE FIRST ASSIGNMENT — both guards here
        #   probe `_kinds`, and reading only the first binding would still say so by accident.
        #   The control below is what makes this row mean something.
        ("assign-then-compare on DIFFERENT predicates is independent", different == "independent"),
    ]


def _attribute_cases() -> list[Case]:
    """Return the cases pinning that an attribute of a bound local names its field.

    ⚑⚑ THE SECOND WIDENING, AND THE ARM NAMED ITSELF AGAIN. `ban_witness_selftest`'s
    `each_bucket_reports_its_own_added_keys` constructs a `Bucket` twice and reads `got.n`, and
    its docstring says the populated and empty buckets are ONE LAW AT TWO POINTS, DELIBERATELY
    LEFT FUSED. Before this it read UNDECIDED.

    ⚑ THE FIELD IS PART OF THE PROBE, NOT NOISE. The same suite reads `got.n` in one arm and
    `got.shape` in another — same constructor, genuinely different questions — so keying on the
    constructor alone would fuse two arms that do not relate. The control asserts exactly that.
    """
    same, probes = _classify(_ATTRIBUTE)
    different, _ = _classify(_ATTRIBUTE_DIFFERENT)
    boolop, mixed = _classify(_BOOLOP)
    return [
        ("construct-then-read one field is a relation", same == "relation"),
        ("the probe names the type AND the field", probes == ("Bucket.n", "Bucket.n")),
        # ⚑ THE CONTROL: two fields of one record are two questions.
        ("two different fields are independent", different == "independent"),
        # ⚑⚑⚑ THIS PAIR WAS PINNED AS A LIMITATION AND THE LIMITATION WAS PAID DOWN, so both
        #   rows went RED when the work landed — which is a tracker case working. A BoolOp whose
        #   operands AGREE on one predicate now resolves to it: `a not in x.f or b not in x.f`
        #   is two membership tests over ONE field, asserting one property of one probe.
        ("an agreeing BoolOp guard resolves", boolop == "relation"),
        ("it names the field both operands probe", mixed[0] == "Bucket.shape"),
        # ⚑ AND A DISAGREEING BOOLOP STILL WITHHOLDS, which is what keeps the widening from
        #   naming a predicate the guard does not single out.
        (
            "a BoolOp over DIFFERENT predicates stays undecided",
            _classify(_BOOLOP_MIXED)[0] == "undecided",
        ),
    ]


def _transparent_cases() -> list[Case]:
    """Return the cases pinning that a wrapper builtin is not a predicate.

    ⚑⚑ MEASURED AS A FALSE POSITIVE IN THE FREEZING DIRECTION. `a_conflict_is_reported_once` and
    `an_unknown_target_is_refused_by_name` both read as relations on `len` and `str` — correct
    verdicts on evidence that would have fused any two guards sharing those builtins. A relation
    reached for a non-load-bearing reason is a coincidence, not a finding.

    ⚑ AND CLOSING THAT HOLE OPENED ANOTHER: resolving `str(exc)` through to `exc` found no
    binding, because `except ... as exc` is not an Assign — so a verified relation REGRESSED to
    undecided. The handler binds the exception the call under test raised, so the probe is that
    call, and both cases are asserted together because the second exists to repair the first.
    """
    wrapped, _ = _classify(_BUILTIN_WRAPPED)
    handler, probes = _classify(_HANDLER_BOUND)
    return [
        ("two guards sharing a builtin are NOT related", wrapped == "independent"),
        ("an except-bound name resolves to the call under test", handler == "relation"),
        ("the probe names that call, not the builtin", probes == ("plan", "plan")),
    ]


def _splittable_cases() -> list[Case]:
    """Return the cases pinning the paydown listing.

    ⚑⚑ THIS MODE IMMEDIATELY REFUTED THE SYMBOL THAT MOTIVATED IT (gate-G42). The census spells
    out only relations, so the population the reader exists to make actionable was the one it
    would not name — and reading the list showed it is dominated by guards over different FIELDS
    OF ONE RESULT, which are relations. A count said the paydown was safe; the enumeration said
    it was not.

    ⚑ THE PROBES RIDE ALONG because they ARE the seam a split would cut on, and here they were
    also the evidence that the cut is wrong.
    """
    made = (
        relation_arm.Arm("a.py", "splitme", 2, "independent", ("one", "two")),
        relation_arm.Arm("a.py", "fused", 2, "relation", ("same", "same")),
        relation_arm.Arm("a.py", "unread", 2, "undecided", ()),
    )
    out = relation_arm.render_splittable(made)
    none = relation_arm.render_splittable(
        (relation_arm.Arm("a.py", "fused", 2, "relation", ("same", "same")),)
    )
    return [
        ("the splittable arm is listed", "splitme" in out),
        # ⚑ NEITHER OTHER VERDICT MAY APPEAR — a relation in this list is a licensed destruction.
        ("a relation is NOT listed as splittable", "fused" not in out),
        ("an undecided arm is NOT listed as splittable", "unread" not in out),
        ("the probes are carried, since they are the seam", "one two" in out),
        # ⚑ AN EMPTY LIST IS A FACT ABOUT THE READER, never a clean tree.
        ("no splittable arms says so about the READER", "READER" in none),
    ]


def _named_cases() -> list[Case]:
    """Return the cases pinning the per-arm lookup.

    ⚑ THIS MODE EXISTS BECAUSE AUDITING A WIDENING NEEDED IT AND THE TOOL COULD NOT ANSWER. The
    census prints a truncated sample, so after a widening moved the counts there was no way to
    ask what verdict ONE arm received — and the reflex was a shell pipe over the output, which
    the standing rule refuses. A reader reporting only aggregates cannot be audited against a case.
    """
    made = (
        relation_arm.Arm("a.py", "the_wanted_arm", 2, "relation", ("same", "same")),
        relation_arm.Arm("a.py", "another", 2, "independent", ("one", "two")),
    )
    hit = relation_arm.named(made, "wanted")
    miss = relation_arm.named(made, "no_such_arm")
    return [
        (
            "a matching arm is reported with its verdict",
            "the_wanted_arm" in hit and "relation" in hit,
        ),
        ("a non-matching arm is not reported", "another" not in hit),
        # ⚑ AN EMPTY RESULT IS A FACT ABOUT THE SPELLING, never about the tree.
        ("a miss names the SPELLING", "SPELLING" in miss),
    ]


def _plumbing_cases() -> list[Case]:
    """Return the cases pinning that claimless guards do not vote."""
    verdict, probes = _classify(_PLUMBING)
    return [
        # ⚑ A FIXTURE CHECK APPENDS NOTHING, so it must not decide whether the real claims relate.
        ("a claimless guard is not counted as a probe", len(probes) == _TWO),
        ("the arm is still read as a relation", verdict == "relation"),
    ]


def _live_cases() -> list[Case]:
    """Read the arms gate-G36 was filed on, against the live suite.

    ⚑ THESE ARE THE EVIDENCE, so they are read from the tree rather than transcribed. If the
    suite is rewritten so these arms stop being relations, this goes red and the finding wants
    re-deriving — which is the correct outcome, not a nuisance.
    """
    probe = ROOT / "substrate" / "module_trim_selftest.py"
    if not probe.is_file():
        return [("module_trim_selftest.py is present to read", False)]
    found = {
        a.name: a
        for a in relation_arm.read(
            "module_trim_selftest.py",
            {
                "a_stranded_import_may_vanish_but_a_body_line_may_not": 2,
                "only_a_real_main_guard_is_recognised": 2,
            },
        )
    }
    asym = found.get("a_stranded_import_may_vanish_but_a_body_line_may_not")
    guard = found.get("only_a_real_main_guard_is_recognised")
    return [
        ("the asymmetry arm is read", asym is not None),
        # ⚑ THE ARM WHOSE TWO HALVES EACH PASS TRIVIALLY ALONE.
        ("the asymmetry arm is a RELATION", asym is not None and asym.relation),
        ("it probes one predicate", asym is not None and len(set(asym.probes)) == 1),
        ("the planted-negatives arm is read", guard is not None),
        ("the planted-negatives arm is a RELATION", guard is not None and guard.relation),
    ]


def _reach_cases() -> list[Case]:
    """Assert the census states its own reach rather than overstating it."""
    found = relation_arm.census()
    if not found:
        return [("the census reads multi-claim arms", False)]
    unread = [a for a in found if a.undecided]
    return [
        ("the census reads the authority's population", len(found) > 0),
        # ⚑⚑⚑ THIS ROW ONCE ASSERTED THAT UNDECIDED WAS THE MAJORITY, AND THREE WIDENINGS MADE
        #   THAT FALSE — so it went red on progress. A reach floor stated as a majority claim
        #   expires the moment the reach improves, which makes it a tracker of a NUMBER rather
        #   than of the property it was written to protect.
        # ⚑ THE PROPERTY IS THAT THE READER STILL WITHHOLDS. A classifier that read everything
        #   would report zero undecided, and its unreadable cases would have been silently
        #   promoted to INDEPENDENT — the direction that licenses a destructive split. So the
        #   assertion is that a real unread population survives, not that it dominates.
        ("the reader still withholds on arms it cannot read", len(unread) > 0),
        (
            "no undecided arm is also called a relation",
            all(not (a.undecided and a.relation) for a in found),
        ),
        # Every verdict is one of exactly three; a fourth would escape both columns.
        (
            "every verdict is one of the three declared",
            all(a.verdict in {"relation", "independent", "undecided"} for a in found),
        ),
    ]


def _render_cases() -> list[Case]:
    """Return the cases pinning that the render names what it could not decide."""
    made = (
        relation_arm.Arm("a.py", "rel", 2, "relation", ("same", "same")),
        relation_arm.Arm("a.py", "ind", 2, "independent", ("one", "two")),
        relation_arm.Arm("a.py", "unread", 2, "undecided", ()),
    )
    out = relation_arm.render(made)
    empty = relation_arm.render(())
    return [
        ("the render warns that splitting destroys a relation", "DESTROYS" in out),
        ("it names splitting a paydown for the independent arms", "paydown" in out),
        # ⚑ PRINTED EVEN AT ZERO — an unread arm is a different fact from a cleared one.
        ("it names the UNDECIDED column", "UNDECIDED" in out),
        ("the relation arm is spelled out with its probe", "rel" in out and "same" in out),
        ("an empty census is a fact about the WALK", "fact about the WALK" in empty),
        ("relations() returns only the relation arms", len(relation_arm.relations(made)) == 1),
    ]


def _live_binding_cases() -> list[Case]:
    """Read the two arms whose own docstrings say the discriminator IS the pair.

    ⚑⚑ THESE ARE THE WIDENING'S EVIDENCE, so they come from the tree. Both of
    `assert_census_selftest`'s arms assign from `_kinds` and compare the local, and both state in
    prose that without the second half a degenerate predicate would pass. Before the binding
    resolution they read UNDECIDED — the reader calling a self-described relation unclassifiable.
    """
    probe = ROOT / "substrate" / "assert_census_selftest.py"
    if not probe.is_file():
        return [("assert_census_selftest.py is present to read", False)]
    found = {
        a.name: a
        for a in relation_arm.read(
            "assert_census_selftest.py",
            {"a_narrowing_assert_is_load": 2, "identity_narrows_only_against_none": 2},
        )
    }
    bucket = {
        a.name: a
        for a in relation_arm.read(
            "ban_witness_selftest.py", {"a_bucket_reports_where_its_decisions_concentrate": 2}
        )
    }
    concentrate = bucket.get("a_bucket_reports_where_its_decisions_concentrate")
    narrowing = found.get("a_narrowing_assert_is_load")
    identity = found.get("identity_narrows_only_against_none")
    return [
        # ⚑⚑ THE ARM THAT DROVE THE MEMBERSHIP FIX, read live. Its guard is
        #   `"..." not in got.shape or "..." not in got.shape` — a literal on the LEFT, so a
        #   resolver taking `.left` unconditionally saw nothing and called it undecided.
        ("the membership arm is read", concentrate is not None),
        ("it is a RELATION", concentrate is not None and concentrate.relation),
        (
            "both guards probe the same field",
            concentrate is not None and set(concentrate.probes) == {"Bucket.shape"},
        ),
        ("the narrowing arm is read", narrowing is not None),
        ("it is a RELATION, not undecided", narrowing is not None and narrowing.relation),
        (
            "its shared predicate is named",
            narrowing is not None and set(narrowing.probes) == {"_kinds"},
        ),
        ("the identity arm is read", identity is not None),
        ("it is a RELATION too", identity is not None and identity.relation),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = (
        _verdict_cases()
        + _binding_cases()
        + _attribute_cases()
        + _transparent_cases()
        + _splittable_cases()
        + _named_cases()
        + _plumbing_cases()
        + _live_cases()
        + _live_binding_cases()
        + _reach_cases()
        + _render_cases()
    )
    bad = [label for label, holds in cases if not holds]
    print(f"relation_arm: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
