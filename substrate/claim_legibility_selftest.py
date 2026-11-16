#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.claim_legibility` — and the unfalsifiable form both members replaced.

⚑⚑⚑ THE FALSIFIABILITY CASES ARE THE POINT. An earlier form of the decision witness was
`cmd = "true"`, which provably cannot fail; a mutation sweep grades that INDETERMINATE, the bucket
reserved for *"falsifiability is not demonstrated"*. So every arm here comes in a pair: one input
that must OPEN and one that must CLOSE. A member with only the closing half is the same defect
wearing a predicate.

⚑⚑ AND THE PAIRING IS NOT DECORATION. The reasoning that produced `true` was *"a user decision is
not debt, so it must never block"* — correct about the gate, and silently fatal to the claim. A
suite that only checked the happy path would have re-derived exactly that.

⚑ THE FIXTURES ARE PROSE STRINGS THROUGH A FIXTURE BIB, NOT THE LIVE WORKLIST. A case reading the
real claims passes or fails on today's wording, so it would report the corpus rather than the
reader — and this family's subject IS claim prose, which makes the temptation strongest here.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.witness import witness_row

from substrate import claim_legibility, warrant_bib

_TWO_MEMBERS = 2

# A decision claim that states an outcome.
_DECIDED = """@misc{U1,
  section = {s},
  claim   = {a harness guard blocks the tree-wide checkout that destroyed a day of work twice},
  check   = {item:U1}
}
"""

# The same claim phrased as a question — nothing to check against later.
_ASKED = """@misc{U1,
  section = {s},
  claim   = {should a harness guard block the tree-wide checkout of the source tree?},
  check   = {item:U1}
}
"""

# A retraction naming its successor.
_NAMED = """@misc{R14-v1,
  section = {s},
  claim   = {R14 was filed as a tooling build; RETRACTED, superseded by R14-v2 which states it},
  check   = {item:R14-legible}
}
"""

# A retraction that says it was retracted and never says by what.
_UNNAMED = """@misc{R14-v1,
  section = {s},
  claim   = {R14 was filed as a tooling build and has since been RETRACTED as misconceived},
  check   = {item:R14-legible}
}
"""


def _verdict(where: str, text: str, run: str, key: str = "U1") -> witness_row.Verdict | None:
    """Write a fixture bib, point the reader at it, and return the last verdict."""
    path = Path(where) / "warrants.bib"
    path.write_text(text, encoding="utf-8")
    original = warrant_bib.BIB
    warrant_bib.BIB = path
    try:
        rows = (
            list(claim_legibility.witness_decision(key))
            if run == "decision"
            else list(claim_legibility.witness_retraction(key, "R14-v2"))
        )
    finally:
        warrant_bib.BIB = original
    verdicts = [r for r in rows if isinstance(r, witness_row.Verdict)]
    return verdicts[-1] if verdicts else None


def a_decision_stating_an_outcome_closes(out: list[str]) -> int:
    """Check a claim that commits to something passes."""
    with tempfile.TemporaryDirectory() as where:
        got = _verdict(where, _DECIDED, "decision")
    if got is None or got.state != witness_row.CLOSED:
        out.append(f"selftest: a stated decision did not close: {got!r}")
        return 1
    return 0


def a_decision_phrased_as_a_question_opens(out: list[str]) -> int:
    """Check the predicate CAN fail — the arm that makes this member falsifiable at all.

    ⚑⚑⚑ THE DEFECT THIS REPLACES. `cmd = "true"` cannot fail and grades indeterminate; a witness
    with only the closing arm above is that same unfalsifiability wearing a predicate. A claim
    phrased as a question has nothing to check against later, which is how *pending* becomes
    permanent.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _verdict(where, _ASKED, "decision")
    if got is None or got.state != witness_row.OPEN:
        out.append(f"selftest: a question-form claim did not open: {got!r}")
        return 1
    return 0


def an_open_decision_carries_a_route(out: list[str]) -> int:
    """Check the finding says what to do about it.

    ⚑ A VERDICT WITHOUT A PART IS A NUMBER. The ordering ranks by population, so an item that
    opens and emits nothing can be weighed only by its own say-so.
    """
    with tempfile.TemporaryDirectory() as where:
        path = Path(where) / "warrants.bib"
        path.write_text(_ASKED, encoding="utf-8")
        original = warrant_bib.BIB
        warrant_bib.BIB = path
        try:
            rows = list(claim_legibility.witness_decision("U1"))
        finally:
            warrant_bib.BIB = original
    parts = [r for r in rows if isinstance(r, witness_row.Part)]
    if not parts or not parts[0].route:
        out.append(f"selftest: an open decision carried no route: {parts!r}")
        return 1
    return 0


def a_retraction_naming_its_successor_closes(out: list[str]) -> int:
    """Check a retraction that says what replaced it passes."""
    with tempfile.TemporaryDirectory() as where:
        got = _verdict(where, _NAMED, "retraction", "R14-v1")
    if got is None or got.state != witness_row.CLOSED:
        out.append(f"selftest: a named successor did not close: {got!r}")
        return 1
    return 0


def a_retraction_without_a_successor_opens(out: list[str]) -> int:
    """Check the retraction predicate CAN fail.

    ⚑⚑ THE FIXTURE SAYS "RETRACTED" AND NAMES NOTHING, deliberately. A predicate keying on the
    word *retracted* rather than on the successor would pass this — and it is the realistic
    failure, since a retraction always says it is one.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _verdict(where, _UNNAMED, "retraction", "R14-v1")
    if got is None or got.state != witness_row.OPEN:
        out.append(f"selftest: an unnamed successor did not open: {got!r}")
        return 1
    return 0


