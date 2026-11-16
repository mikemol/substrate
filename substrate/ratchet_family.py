#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The ratchet family — seven items whose figure IS a gate's added-key count.

⚑⚑⚑ ONE BODY, N ITEMS, AND THE BODY ALREADY EXISTED. `ratchet_witness.witness(key, gate, figure)`
is the shared implementation; what was missing is a DECLARATION of the roster, so nothing could
read which items ride on it without running them. The origin's docstring states the principle —
*"each of these items says the same thing about a different gate, so writing N witnesses would be
N chances to drift"* — while spelling the membership only as N separate call sites.

⚑⚑ AND THE ORIGIN'S OWN COUNT OF ITS MEMBERS WAS STALE BY TWO. Its docstring names six items
(`A5`, `G1`, `G6`, `R8`, `R2-SWEEP`, `R9-residue`); the tree has EIGHT call sites, adding `S1` and
`T12-rederive`. A membership written in prose beside the code that implements it drifts silently
in exactly this direction — the prose is the artifact no gate re-derives.

⚑ `A5` IS ABSENT FROM THIS ROSTER DELIBERATELY. It has its own family (`ban_witness`), because a
ban key partitions by DIRECTIVE and the aggregate must cover kinds no sub-item names — a structure
the plain added-key count cannot express. Seven ride here; the eighth graduated.

⚑⚑ THE FIGURE COMES FROM THE CLAIM, NOT FROM THE GATE. `warrant_bib.tag` reads the `[name=N]` the
item declares, and the census supplies the truth; the item OPENS when they disagree. That is the
mechanism that would have caught a ban item being sized against 66 when the tree said 216 — a
witness that took the gate's own number would compare a value to itself.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from mikemol.witness import witness_family, witness_row

from substrate import ratchet_census, ratchet_witness

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(frozen=True, slots=True)
class Item:
    """One ratchet item: the worklist key, its gate, and the figure its claim declares."""

    key: str
    gate: str
    figure: str


# ⚑ THE ROSTER, DECLARED ONCE. Read from here rather than from eight call sites, so a member
# cannot be added to the tree while the family's own account of itself stays behind.
ITEMS = (
    Item("R8", "check_public_ratchet", "public-added"),
    Item("G1", "check_claims", "claims-added"),
    Item("G6", "check_cap_ratchet", "cap-added"),
    Item("R2-SWEEP", "check_sumtype_ratchet", "sumtype-added"),
    # ⚑⚑⚑ THE ONE MIGRATED MEMBER, AND IT IS SPELLED DOTTED FOR A REASON THE OPPOSITE OF F23's.
    # `gate_module` resolves a BARE stem against `GATE_DIR` (`scripts/`) by construction, so a
    # bare `private_gate` reports `ModuleNotFoundError` for a module that is present — measured,
    # not reasoned. A package module resolves by ORDINARY import, which is the `_by_name` arm,
    # so the dotted name is the spelling that reaches it.
    #
    # ⚑⚑ SO THE TWO SPELLINGS ARE NOT INTERCHANGEABLE AND NEITHER IS UNIVERSALLY RIGHT: bare
    # reaches `scripts/` and arms `sibling_finder`; dotted reaches an installed package. F23 was
    # a dotted name applied to a scripts-resident gate; this is the mirror image, and writing
    # the comment BEFORE the measurement got it backwards once already.
    Item("R9-residue", "substrate.private_census", "private-added"),
    Item("S1", "check_snapshot_guard", "snapshot-added"),
    Item("T12-rederive", "check_rederive_ratchet", "rederive-added"),
)

FAMILY = witness_family.of(
    key="ratchet",
    apex="every ratchet gate is at its recorded baseline, and each item's claim carries the "
    "figure the census must agree with — so a population that grew is refused rather than "
    "re-recorded",
    subject="the ratchet gates whose added-key count is a worklist item's figure",
    members=[
        witness_family.Member(
            name="the_public_re_export_residue_is_paid_down",
            claim="the leaf-side `public` re-export residue: a wholesale re-export in a new "
            "module is refused outright rather than ratcheted",
        ),
        witness_family.Member(
            name="no_prose_claim_is_falsified_by_the_tree",
            claim="the gate where a recorded finding goes to die honestly — it once refused on "
            "the very claim a prior fix had corrected, because the arc's own rewires moved "
            "the count again",
        ),
        witness_family.Member(
            name="no_module_elaborates_over_the_cap",
            claim="its baseline is a 0-byte file, so every key reads as added: this reports a "
            "LEVEL, not a delta — the honest reading, and the reason the item cannot be "
            "closed by re-recording",
        ),
        witness_family.Member(
            name="no_type_is_declared_in_both_a_parent_and_its_leaf",
            claim="a sumtype key counting BOTH the parent and the leaf is the signature of a "
            "split whose parent was never retired — the rewrite stopped one layer short of "
            "its own base",
        ),
        witness_family.Member(
            name="private_helpers_are_extracted_not_merely_hidden",
            claim="the paydown is EXTRACTING the helper into its own file, never deleting the "
            "keyword and leaving the definition — at one-definition-per-file there is no "
            "surface left to narrow",
        ),
        witness_family.Member(
            name="every_in_place_editor_is_snapshot_armed",
            claim="a census verifies PRESENCE, never behaviour: five tools once read as armed "
            "while snapshotting nothing, and a rewrite left 33 files unrecoverable",
        ),
        witness_family.Member(
            name="no_tool_re_derives_a_shared_authority",
            claim="a shared NAME is not a shared authority, and the re-derivation census is what "
            "distinguishes a delegator from a rival",
        ),
    ],
)


