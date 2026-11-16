#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.doc_split`: a conservation guard that can actually refuse.

⚑⚑⚑ THE LOAD-BEARING ARMS ARE THE NEGATIVE ONES, AND THAT IS NOT A STYLE PREFERENCE. A guard that
returns "conserved" unconditionally passes every positive arm ever written — the constant-predicate
failure this repo has measured repeatedly, most sharply where a coverage census reported every
module as uncovered and satisfied all its own assertions. So each direction of loss is planted
DELIBERATELY and asserted to be caught, and the positive arm only means something beside them.

⚑⚑ THE REWRITE ARM IS THE ONE A LINE COUNT CANNOT SEE. `a_rewritten_line_is_caught` moves a line
into a part with one word changed: the count is identical, every heading is present, the split
looks right, and the record has silently changed. That is the defect class the both-directions rule
exists for, and a one-directional check passes it.

⚑⚑⚑ AND THE OPERAND ARMS ARE A THIRD KIND, WHICH NEITHER OF THE ABOVE REACHES. The guard once
reported CONSERVED against an EMPTY reference file left by a failed `git show`. Every arm above
still held; the predicate was right. Both multiset differences of an empty origin are empty, which
is precisely what a faithful split produces, so the vacuous case is INDISTINGUISHABLE from the
success case no matter how many directions the comparison takes. The failure lives in the OPERAND,
and only an arm that hands the guard a degenerate operand can see it.

⚑⚑ EACH REFUSAL ARM IS PAIRED WITH ONE ASSERTING THE LEGITIMATE CASE IS *NOT* REFUSED. A guard
that refuses everything satisfies every refusal arm and reads as fixed — the constant-predicate
failure inverted. `a_one_line_origin_is_still_measured` and
`empty_parts_are_a_finding_rather_than_a_refusal` are those pairs.

⚑ THE FIXTURES ARE WRITTEN HERE RATHER THAN READ FROM THE LIVE TREE, so no arm expires when the
worklist this module was built to split is split again. A case pinned to a named document is a
witness-victim: it goes red the day the work succeeds.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.witness import witness_family

from substrate import doc_split, suite_emit

_ORIGIN = """* alpha, a finding with a marker
* beta, a second finding
* alpha, a finding with a marker
"""

# Split faithfully: the duplicate `alpha` is deliberately kept in BOTH parts, because the origin
# holds it twice and a multiset comparison is what makes that checkable.
_LEFT = "# Left\n\n* alpha, a finding with a marker\n* alpha, a finding with a marker\n"
_RIGHT = "# Right\n\n* beta, a second finding\n"

# The scaffolding a real split invents: the parts' own titles, absent from the origin.
# ⚑ THE ORIGIN CARRIES NO TITLE OF ITS OWN, DELIBERATELY. An earlier fixture gave it one and the
# suite went red — correctly, because neither part carried it, so the guard reported a genuine
# drop. Excusing an origin line through `_ALLOWED` would have "fixed" it by disabling the check;
# the fixture was wrong, not the guard, and this comment records which way that went.
_ALLOWED = frozenset({"# Left", "# Right"})

# The exit code a malformed invocation returns, kept distinct from a conservation failure.
_BAD_ARGV = 2

# Every spelling of an origin the comparison cannot measure. ⚑ THE BYTE-EMPTY ONE IS NOT THE
# CLASS — it is the instance that happened to be caught, and the other three are the same shape.
_VACUOUS_ORIGINS = ("", "   ", "\n\n\n", "  \n\t\n  ")


def _losses(*parts: str) -> tuple[doc_split.Loss, ...]:
    """Return the conservation losses for a split of the shared origin."""
    return doc_split.conserved(_ORIGIN, parts, _ALLOWED)


def a_faithful_split_conserves(out: list[str]) -> int:
    """Check that a split losing nothing reports no losses at all."""
    losses = _losses(_LEFT, _RIGHT)
    if losses:
        out.append(f"selftest: a faithful split reported {len(losses)} loss(es): {losses}")
        return 1
    return 0


def a_dropped_line_is_caught(out: list[str]) -> int:
    """Check that content present in the origin and in no part is reported as dropped.

    ⚑ THE PLAINEST FAILURE AND THE ONE A SPLITTER PRODUCES MOST — a section omitted from the part
    list entirely. It is checked first because a guard that misses this misses everything.
    """
    bad = 0
    dropped = [loss for loss in _losses(_LEFT) if loss.direction == "dropped"]
    if not dropped:
        out.append("selftest: omitting a whole part reported no dropped line")
        bad += 1
    elif "beta" not in dropped[0].line:
        out.append(f"selftest: the dropped line is {dropped[0].line!r}, want the beta finding")
        bad += 1
    return bad