def an_unreadable_claim_opens_rather_than_raising(out: list[str]) -> int:
    """Check a key with no entry OPENS instead of crashing.

    ⚑ A WITNESS THAT RAISES TAKES THE WHOLE ROSTER DOWN. An unreadable claim is a finding about
    the CLAIM — the item cannot be measured — and that is a verdict, not an exception.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _verdict(where, _DECIDED, "decision", "NO-SUCH-KEY")
    if got is None or got.state != witness_row.OPEN:
        out.append(f"selftest: an absent claim did not open: {got!r}")
        return 1
    return 0


def the_family_holds_one_member_per_predicate(out: list[str]) -> int:
    """Check the roster is the two claims, each a leaf."""
    got = claim_legibility.FAMILY
    bad = 0
    if len(got.members) != _TWO_MEMBERS:
        out.append(f"selftest: the family holds {len(got.members)} member(s)")
        bad += 1
    if got.count != len(got.members) or got.unsplit() != ():
        out.append(f"selftest: count {got.count}, unsplit {got.unsplit()!r}")
        bad += 1
    return bad


def the_familys_premises_all_resolve(out: list[str]) -> int:
    """Check no declared premise names a member the family does not hold."""
    got = claim_legibility.FAMILY.dangling_premises()
    if got != ():
        out.append(f"selftest: the family carries a dangling premise: {got!r}")
        return 1
    return 0


def the_question_tell_is_named_once(out: list[str]) -> int:
    """Check the reader exposes its tell rather than burying it in a literal.

    ⚑ A PREDICATE TYPED AT TWO SITES IS HOW A CHECK STARTS DISAGREEING WITH ITS OWN CASES — the
    witness looks for one thing and the suite asserts about another, and both pass.
    """
    if claim_legibility.QUESTION != "?":
        out.append(f"selftest: the question tell reads {claim_legibility.QUESTION!r}")
        return 1
    return 0


# ⚑⚑⚑ THE TWO ARMS BELOW BEAR THE FAMILY'S MEMBER NAMES, AND THAT CORRESPONDENCE IS THE POINT.
# `family_roster` reports a declared member no arm runs, because **a family naming a member
# nothing runs reads as MORE rigorous than an undeclared suite while being less.** This family
# declared two claims about the live worklist and ran neither by name: every other arm here drives
# a FIXTURE bib, which is the right subject for testing the reader and the wrong one for the
# family's own claims.
#
# ⚑⚑ THEY ASSERT THE VERDICT IS RENDERED, NOT THAT IT IS CLOSED. The live claims are the subject,
# and their wording is the arc's business rather than this suite's — a case pinning "closed" would
# fail the day someone phrases a decision as a question, reporting the corpus instead of the
# witness. What must hold is that the witness REACHES a verdict rather than raising.
def a_decision_claim_states_its_outcome(out: list[str]) -> int:
    """Check the decision witness reaches a verdict on the live worklist."""
    rows = list(claim_legibility.witness_decision("U1"))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append("selftest: the decision witness rendered no verdict")
        return 1
    return 0


def a_retraction_names_its_successor(out: list[str]) -> int:
    """Check the retraction witness reaches a verdict on the live worklist."""
    rows = list(claim_legibility.witness_retraction("R14-v1", "R14-v2"))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append("selftest: the retraction witness rendered no verdict")
        return 1
    return 0


_ARMS = (
    a_decision_claim_states_its_outcome,
    a_retraction_names_its_successor,
    a_decision_stating_an_outcome_closes,
    a_decision_phrased_as_a_question_opens,
    an_open_decision_carries_a_route,
    a_retraction_naming_its_successor_closes,
    a_retraction_without_a_successor_opens,
    an_unreadable_claim_opens_rather_than_raising,
    the_family_holds_one_member_per_predicate,
    the_familys_premises_all_resolve,
    the_question_tell_is_named_once,
)

# ⚑ THE TWO MEMBER ARMS CONTRIBUTE ONE CASE EACH, and the total MOVES by exactly two. That is
# growth, not a corrected sum: these assertions did not exist before. A total that HELD would have
# meant the arms were already counted under other names.
_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"claim-legibility selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"claim-legibility selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
