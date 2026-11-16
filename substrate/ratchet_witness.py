#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""One body, N items — a witness whose figure IS a ratchet gate's added-key count.

⚑⚑ ONE IMPLEMENTATION, SIX ITEMS, AND THAT IS THE WHOLE ARGUMENT. Each of these items says the
same thing about a different gate — *"this census holds N keys the baseline does not"* — so
writing six witnesses would be six chances to drift. The item's claim carries the figure as a
`[<name>=N]` tag; the gate supplies the truth; the anchor refuses when they disagree.

⚑⚑⚑ THAT ANCHOR IS WHAT WOULD HAVE CAUGHT A REAL MISMATCH: an item sized against 66 while the
tree held 216. A witness that reports only the gate's number cannot be wrong about the claim,
because it never reads it — which is exactly the failure mode of a figure nobody reconciles.

⚑⚑ THE SHAPE RIDES WITH THE COUNT, and that is not decoration. Handed *"216 added"* a reader
classifies it in prose — *"a real population, not the 4-site kind"* — and that judgement decides
whether the work is a SWEEP or a per-site grind, i.e. which tool applies. A tally cannot answer
it; the partition can, and it is a read of keys already in hand. **A count is not a shape.**

⚑⚑ AND THE ROWS ARE THE ADDED KEYS THEMSELVES, WHICH WERE IN HAND ALL ALONG. The prior body
printed a four-key sample into a sentence and side-channelled the total as a scalar, so the
ordering could rank these items only by a number whose population it could not see. Every one of
the six was `size` with NO parts.

⚑ AN UNMEASURABLE CENSUS IS OPEN, NOT CLEAN. A gate that cannot be read has an unknown state,
and reporting it as at-baseline would bank a green verdict nothing measured.

⚑⚑⚑ THE FIGURE COMES FROM `warrant_records` AND THE EXCEPTION FROM `warrant_bib`, AND THAT SPLIT
IS DELIBERATE RATHER THAN UNTIDY (gate-G209). The engine half — `records` / `claim_of` / `tag` —
imports paperkit at module scope, so it lives in its own module; `WarrantError` stays with the
config half precisely so **a caller catching it need not import the engine to name the exception
it is catching**. Reading both from one module is what made `scratch/bibstruct.py` unreachable in
every mode without a paperkit venv, and collapsing them back here would re-close that hole.

⚑⚑⚑ THE GATE IS NAMED BARE, NOT `scripts.<gate>`, AND THE PREFIX WAS A LIVE DEFECT. `gate_module`
runs a SIBLING FINDER scoped to `scripts/` so a gate importing its siblings by bare name resolves —
but only on its `_by_location` fallback, which a DOTTED name never reaches, because ordinary
package import succeeds first and the finder never runs. MEASURED: `ratchet_census_show
check_public_ratchet` reads OVER at 75 of 490 while `ratchet_census_show
scripts.check_public_ratchet` reads `ModuleNotFoundError: No module named 'ratchet'` — **the same
gate, two verdicts, decided by the caller's spelling.**

⚑⚑ SO THE GATE WAS NEVER BROKEN AND NEITHER WAS ITS IMPORT. Three ticks carried this as a
packaging blocker needing `scripts/` drained, on the theory that a bare `import ratchet` cannot
resolve for an installed wheel. That is true of an ADOPTER and false of this caller, which has the
finder: `check_cap_ratchet` imports `ratchet` AND `buildtime` bare and censuses fine. A reading
that is right about one consumer and wrong about another is the kind a count cannot catch.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split). The figure layer beneath it —
`gate_module`, `ratchet_census`, `key_spec`, `kind_partition` — exists for this.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mikemol.witness import witness_row
from mikemol.witness.warrant_bib import WarrantError

from substrate import kind_partition, ratchet_census, warrant_records

if TYPE_CHECKING:
    from collections.abc import Iterator

# How many added keys to name in the verdict sentence before the partition speaks for the rest.
_SAMPLE = 4


def route(gate: str) -> str:
    """Return the command that enumerates this gate's census.

    ⚑ THE ROUTE IS THE GATE'S OWN LISTING, NOT PROSE. Every ratchet gate grew a `--list` mode
    precisely so a census could be ENUMERATED; naming it on each row makes the row actionable
    instead of descriptive.
    """
    return f"python3 scripts/{gate}.py --list"


def witness(key: str, gate: str, figure: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield one part per added key, then the verdict — the shared body for a ratchet item.

    `key` is the worklist item; `gate` is the gate module; `figure` is the `[name=N]` tag in the
    item's claim that this census must agree with.
    """
    census, why = ratchet_census.census(gate)
    if census is None:
        yield witness_row.opened(
            key, f"CANNOT MEASURE {gate} ({why}) — an unmeasurable census is not a clean one"
        )
        return

    try:
        want = warrant_records.tag(key, figure)
    except WarrantError as exc:
        # ⚑ AN UNANCHORED CLAIM IS OPEN, NOT ASSUMED-CORRECT. Without a figure in the claim
        # there is nothing to reconcile the census against, and defaulting to the census's own
        # number would make the check compare a value to itself.
        yield witness_row.opened(key, f"the claim carries no [{figure}=N] tag: {exc}")
        return

    for added in census.added:
        yield witness_row.part(key, added, route=route(gate))

    buckets, _why = kind_partition.kinds(gate)
    shape = f" — {kind_partition.render(buckets)}" if buckets else ""
    sample = ", ".join(census.added[:_SAMPLE]) or "none"

    if census.over != want:
        yield witness_row.opened(
            key,
            f"claim says {want} added; {gate} holds {census.over} of {census.held}"
            f"{shape} ({sample})",
        )
        return
    if census.over:
        yield witness_row.opened(
            key, f"{census.over} key(s) still added over baseline in {gate}{shape}: {sample}"
        )
        return
    yield witness_row.closed(key, f"{gate} is at baseline ({census.held} held)")