def a_rewritten_line_is_caught(out: list[str]) -> int:
    """Check that a line altered in transit is caught, though the line COUNT is unchanged.

    ⚑⚑ THIS IS WHY BOTH DIRECTIONS ARE TAKEN. The part carries the same number of lines as the
    origin gave it, so any check keyed on a count agrees the split conserved. Only the reverse
    difference — content the parts hold that the origin never did — names the rewrite.
    """
    bad = 0
    edited = _RIGHT.replace("a second finding", "a SECOND finding")
    losses = _losses(_LEFT, edited)
    if not [loss for loss in losses if loss.direction == "gained"]:
        out.append("selftest: a rewritten line produced no gained loss")
        bad += 1
    if not [loss for loss in losses if loss.direction == "dropped"]:
        out.append("selftest: a rewritten line produced no dropped loss")
        bad += 1
    return bad


def a_duplicated_line_is_caught(out: list[str]) -> int:
    """Check that a line copied into two parts is reported, not silently accepted.

    ⚑ A SET COMPARISON CALLS THIS CONSERVED, which is the whole argument for the multiset. A
    finding that lands under two concerns is acted on twice, and the second reader has no way to
    know the first already did it.
    """
    losses = _losses(_LEFT, _RIGHT + "* beta, a second finding\n")
    if not [loss for loss in losses if loss.direction == "gained"]:
        out.append("selftest: duplicating a line across parts reported no loss")
        return 1
    return 0


def a_missing_duplicate_is_caught(out: list[str]) -> int:
    """Check that emitting a twice-held line only once is reported as a drop.

    ⚑ THE MULTISET'S OTHER HALF, and the one a set comparison is blind to in the losing direction:
    the origin holds `alpha` twice, a part holds it once, and every distinct line is present.
    """
    thin = "# Left\n\n* alpha, a finding with a marker\n"
    if not [loss for loss in _losses(thin, _RIGHT) if loss.direction == "dropped"]:
        out.append("selftest: dropping one of two identical lines reported no loss")
        return 1
    return 0


def the_allowance_excuses_only_gained_lines(out: list[str]) -> int:
    """Check that an allowance cannot excuse a line the ORIGIN held.

    ⚑⚑ THE ONE-DIRECTIONAL EXEMPTION IS WHAT KEEPS THE GUARD HONEST. An allowance readable in both
    directions would let a caller silence a genuine deletion by listing the deleted line, which is
    the loophole that swallows the rule standing beside it. Asserted by naming the beta finding as
    allowed and then dropping it: it must still be reported.
    """
    beta = "* beta, a second finding"
    losses = doc_split.conserved(_ORIGIN, (_LEFT,), frozenset({beta, "# Left"}))
    if not [loss for loss in losses if loss.direction == "dropped"]:
        out.append("selftest: an allowance excused a line the origin held")
        return 1
    return 0


def blank_lines_and_indentation_do_not_count(out: list[str]) -> int:
    """Check that re-indenting and re-spacing a line is not reported as a change.

    ⚑ A BULLET MOVED OUT OF A SECTION BECOMES A TOP-LEVEL BULLET. Refusing that would make every
    honest split fail, so indentation is normalised — and only indentation, which is why the
    rewrite arm above still fires on a single changed word.
    """
    alpha = "* alpha, a finding with a marker"
    indented = f"# Left\n\n\n    {alpha}\n\n  {alpha}\n"
    losses = doc_split.conserved(_ORIGIN, (indented, _RIGHT), _ALLOWED)
    if losses:
        out.append(f"selftest: re-indentation reported {len(losses)} loss(es)")
        return 1
    return 0


def the_report_verdict_follows_its_own_rows(out: list[str]) -> int:
    """Check that `ok` is derived from the losses rather than settable beside them."""
    bad = 0
    clean = doc_split.Report(origin="o", parts=("a",), losses=())
    dirty = doc_split.Report(origin="o", parts=("a",), losses=(doc_split.Loss("dropped", "x", 1),))
    if not clean.ok:
        out.append("selftest: a report with no losses is not ok")
        bad += 1
    if dirty.ok:
        out.append("selftest: a report carrying a loss reported ok")
        bad += 1
    return bad


