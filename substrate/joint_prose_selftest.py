#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the prose reader, and pin that it is a FLOOR rather than a verdict.

⚑⚑⚑ THE LOAD-BEARING PROPERTY IS THE ASYMMETRY. A hit is evidence FOR jointness and a miss is
SILENCE — never evidence against. Two syntactic discriminators were already built and refuted
(gate-G44), each failing by asserting a verdict its evidence could not carry, and a prose reader
that returned "independent" from an absent word would be the third and would fail in the
licensing direction. So the suite asserts silence is not independence, in both directions.

⚑⚑ THE LIVE ARMS ARE READ FROM THE TREE BECAUSE MY DOUBT ABOUT THEM WAS THE ERROR. Seeing the
first census I judged two `contrast` hits incidental — `"reports UNREAD rather than an empty
roster"` looked like one claim's value, not two joined claims. Opening both showed they are joint:
`a_missing_census_is_unread` asserts `known` is false AND `why` names UNREAD, and
`omitting_the_builder_skips_the_build` asserts three properties of one skipped path. The prose was
stronger evidence than I credited, so the cases read the real arms rather than my summary of them.

⚑ AND THE NEGATIVE CONTROL IS A DOCSTRING WITH NO SIGNAL, without which a reader hard-wired to
"joint" satisfies every positive row here and reports the whole tree as unsplittable.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import joint_prose

ROOT = Path(__file__).resolve().parent.parent

Case = tuple[str, bool]

_CONJUNCTION = "Check coverage names what is covered and what is not."
_CONTRAST = "Check reach returns the seed it found, not merely True."
_DECLARED = "Check the state is its own. BOTH HALVES ARE ASSERTED, because each alone is weak."
_SILENT = "Check the parser reads a nested module path."
_EMPTY = ""


def _signal_cases() -> list[Case]:
    """Return the cases pinning the three measured prose forms."""
    conj, conj_quote = joint_prose.read_doc(_CONJUNCTION)
    contrast, _ = joint_prose.read_doc(_CONTRAST)
    declared, _ = joint_prose.read_doc(_DECLARED)
    return [
        ("a conjunction joining two claims is read", conj == "conjunction"),
        ("the quote carries the match, so it can be audited", "covered" in conj_quote),
        # ⚑ A CONTRAST SAYS THE FIRST HALF IS INSUFFICIENT — which is what a control IS.
        ("a contrast is read", contrast == "contrast"),
        ("a declared fusion is read", declared == "declared"),
    ]


def _weak_cases() -> list[Case]:
    """Return the cases pinning that a conjunction alone is NOT jointness (gate-G46).

    ⚑⚑ MEASURED BY AUDIT, NOT BY TASTE. Five hits were opened: both `conjunction` matches are
    FALSE and all three `contrast`/`declared` matches are real. `a_binding_runs` is a sequential
    pipeline — unbound, then raises, then empty — and `a_stamp_path_cannot_collide` tests two
    independent properties. Both matched an `and` in the DESIGN PARAGRAPH, which says why the arm
    exists rather than what its guards assert.

    ⚑ THE CLASS IS REPORTED, NOT DROPPED. Losing it would hide the evidence that it fires;
    counting it would freeze splittable arms, which is the over-reach that cost two structural
    discriminators.
    """
    signal, _ = joint_prose.read_doc(_CONJUNCTION)
    row = joint_prose.Prose("a.py", "b", signal, "")
    return [
        ("a conjunction is still READ", signal == "conjunction"),
        ("but it does NOT count as joint", not row.joint),
        ("it is reported as its own weak class", row.weak),
        # ⚑ THE STRONG CLASSES MUST NOT BE SWEPT UP BY THE NARROWING.
        ("a contrast still counts as joint", joint_prose.Prose("a.py", "b", "contrast", "").joint),
        (
            "a declared fusion still counts as joint",
            joint_prose.Prose("a.py", "b", "declared", "").joint,
        ),
        (
            "a silent arm is neither joint nor weak",
            not joint_prose.Prose("a.py", "b", "silent", "").joint
            and not joint_prose.Prose("a.py", "b", "silent", "").weak,
        ),
    ]


