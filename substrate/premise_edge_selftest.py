#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.premise_edge` — undeclared, unchecked and refuted are three things.

⚑⚑⚑ THE UNCHECKABLE CASE IS THE ITEM. A premise nobody has decided is not a premise that FAILED,
and collapsing the two makes an unmeasured grounding indistinguishable from a refuted one — the
reading that turns a reader-side gap into an accusation about the claim. Both prior figures for
R12b (113, then 345) were void because a number said nothing about the census it rested on.

⚑⚑ AND THE MULTI-TARGET SPLIT IS LOAD-BEARING. `rests-on = {A, B}` arrives as ONE string, so a
reader taking the field whole treats `"A, B"` as a single premise name matching nothing — every
edge silently unresolvable while the count reads correct. Live: `B3` declares eight premises in
one field.

⚑ THE FIXTURES ARE FAKE BIBS. A case reading the live warrants measures today's 9 declared edges;
it would go red the moment someone declares a tenth — reporting correct work as a defect. What is
asserted is that this reader reaches the right verdict about whatever bib it is handed.
"""

from __future__ import annotations

import sys

from substrate import premise_edge

# A bib with one single-premise claim, one multi-premise claim, and one with no grounding.
_ENTRIES = {
    "R12b": {"claim": "re-emitted against a current census", "rests-on": "CENSUS"},
    "B3": {"claim": "the gated commit", "rests-on": "A5, R8, G1"},
    "CENSUS": {"claim": "the census is current"},
}

_MULTI = ("A5", "R8", "G1")


class _Bib:
    """A bib returning the entries the case chose."""

    def __init__(self, entries: dict[str, dict[str, str]] | None = None) -> None:
        self._entries = entries if entries is not None else dict(_ENTRIES)

    def entries(self, path: str | None = None) -> dict[str, dict[str, str]]:
        """Return the fixture entries."""
        del path
        return self._entries


def _grounding_with(
    api: _Bib,
    claim: str,
    decide: dict[str, tuple[bool, str]] | None = None,
) -> tuple[tuple[premise_edge.Premise, ...], str]:
    """Run the reader against a fixture bib."""

    def _load() -> tuple[premise_edge.Bib | None, str]:
        return api, ""

    original = premise_edge.bib
    premise_edge.bib = _load
    try:
        return premise_edge.grounding(claim, decide)
    finally:
        premise_edge.bib = original


def a_single_premise_is_read(out: list[str]) -> int:
    """Check a one-target edge yields one premise."""
    rows, why = _grounding_with(_Bib(), "R12b", {"CENSUS": (True, "stamp matches")})
    if why:
        out.append(f"selftest: reading a declared claim reported {why!r}")
        return 1
    if len(rows) != 1 or rows[0].premise != "CENSUS":
        out.append(f"selftest: the single premise read as {rows!r}")
        return 1
    return 0


def a_multi_premise_field_is_split(out: list[str]) -> int:
    """Check a comma-separated edge becomes several premises — the LOAD-BEARING case.

    ⚑⚑ ONE STRING, MANY PREMISES. Taking the field whole yields a premise named `"A5, R8, G1"`
    that matches nothing, so every one of them reads unresolvable while the claim reads grounded.
    """
    rows, _why = _grounding_with(_Bib(), "B3")
    got = tuple(row.premise for row in rows)
    if got != _MULTI:
        out.append(f"selftest: the multi-premise field split to {got!r}")
        return 1
    return 0


def a_claim_with_no_edge_is_undeclared(out: list[str]) -> int:
    """Check a claim declaring nothing is UNDECLARED, not ungrounded.

    ⚑ AN ABSENT DECLARATION IS A FACT ABOUT THE BIB, not about the claim's foundations. Live, 36
    of 45 entries declare no `rests-on` — reading that as 36 broken groundings would be a census
    reporting its own coverage as a defect.
    """
    rows, why = _grounding_with(_Bib(), "CENSUS")
    if rows:
        out.append(f"selftest: an undeclared claim yielded premises: {rows!r}")
        return 1
    if "UNDECLARED" not in why:
        out.append(f"selftest: the undeclared reason reads as {why!r}")
        return 1
    return 0


def a_satisfied_premise_is_marked_holding(out: list[str]) -> int:
    """Check a decided-true premise reports satisfied."""
    rows, _why = _grounding_with(_Bib(), "R12b", {"CENSUS": (True, "stamp matches")})
    if not rows or rows[0].satisfied is not True:
        out.append(f"selftest: a satisfied premise read as {rows!r}")
        return 1
    return 0


def a_refuted_premise_is_marked_failing(out: list[str]) -> int:
    """Check a decided-false premise reports unsatisfied — the POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS, A READER CALLING EVERY DECIDED PREMISE SATISFIED passes the case above and
    reports R12b grounded against a stale census — the exact reading that voided two figures.
    """
    rows, _why = _grounding_with(_Bib(), "R12b", {"CENSUS": (False, "ledger is stale")})
    if not rows or rows[0].satisfied is not False:
        out.append(f"selftest: a refuted premise read as {rows!r}")
        return 1
    return 0


def an_undecided_premise_is_uncheckable(out: list[str]) -> int:
    """Check a premise with no verdict is UNCHECKABLE, not failing.

    ⚑⚑⚑ THE WHOLE ITEM. Folding undecided into failing makes a gap in the reader read as a defect
    in the claim, and the resulting count is a fact about what was supplied rather than about the
    grounding.
    """
    rows, _why = _grounding_with(_Bib(), "R12b")
    if not rows or rows[0].satisfied is not None:
        out.append(f"selftest: an undecided premise read as {rows!r}")
        return 1
    if rows[0].checkable:
        out.append("selftest: an undecided premise reported as checkable")
        return 1
    return 0


def blocked_holds_only_refuted_premises(out: list[str]) -> int:
    """Check the blocked set excludes undecided premises.

    ⚑ AN UNCHECKED PREMISE IS NOT EVIDENCE OF A BROKEN GROUNDING. Including it would make an
    unmeasured claim indistinguishable from a refuted one at exactly the call site that acts.
    """
    rows, _why = _grounding_with(_Bib(), "B3", {"A5": (False, "red"), "R8": (True, "green")})
    got = premise_edge.blocked(rows)
    if len(got) != 1 or got[0].premise != "A5":
        out.append(f"selftest: the blocked set read as {got!r}")
        return 1
    return 0


def blocked_is_empty_when_every_premise_holds(out: list[str]) -> int:
    """Check a fully satisfied grounding yields no blockers."""
    rows, _why = _grounding_with(_Bib(), "R12b", {"CENSUS": (True, "stamp matches")})
    if premise_edge.blocked(rows):
        out.append(f"selftest: a satisfied grounding reported blockers: {rows!r}")
        return 1
    return 0


def a_premise_carries_its_reason(out: list[str]) -> int:
    """Check the supplied verdict's reason survives to the row.

    ⚑ THE MECHANISM R12b USED: it inherits the census reason VERBATIM. A premise reporting only a
    boolean sends the reader back to re-derive why, which is where a stale figure gets quoted.
    """
    rows, _why = _grounding_with(_Bib(), "R12b", {"CENSUS": (False, "ledger is stale")})
    if not rows or "stale" not in rows[0].why:
        out.append(f"selftest: the premise lost its reason: {rows!r}")
        return 1
    return 0


def each_premise_names_its_claim(out: list[str]) -> int:
    """Check a row can be attributed without its surrounding call."""
    rows, _why = _grounding_with(_Bib(), "B3")
    stray = [row.premise for row in rows if row.claim != "B3"]
    if stray:
        out.append(f"selftest: premise row(s) with the wrong claim: {stray!r}")
        return 1
    return 0


def an_unloadable_bib_is_ungrounded(out: list[str]) -> int:
    """Check a bib that will not load reports its reason, not an empty grounding."""
    original = premise_edge.BIB
    premise_edge.BIB = "no-such-bib-reader-6d02"
    try:
        rows, why = premise_edge.grounding("R12b")
    finally:
        premise_edge.BIB = original
    if rows:
        out.append(f"selftest: an unloadable bib yielded premises: {rows!r}")
        return 1
    if "will not load" not in why:
        out.append(f"selftest: the unloadable reason reads as {why!r}")
        return 1
    return 0


def the_render_distinguishes_the_three_states(out: list[str]) -> int:
    """Check satisfied, refuted and unchecked render differently.

    ⚑ A RENDER THAT COLLAPSES TWO undoes the distinction at the last step, where the reader looks.
    """
    rows = (
        premise_edge.Premise(claim="X", premise="a", satisfied=True, why="ok"),
        premise_edge.Premise(claim="X", premise="b", satisfied=False, why="no"),
        premise_edge.Premise(claim="X", premise="c", satisfied=None, why="unknown"),
    )
    text = premise_edge.render("X", rows)
    if "✓" not in text or "⚑" not in text or "?" not in text:
        out.append(f"selftest: the render collapses states:\n{text}")
        return 1
    return 0


def the_declared_map_splits_every_edge(out: list[str]) -> int:
    """Check the whole-bib read splits multi-target fields too.

    ⚑ THE PER-CLAIM PATH AND THE CENSUS PATH MUST AGREE. Two splitters is how a summary reports a
    different edge count from the detail it summarises.
    """
    got = premise_edge.declared(_Bib())
    if got.get("B3") != _MULTI:
        out.append(f"selftest: the declared map read B3 as {got.get('B3')!r}")
        return 1
    if "CENSUS" in got:
        out.append("selftest: a claim with no edge appears in the declared map")
        return 1
    return 0


_ARMS = (
    a_single_premise_is_read,
    a_multi_premise_field_is_split,
    a_claim_with_no_edge_is_undeclared,
    a_satisfied_premise_is_marked_holding,
    a_refuted_premise_is_marked_failing,
    an_undecided_premise_is_uncheckable,
    blocked_holds_only_refuted_premises,
    blocked_is_empty_when_every_premise_holds,
    a_premise_carries_its_reason,
    each_premise_names_its_claim,
    an_unloadable_bib_is_ungrounded,
    the_render_distinguishes_the_three_states,
    the_declared_map_splits_every_edge,
)

_CASE_COUNT = 2 + 1 + 2 + 1 + 1 + 2 + 1 + 1 + 1 + 1 + 2 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"premise-edge selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"premise-edge selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