def the_render_names_the_verdict_and_every_loss(out: list[str]) -> int:
    """Check that the rendered report states its verdict and hides no row behind a count.

    ⚑ A SUMMARY THAT COUNTS THE LOSSES LEAVES THE READER TO FIND THEM IN TWO DOCUMENTS. The line
    itself is what locates the defect, so every one is printed.
    """
    bad = 0
    report = doc_split.Report(
        origin="o",
        parts=("a", "b"),
        losses=(
            doc_split.Loss("dropped", "the beta finding", 1),
            doc_split.Loss("gained", "an invented line", 2),
        ),
    )
    text = doc_split.render(report)
    if "NOT CONSERVED" not in text:
        out.append("selftest: a report with losses did not render NOT CONSERVED")
        bad += 1
    for needle in ("the beta finding", "an invented line"):
        if needle not in text:
            out.append(f"selftest: the render omitted {needle!r}")
            bad += 1
    return bad


def a_bad_invocation_exits_two_not_one(out: list[str]) -> int:
    """Check that a malformed call is distinguishable from a conservation failure.

    ⚑ EXIT 1 AND EXIT 2 ARE FIXED IN DIFFERENT PLACES — the documents versus the call site — so
    collapsing them sends a reader hunting for missing content that was never measured.
    """
    if doc_split.main(("only-one-path",)) != _BAD_ARGV:
        out.append("selftest: a one-argument invocation did not exit 2")
        return 1
    return 0


def slicing_returns_the_named_spans_in_order(out: list[str]) -> int:
    """Check that spans are 1-indexed, inclusive, and emitted in the order the caller gave.

    ⚑ ORDER IS THE CALLER'S, NOT SORTED. A concern assembled from three ranges of a chronological
    record often wants the later one first, and silently reordering would produce a document whose
    argument runs backwards while conserving every line — invisible to the guard beside it.
    """
    bad = 0
    text = "one\ntwo\nthree\nfour\n"
    if doc_split.slice_lines(text, ((1, 2),)) != "one\ntwo":
        out.append("selftest: a leading span was not 1-indexed and inclusive")
        bad += 1
    if doc_split.slice_lines(text, ((3, 3), (1, 1))) != "three\none":
        out.append("selftest: spans were not emitted in the order given")
        bad += 1
    return bad


def a_malformed_span_refuses_rather_than_emitting_nothing(out: list[str]) -> int:
    """Check that a bad or absent span exits 2 instead of silently producing an empty slice.

    ⚑⚑ AN EMPTY SLICE IS THE PLAUSIBLE-AND-WRONG OUTPUT. It writes a well-formed part, loses the
    content, and only the conservation guard downstream would ever notice — so the operand is
    refused where it is read, which is the one place the cause is still legible.
    """
    bad = 0
    for argv in (("--slice", "x.md", "3-1"), ("--slice", "x.md", "notaspan"), ("--slice", "x.md")):
        if doc_split.main(argv) != _BAD_ARGV:
            out.append(f"selftest: {argv!r} did not exit 2")
            bad += 1
    return bad


def only_dropped_keeps_the_unexcusable_direction(out: list[str]) -> int:
    """Check that `only_dropped` hides gained losses, keeps dropped ones, and refuses on them.

    ⚑⚑ THE THIRD ASSERTION IS WHAT MAKES THE MODE HONEST. A filter that removed the gained rows
    and then always reported `ok` would satisfy any positive check — so the verdict is asserted in
    BOTH states: scaffolding alone must read ok, and a genuine drop must not.
    """
    bad = 0
    gained_only = doc_split.Report("o", ("a",), (doc_split.Loss("gained", "# Left", 1),))
    both = doc_split.Report(
        "o",
        ("a",),
        (doc_split.Loss("gained", "# Left", 1), doc_split.Loss("dropped", "a real finding", 1)),
    )
    if not doc_split.only_dropped(gained_only).ok:
        out.append("selftest: only_dropped refused a report whose losses are all gained")
        bad += 1
    filtered = doc_split.only_dropped(both)
    if filtered.ok:
        out.append("selftest: only_dropped reported ok while a dropped line remained")
        bad += 1
    if [loss.direction for loss in filtered.losses] != ["dropped"]:
        out.append("selftest: only_dropped did not keep exactly the dropped losses")
        bad += 1
    return bad