def _floor_cases() -> list[Case]:
    """Return the cases pinning that silence is NOT independence.

    ⚑⚑ THE ASYMMETRY IS THE DESIGN. Prose is weaker evidence than structure, so an arm may be
    joint and say nothing. Reading that silence as independence would license a split on an
    absence — the shape gate-G44 reverted a whole discriminator to avoid.
    """
    silent, quote = joint_prose.read_doc(_SILENT)
    empty, _ = joint_prose.read_doc(_EMPTY)
    return [
        # ⚑ THE CONTROL: without this a reader stuck at "joint" passes every row above and
        #   reports the entire tree as unsplittable.
        ("an ordinary docstring is SILENT, not joint", silent == "silent"),
        ("a silent reading is not joint", not joint_prose.Prose("a", "b", silent, "").joint),
        ("an absent docstring is silent too", empty == "silent"),
        ("a silent reading carries no quote to over-read", quote == ""),
    ]


def _order_cases() -> list[Case]:
    """Return the cases pinning that the strongest signal present is the one reported.

    ⚑ A DECLARED FUSION IS THE AUTHOR SAYING IT; a conjunction is the weakest and most likely to
    be incidental. Reporting the last match scanned rather than the best would understate the
    evidence on exactly the arms where it is strongest.
    """
    both = "Check a thing and the other thing. ⚑ BOTH HALVES ARE ASSERTED here."
    signal, _ = joint_prose.read_doc(both)
    return [
        ("a declared fusion outranks a conjunction", signal == "declared"),
    ]


def _render_cases() -> list[Case]:
    """Return the cases pinning that the render states its own weakness."""
    made = (
        joint_prose.Prose("a.py", "joint", "declared", "BOTH HALVES ARE ASSERTED"),
        joint_prose.Prose("a.py", "loose", "conjunction", "a thing and the other"),
        joint_prose.Prose("a.py", "quiet", "silent", ""),
    )
    out = joint_prose.render(made)
    empty = joint_prose.render(())
    return [
        ("the render names the joint population", "joint" in out),
        # ⚑ THE WEAK CLASS GETS ITS OWN ROW, so a measured false-positive class cannot be
        #   absorbed into either the joint side or the silent side.
        ("the weak class is its own row", "MEASURED WEAK" in out),
        # ⚑ ASSERTED ON THE RECORD, NOT ON THE RENDERED TEXT. A first cut sliced the output
        #   around a column label, which passes for the wrong reason the moment a row moves.
        (
            "the weak arm is not counted as joint",
            not joint_prose.Prose("a.py", "loose", "conjunction", "").joint,
        ),
        # ⚑⚑ THE WORDING IS THE GUARD. A reader skimming a "silent" count could bank it as an
        #   independent count, so the row says what it is not.
        ("the silent row says it is NOT independence", "NOT independent" in out),
        ("the joint arm is spelled out with its quote", "BOTH HALVES" in out),
        # ⚑⚑ THE SAMPLE MUST NAME ITS CLASS, and this is asserted by ORDER, not by presence.
        #   The joint rows were appended directly under the SILENT count, so `contrast` rows
        #   read as members of "prose says nothing". Counts were right; the layout inverted
        #   them. Asserting the header merely EXISTS would pass with it in the wrong place.
        (
            "the joint sample is headed, so it cannot read as the silent row's members",
            out.index("JOINT arm(s), with the quote") > out.index("NOT independent"),
        ),
        (
            "the header sits ABOVE the first sampled row",
            out.index("JOINT arm(s), with the quote") < out.index("BOTH HALVES"),
        ),
        ("an empty read is a fact about the WALK", "fact about the WALK" in empty),
    ]


