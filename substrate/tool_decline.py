#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""A reading CONSIDERED AND REFUSED, plus the three predicates that classify a flag's silence.

⚑⚑⚑ AN ABSENT ARGUMENT READS AS AN ABSENT OBJECTION. A census reports what it FOUND and what it
COULD NOT READ; neither can say *"this was considered and rejected, here is why"*. So a rejected
reading leaves no trace, becomes indistinguishable from one nobody thought of, and the next reader
either re-derives the question or ADOPTS the rejected reading because nothing contradicts it.
MEASURED 2026-08-19: an over-broad claim was relayed into a peer's tree and travelled two messages
because nothing recorded that it had already been refused.

⚑⚑ THE CHECK MUST ASSERT THE NEGATION, NOT COMMENT THE REFUSAL. A comment saying *"we considered
and rejected the general reading"* governs only the reader already looking at it. A check that
FAILS IF THE REJECTED READING BECOMES TRUE governs the claim. `check=None` is legal and means
UNGUARDED — reported rather than hidden, because a decline nothing checks is a comment with a
record round it.

⚑ SAME FAMILY AS `Convention` AND gcalculus `farm.py`'s `Arm`, and the load-bearing field is the
same one: a FALSIFIABLE DISCRIMINATOR. An `Arm` declares the message its mutation must provoke; a
`Convention` declares the invoker that makes a flag shared; a `Decline` declares the check that
would go red if the refusal lapsed. All three make their own VACUITY detectable — an `Arm` that
stops biting is VACUOUS, a `Convention` whose invoker stops invoking is STALE, a `Decline` whose
check no longer runs is UNGUARDED.

⚑ A DECLINE IS NOT A TODO. A missing mode is WORK; a declined reading is neither work nor finding
— it is a SETTLED question, and the record exists so it stays settled.

⚑⚑ AND THE THREE PREDICATES BELOW EXIST BECAUSE A FLAG'S SILENCE HAS KINDS. A flag a tool
dispatches but never mentions is INVISIBLE debt; one it mentions while another tool declares it is
a CITATION and the remedy rather than the defect; one marked as a deliberate failing fixture is
neither. Collapsing any pair drives a paydown that makes the corpus worse while making a number
greener.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers), 2,196 findings, refused whole by the
per-file gate. The cut continues until the dispatch moves out and the original is retired.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from substrate.tool_census import Tool

# The comment a tool writes at a dispatch site to declare a deliberate failing fixture.
FIXTURE_MARK = "toolmodes:fixture"

# What a citation's owner attribution is worth. ⚑ THE `?` IS NOT HEDGING — it says the citing line
# names no owner, so the reader resolves it and the census does not pretend to.
WITNESSED = "CITATION"
INFERRED = "CITATION?"


@dataclass(frozen=True, slots=True)
class Decline:
    """One claim considered and refused, with the check that fails if the refusal stops holding.

    Fields deliberately mirror `Convention(flag, invoker, contract, why)`:

      claim     the REJECTED reading, stated as temptingly as someone would actually state it
      instead   what is true in its place, one line
      check     the command whose FAILURE would mean the refusal has lapsed — the discriminator.
                `None` is legal and means UNGUARDED, which the census REPORTS rather than hides.
      why       the argument, and what a reader loses by adopting the rejected reading
    """

    claim: str
    instead: str
    check: str | None
    why: str

    @property
    def guarded(self) -> bool:
        """Report whether anything would go red if this refusal lapsed."""
        return bool(self.check)


@dataclass(frozen=True, slots=True)
class Citation:
    """A flag one tool NAMES and another DECLARES — a cross-reference, not a gap."""

    kind: str
    owners: tuple[str, ...]

    @property
    def witnessed(self) -> bool:
        """Report whether the citing line named the owner, rather than the owner being inferred."""
        return self.kind == WITNESSED