def a_vacuous_origin_is_refused_in_every_spelling(out: list[str]) -> int:
    """Check that an origin with no body lines REFUSES rather than reporting CONSERVED.

    ⚑⚑⚑ THE MEASURED DEFECT. A run reported CONSERVED against a reference a failed `git show` had
    left empty. The both-directions rule was correct and could not see it: both multiset
    differences of an empty origin are empty, which is exactly what a faithful split produces. The
    failure was in the OPERAND, so no strengthening of the PREDICATE reaches it.

    ⚑⚑ EVERY SPELLING, BECAUSE THE BYTE-EMPTY ONE IS NOT THE CLASS. Whitespace, bare newlines and
    a file of blank lines all reduce to no body lines and are equally vacuous; refusing only the
    caught instance would leave its siblings live.
    """
    bad = 0
    for vacuous in _VACUOUS_ORIGINS:
        try:
            doc_split.conserved(vacuous, (_LEFT, _RIGHT), _ALLOWED)
        except doc_split.VacuousOriginError:
            continue
        out.append(f"selftest: a vacuous origin {vacuous!r} was not refused")
        bad += 1
    return bad


def a_one_line_origin_is_still_measured(out: list[str]) -> int:
    """Check the refusal is keyed on an UNMEASURABLE origin, never on a small one — THE PAIR.

    ⚑⚑⚑ WITHOUT THIS ARM A `conserved` THAT REFUSED EVERYTHING would satisfy the case above and
    read as fixed. That is the constant-predicate failure inverted: the refusal arm alone cannot
    tell a guard that refuses the vacuum from one that refuses all work.

    ⚑ A ONE-LINE ORIGIN IS THE NEAR NEIGHBOUR AND IT MUST STILL BITE, in both directions — a part
    that drops the line reports `dropped`, and a faithful part reports nothing at all.
    """
    bad = 0
    single = "* the only finding\n"
    if doc_split.conserved(single, ("# Left\n\n* the only finding\n",), frozenset({"# Left"})):
        out.append("selftest: a faithful one-line split was reported as losing content")
        bad += 1
    if not [
        loss
        for loss in doc_split.conserved(single, ("# Left\n",), frozenset({"# Left"}))
        if loss.direction == "dropped"
    ]:
        out.append("selftest: a one-line origin's dropped line was not reported")
        bad += 1
    return bad


def empty_parts_are_a_finding_rather_than_a_refusal(out: list[str]) -> int:
    """Check that parts holding nothing report every line dropped — DELIBERATELY NOT REFUSED.

    ⚑⚑ THIS IS THE GUARD'S LOUDEST TRUE FINDING, and refusing it would convert the sharpest
    detection the tool has into an error about the invocation. The degenerate operand is the
    ORIGIN, whose emptiness makes the comparison vacuous; empty PARTS make it maximally
    informative. Pinned so a later reader does not extend the refusal by symmetry.
    """
    losses = doc_split.conserved(_ORIGIN, ("", ""), _ALLOWED)
    if not [loss for loss in losses if loss.direction == "dropped"]:
        out.append("selftest: empty parts against a real origin reported no dropped line")
        return 1
    return 0


def an_unreadable_origin_refuses_by_its_own_name(out: list[str]) -> int:
    """Check an ABSENT origin refuses as unreadable, not as empty — different repairs.

    ⚑⚑ THE FAILED `git show` LEFT A FILE THAT WAS BOTH. Collapsing the two would send a reader to
    inspect an empty document when the document is missing, so the message names which it saw.
    """
    try:
        doc_split.consider(Path("/nonexistent/origin.md"), ())
    except doc_split.VacuousOriginError as refused:
        if "could not be read" not in str(refused):
            out.append(f"selftest: an absent origin refused as {refused}, not as unreadable")
            return 1
        return 0
    out.append("selftest: an absent origin was not refused")
    return 1