def _live_cases() -> list[Case]:
    """Read the arms whose prose I DOUBTED, against the tree.

    ⚑⚑ THESE ARE HERE BECAUSE MY DOUBT WAS THE ERROR. Both looked like incidental `rather than`
    matches and both are genuinely joint — the first asserts `known` is false AND `why` names
    UNREAD, the second asserts three properties of one skipped path. A case built on my reading
    would have pinned the wrong thing, so it is built on theirs.
    """
    probe = ROOT / "substrate" / "gate_precondition_selftest.py"
    if not probe.is_file():
        return [("gate_precondition_selftest.py is present to read", False)]
    census = {
        p.name: p
        for p in joint_prose.read(
            "gate_precondition_selftest.py", frozenset({"a_missing_census_is_unread"})
        )
    }
    drive = {
        p.name: p
        for p in joint_prose.read(
            "catalog_drive_selftest.py", frozenset({"omitting_the_builder_skips_the_build"})
        )
    }
    unread = census.get("a_missing_census_is_unread")
    skipped = drive.get("omitting_the_builder_skips_the_build")
    return [
        ("the doubted contrast arm is read", unread is not None),
        ("its prose declares the claims joint", unread is not None and unread.joint),
        ("the second doubted arm is read", skipped is not None),
        ("its prose declares the claims joint too", skipped is not None and skipped.joint),
    ]


def _live_weak_cases() -> list[Case]:
    """Read the two arms whose conjunction matches were FALSE, against the tree.

    ⚑⚑ THESE ARE THE MEASUREMENT gate-G46 RESTS ON, so they come from the tree rather than from
    my summary. `a_binding_runs` is a sequential pipeline (unbound, then raises, then empty) and
    `a_stamp_path_cannot_collide_across_directories` asserts two independent properties. Both
    match an `and` that sits in the design paragraph, never in the claim structure.

    ⚑ IF EITHER EVER READS AS JOINT, the narrowing has been undone and this goes red — which is
    the point of reading them live rather than transcribing the verdict.
    """
    probe = ROOT / "substrate" / "concept_bindings_selftest.py"
    if not probe.is_file():
        return [("concept_bindings_selftest.py is present to read", False)]
    binding = {
        p.name: p
        for p in joint_prose.read("concept_bindings_selftest.py", frozenset({"a_binding_runs"}))
    }
    stamp = {
        p.name: p
        for p in joint_prose.read(
            "gen_selftest_mk_selftest.py",
            frozenset({"a_stamp_path_cannot_collide_across_directories"}),
        )
    }
    runs = binding.get("a_binding_runs")
    collide = stamp.get("a_stamp_path_cannot_collide_across_directories")
    return [
        ("the pipeline arm is read", runs is not None),
        ("it does NOT read as joint", runs is not None and not runs.joint),
        ("it is reported as weak rather than dropped", runs is not None and runs.weak),
        ("the two-property arm is read", collide is not None),
        ("it does NOT read as joint either", collide is not None and not collide.joint),
    ]


def _live_bound_cases() -> list[Case]:
    """Pin the MEASURED false positive in the strong class (gate-G47).

    ⚑⚑ THE PROSE READER IS WRONG ABOUT THIS ARM AND THE SUITE SAYS SO. `the_generator_is_not_debt`
    matches `contrast`, and one of its two guards is a FIXTURE PRECONDITION — *was the parse seen
    at all* — which protects the fixture rather than asserting half a law. The structural reader
    calls it independent on two different predicates, and structure is right.

    ⚑ IT IS ASSERTED AS A KNOWN BOUND, not as a defect to fix. A narrowing that removed it would
    have to distinguish a fixture guard from a claim guard, which is AST work and belongs in the
    structural reader — the one that already gets this arm right. Pinning it here keeps the bound
    visible instead of leaving the docstring to carry it alone.
    """
    probe = ROOT / "substrate" / "dag_source_selftest.py"
    if not probe.is_file():
        return [("dag_source_selftest.py is present to read", False)]
    found = {
        p.name: p
        for p in joint_prose.read(
            "dag_source_selftest.py", frozenset({"the_generator_is_not_debt"})
        )
    }
    generator = found.get("the_generator_is_not_debt")
    return [
        ("the fixture-guarded arm is read", generator is not None),
        # ⚑ THE READER STILL CALLS IT JOINT, WHICH IS THE BOUND. If this ever goes red the class
        #   has been narrowed and gate-G47's bound wants re-deriving rather than deleting.
        (
            "the prose reader still reads it as joint — a KNOWN false positive",
            generator is not None and generator.joint,
        ),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = (
        _signal_cases()
        + _weak_cases()
        + _floor_cases()
        + _order_cases()
        + _render_cases()
        + _live_cases()
        + _live_weak_cases()
        + _live_bound_cases()
    )
    bad = [label for label, holds in cases if not holds]
    print(f"joint_prose: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