def fixtures(tool: Tool) -> frozenset[str]:
    """Return the flags this tool DECLARED as deliberate failing fixtures, not capabilities.

    ⚑ A SET RATHER THAN A FILTER APPLIED UPSTREAM, because the two consumers want different
    things. A divergence report must SHOW the fixtures — an invisible exemption is the rot —
    while a ratchet must not COUNT them. Returning the class lets each decide.

    ⚑⚑ A FIXTURE STILL HAS TO BE DISPATCHED. The mark is checked against what the tool ACCEPTS,
    so marking a flag it does not dispatch declares nothing: a comment cannot mint an exemption
    for a mode that is not there, which keeps the marker from pre-emptively silencing future debt.
    """
    if FIXTURE_MARK not in tool.source:
        return frozenset()
    return frozenset(
        flag
        for line in tool.source.splitlines()
        if FIXTURE_MARK in line
        for flag in tool.accepted
        if flag in line
    )


def citations(rows: tuple[Tool, ...]) -> dict[tuple[str, str], Citation]:
    """Return `{(relpath, flag): Citation}` — a flag a tool names and another tool declares.

    ⚑⚑ A CITATION IS A THIRD THING, AND COLLAPSING IT INTO EITHER NEIGHBOUR IS THE DEFECT. One
    tool prints *"contract is preserved — verified by `agda_defs --telescope`"*; `--telescope` is
    DECLARED, by `agda_defs` — so booking it against the citing tool as *"declared by NO tool"* is
    an ATTRIBUTION error, not a detection one. The mode exists; the reader was pointed at the
    wrong owner.

    ⚑⚑⚑ AND THE STAKES ARE THE INVERSE OF A DEFECT. The standing rule is that tools must point at
    a document that points back at all of them, so a sentence naming a sibling's mode is the
    REMEDY. Scoring it as debt would drive a paydown that DELETES cross-references — turning the
    corpus worse while turning a number greener.

    ⚑ ONE BODY BECAUSE TWO ARMS DISAGREED ABOUT ONE FLAG IN ONE RUN. A gap report already
    resolved this against the global index while a find report's prose arm did not consult it, so
    the same invocation reported that a tool declares `--telescope` AND that no tool declares it.
    The discriminator was already in the tree; this is it lifted to one place.

    ⚑⚑ TWO KINDS, BECAUSE ONE IS UNDECIDABLE AND SAYING SO IS THE POINT. A citing line that also
    names a declaring tool WITNESSES the owner; a bare flag in a sentence whose subject is the
    tool is genuinely undecidable from the flag's neighbourhood, and a "tool name near flag"
    heuristic silently guesses. The second kind is reported with EVERY declarer rather than one.
    """
    declared: dict[str, set[str]] = {}
    for tool in rows:
        for mode in tool.modes:
            declared.setdefault(mode, set()).add(tool.relpath)

    out: dict[tuple[str, str], Citation] = {}
    for tool in rows:
        lines = tool.source.splitlines()
        for flag in sorted(tool.mentioned):
            owners = tuple(sorted(declared.get(flag, set()) - {tool.relpath}))
            if not owners:
                continue
            stems = {owner.rsplit("/", 1)[-1].removesuffix(".py") for owner in owners}
            witnessed = any(flag in line and any(stem in line for stem in stems) for line in lines)
            out[(tool.relpath, flag)] = Citation(
                kind=WITNESSED if witnessed else INFERRED, owners=owners
            )
    return out


def invisible(tool: Tool, universal: frozenset[str]) -> tuple[str, ...]:
    """Return the flags a tool dispatches that NO READER CAN SEE — the sharp class.

    Argv-anchored, and absent from every usage line AND the prose AND the bracketed options: a
    capability that exists and is unreachable through the documented interface. That is exactly
    how one tool's modes became invisible, since its bare run prints a selftest.

    ⚑ A BRACKETED OPTION IS DOCUMENTED. `--closure <Mod> [--prefix <Pfx>]` declares `--prefix` on
    the usage line; it is correctly not a MODE, and reporting it as an undocumented one would send
    a reader to document what the tool already documents.

    ⚑ ONE BODY, TWO CONSUMERS, AND THAT IS THE POINT. A divergence report names this class and a
    sync publishes it into the skill. Two copies would let the gate's number and the document's
    number disagree while both were "right" — the `agda_files()`-had-four-bodies class one layer
    up.
    """
    return tuple(
        sorted(
            flag
            for flag in tool.accepted
            if flag not in tool.modes
            and flag not in tool.mentioned
            and flag not in tool.options
            and flag not in universal
        )
    )