def item(key: str) -> Item | None:
    """Return the roster entry for a worklist key, or None when it rides no ratchet."""
    for got in ITEMS:
        if got.key == key:
            return got
    return None


def unmeasurable() -> tuple[tuple[str, str], ...]:
    """Return `(gate, why)` for every roster gate whose census cannot be read.

    ⚑⚑ AN UNMEASURABLE CENSUS IS NOT A CLEAN ONE, and this reader exists so the distinction is
    visible BEFORE a verdict is rendered. MEASURED: four of seven gates fail with
    `ModuleNotFoundError` on a SIBLING (`ratchet`, `buildtime`) — they are written to run as
    scripts, where CPython puts their directory on the path, and importing them as modules is a
    different resolution. **That is a fact about the invocation, not about the gate**, and every
    one of the four is present on disk.

    ⚑⚑⚑ AND THE SPELLING WAS DOING IT — the census was asked for `scripts.<gate>`, and that
    prefix SELECTS A DIFFERENT RESOLUTION. `scripts/` is a package (it has an `__init__.py`), so
    the dotted name imports ordinarily via `_by_name`, where a bare `import ratchet` inside the
    gate has nothing to resolve against. The BARE stem fails that path and falls through to
    `gate_module._by_location`, which arms `sibling_finder` over the gate directory — so the same
    gate reads UNMEASURABLE under one spelling and reports 75-added-of-490 under the other.

    ⚑⚑ TWO SPELLINGS, ONE CAPABILITY, DIFFERENT ANSWERS — the `--calls emit` shape, and it cost
    a wrong diagnosis in the turn that fixed it: the prefix was read as a dead path building
    `scripts/scripts.<gate>.py`, which would have been a harmless no-op to remove. One call to
    `ratchet_census_show` with the bare name settled it. The prefix is not redundant, it is
    ACTIVE, and dropping it is what re-arms the finder.
    """
    out: list[tuple[str, str]] = []
    for got in ITEMS:
        census, why = ratchet_census.census(got.gate)
        if census is None:
            out.append((got.gate, why or "no reason given"))
    return tuple(out)


def witness(key: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield the rows for one ratchet item, dispatching on the roster.

    ⚑ THE ROSTER DECIDES, NOT THE CALLER. A caller passing a gate name directly could ask about a
    gate no item claims, and the verdict would then answer for a population nobody is accountable
    for — the coverage defect the ban family found at the aggregate level.
    """
    got = item(key)
    if got is None:
        yield witness_row.opened(
            key,
            f"{key!r} rides no ratchet in this family "
            f"({', '.join(i.key for i in ITEMS)}) — the claim is UNMEASURED, not satisfied",
        )
        return
    yield from ratchet_witness.witness(got.key, got.gate, got.figure)


def render() -> str:
    """Return the roster and which gates can currently be measured."""
    blocked = dict(unmeasurable())
    lines = [f"  {len(ITEMS)} ratchet item(s)"]
    lines.extend(
        f"    {got.key:<14} {got.gate:<26} "
        + (f"⚑ UNMEASURABLE — {blocked[got.gate]}" if got.gate in blocked else "measurable")
        for got in ITEMS
    )
    lines.append(f"  {len(ITEMS) - len(blocked)} of {len(ITEMS)} measurable")
    return "\n".join(lines) + "\n"


# ⚑ A CLI, BECAUSE THE ALTERNATIVE WAS AN INLINE SCRIPT AND THE HOOK REFUSED IT — correctly. A
# `python3 -c` reading this roster is judgement living in a turn: it evaporates, and the next
# reader re-derives it differently. A mode is the same read, kept.
if __name__ == "__main__":
    import sys

    sys.stdout.write(render())
    sys.exit(0)
