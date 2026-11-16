#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The claim-legibility family — a claim's own prose must carry what a reader needs.

⚑⚑⚑ THESE TWO ITEMS SHARE A READER AND A SHAPE, WHICH IS WHAT MAKES THEM A FAMILY. Both read one
claim's PROSE and assert a property of it: a decision item must state the outcome it would commit
to, and a retraction must name its successor. Neither inspects the tree; both inspect what the
worklist SAYS. Written apart, they were two witnesses re-deriving the same access.

⚑⚑ AND BOTH EXIST BECAUSE AN EARLIER FORM COULD NOT FAIL. `U1` was once `cmd = "true"`, which
provably cannot fail and therefore grades INDETERMINATE — the bucket reserved for *"falsifiability
is not demonstrated"*. The reasoning that produced it was *"a user decision is not debt, so it
must never block"*: correct about the GATE, and it silently made the CLAIM unfalsifiable, which is
a different and worse thing.

⚑ THE FIX IS THAT THE TWO REQUIREMENTS ARE SEPARABLE, and separating them is the whole design:
never block on a pending decision — so an UNDECIDED item is CLOSED; and stay falsifiable — so the
witness reads the decision RECORD, and a malformed or missing record is a real failure. What it
discriminates on is not *"has the user decided"* (they may legitimately not have) but *"is the
decision legible"*.

⚑⚑ THE PROSE COMES FROM `warrant_records` AND THE EXCEPTION FROM `warrant_bib` (gate-G209). The
engine half — `records` / `claim_of` / `tag` — imports paperkit at module scope and lives in its
own module; `WarrantError` stays with the config half precisely so a caller catching it need not
import the engine to name the exception it is catching. ⚑ THIS MODULE WAS THE LAST SITE FOUND, AND
IT WAS FOUND BY ASKING THE THIRD QUESTION: a census of `tag` and `records` reported the migration
complete, because `claim_of` is a third moved name and nobody had asked about it.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mikemol.witness import witness_family, witness_row
from mikemol.witness.warrant_bib import WarrantError

from substrate import warrant_records

if TYPE_CHECKING:
    from collections.abc import Iterator

# ⚑ A CLAIM PHRASED AS A QUESTION HAS NOTHING TO CHECK AGAINST LATER, and is how *pending* becomes
# permanent. Named once so the witness and its cases share one spelling of the tell.
QUESTION = "?"

FAMILY = witness_family.of(
    key="claim-legibility",
    apex="a claim's own prose carries what a later reader needs — the outcome a decision would "
    "commit to, and the successor a retraction was replaced by — so that recording the "
    "decision is a checkable event rather than a change of subject",
    subject="the prose of individual worklist claims",
    members=[
        witness_family.Member(
            name="a_decision_claim_states_its_outcome",
            claim="an earlier form of this was `cmd = true`, which provably cannot fail and so "
            "grades indeterminate. The reasoning — a user decision is not debt, so it must "
            "never block — was correct about the GATE and silently made the CLAIM "
            "unfalsifiable. A decision item whose prose is a question has nothing to check "
            "against later, which is how pending becomes permanent",
        ),
        witness_family.Member(
            name="a_retraction_names_its_successor",
            claim="retraction is VERSIONED KEYS, not a growing section: at scale a retract "
            "section becomes the document. A retraction that does not say what replaced it "
            "is a deletion wearing a correction's clothes",
        ),
    ],
)


def prose(key: str) -> tuple[str | None, str | None]:
    """Return one claim's prose, or say why it could not be read."""
    try:
        return warrant_records.claim_of(key), None
    except WarrantError as exc:
        return None, str(exc)


def witness_decision(key: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield the verdict for a decision claim stating the outcome it would commit to."""
    text, why = prose(key)
    if text is None:
        # ⚑ AN UNREADABLE CLAIM IS A FINDING ABOUT THE CLAIM, not a pass. The item cannot be
        # measured, and that is a verdict rather than an exception — a witness that raised would
        # take the whole roster down.
        yield witness_row.opened(key, f"the claim could not be read: {why}")
        return

    if QUESTION in text:
        yield witness_row.part(key, "claim prose", route="state the outcome deciding commits to")
        yield witness_row.opened(
            key,
            "the claim is phrased as a question; a decision item must state the outcome it "
            "would commit to, so that recording the decision is a checkable event",
        )
        return
    yield witness_row.closed(
        key,
        "the decision is legible and pending — not debt, and not blocking; the claim states "
        "what deciding would commit to",
    )


def witness_retraction(
    key: str, successor: str
) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield the verdict for a retracted claim naming what replaced it."""
    text, why = prose(key)
    if text is None:
        yield witness_row.opened(key, f"the claim could not be read: {why}")
        return

    if successor not in text:
        yield witness_row.part(key, successor, route=f"name {successor} in the claim's own prose")
        yield witness_row.opened(
            key,
            f"{key} does not name its successor in its own prose; a retraction that does "
            f"not say what replaced it is a deletion wearing a correction's clothes",
        )
        return
    yield witness_row.closed(key, f"{key} names {successor} as its corrector")