def a_vacuous_origin_exits_two_through_the_cli(out: list[str]) -> int:
    """Check the refusal reaches the command line as a BAD INVOCATION, not a conservation failure.

    ⚑ EXIT 2, NOT 1, and the distinction is the one `main` already draws: exit 1 says content is
    missing from the documents, exit 2 says the call itself cannot be answered. A vacuous origin
    is the second — nothing was measured — so reporting it as 1 would send a reader hunting for
    losses that were never computed.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        origin = base / "origin.md"
        origin.write_text("\n\n", encoding="utf-8")
        part = base / "part.md"
        part.write_text("# Left\n", encoding="utf-8")
        if doc_split.main((str(origin), str(part))) != _BAD_ARGV:
            out.append("selftest: a whitespace-only origin did not exit 2 through the CLI")
            return 1
    return 0


FAMILY = witness_family.of(
    key="doc_split",
    apex="a markdown split conserves its origin: every non-blank line lands in exactly one "
    "part, checked as a multiset in both directions so a drop, a duplicate and a "
    "silent rewrite are each named — and an origin with nothing to conserve is REFUSED "
    "rather than reported conserved",
    subject="`substrate.doc_split`'s conservation guard over a document split by concern",
    members=(
        witness_family.Member(
            name="a_faithful_split_conserves",
            claim="a split losing nothing reports no losses",
        ),
        witness_family.Member(
            name="a_dropped_line_is_caught",
            claim="content in the origin and in no part is reported as dropped",
            cases=2,
        ),
        witness_family.Member(
            name="a_rewritten_line_is_caught",
            claim="a line altered in transit is caught though the count is unchanged",
            cases=2,
        ),
        witness_family.Member(
            name="a_duplicated_line_is_caught",
            claim="a line copied into two parts is reported, not silently accepted",
        ),
        witness_family.Member(
            name="a_missing_duplicate_is_caught",
            claim="emitting a twice-held line once is reported as a drop",
        ),
        witness_family.Member(
            name="the_allowance_excuses_only_gained_lines",
            claim="an allowance cannot excuse a line the origin held",
        ),
        witness_family.Member(
            name="blank_lines_and_indentation_do_not_count",
            claim="re-indenting and re-spacing a line is not a change",
        ),
        witness_family.Member(
            name="the_report_verdict_follows_its_own_rows",
            claim="ok is derived from the losses rather than stored beside them",
            cases=2,
        ),
        witness_family.Member(
            name="the_render_names_the_verdict_and_every_loss",
            claim="the render states its verdict and hides no row behind a count",
            cases=3,
        ),
        witness_family.Member(
            name="a_bad_invocation_exits_two_not_one",
            claim="a malformed call is distinguishable from a conservation failure",
        ),
        witness_family.Member(
            name="slicing_returns_the_named_spans_in_order",
            claim="spans are 1-indexed, inclusive, and emitted in the caller's order",
            cases=2,
        ),
        witness_family.Member(
            name="a_malformed_span_refuses_rather_than_emitting_nothing",
            claim="a bad or absent span exits 2 instead of silently slicing nothing",
            cases=3,
        ),
        witness_family.Member(
            name="only_dropped_keeps_the_unexcusable_direction",
            claim="gained losses are hidden, dropped ones kept, and the verdict follows",
            cases=3,
        ),
        witness_family.Member(
            name="a_vacuous_origin_is_refused_in_every_spelling",
            claim="an origin with no body lines is refused, not reported conserved — empty, "
            "whitespace-only and blank-line spellings alike",
            cases=len(_VACUOUS_ORIGINS),
        ),
        witness_family.Member(
            name="a_one_line_origin_is_still_measured",
            claim="the refusal is keyed on an unmeasurable origin, never a small one — the "
            "discriminator against a guard that refuses everything",
            cases=2,
        ),
        witness_family.Member(
            name="empty_parts_are_a_finding_rather_than_a_refusal",
            claim="empty parts against a real origin stay the guard's loudest true finding",
        ),
        witness_family.Member(
            name="an_unreadable_origin_refuses_by_its_own_name",
            claim="an absent origin refuses as unreadable rather than as empty",
        ),
        witness_family.Member(
            name="a_vacuous_origin_exits_two_through_the_cli",
            claim="a vacuous origin exits 2, not 1 — nothing measured, not content missing",
        ),
    ),
)

_ARMS = (
    a_faithful_split_conserves,
    a_dropped_line_is_caught,
    a_rewritten_line_is_caught,
    a_duplicated_line_is_caught,
    a_missing_duplicate_is_caught,
    the_allowance_excuses_only_gained_lines,
    blank_lines_and_indentation_do_not_count,
    the_report_verdict_follows_its_own_rows,
    the_render_names_the_verdict_and_every_loss,
    a_bad_invocation_exits_two_not_one,
    slicing_returns_the_named_spans_in_order,
    a_malformed_span_refuses_rather_than_emitting_nothing,
    only_dropped_keeps_the_unexcusable_direction,
    a_vacuous_origin_is_refused_in_every_spelling,
    a_one_line_origin_is_still_measured,
    empty_parts_are_a_finding_rather_than_a_refusal,
    an_unreadable_origin_refuses_by_its_own_name,
    a_vacuous_origin_exits_two_through_the_cli,
)

_CASE_COUNT = FAMILY.count
_SELF_KEY = "substrate/doc_split_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
