#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Bind each worklist key whose reader already emits worklist rows.

⚑⚑⚑ THREE ARITIES EXIST AND MEASURING THEM IS WHAT MADE THIS TABLE HONEST. `witness(key)`,
`witness(key, second)`, `witness(key, second, third)` — a family answering from the key alone, one
that needs one more value, one that needs two. A table typed to any single shape cannot hold the
others, and typing it loosely would erase the distinction a caller needs.

⚑⚑ THE SECOND ARGUMENT IS NOT ALWAYS A FIGURE, WHICH IS WHY THE FIELD IS NOT CALLED ONE. Most
readers take the `[name=N]` tag their claim must agree with; `witness_retraction` takes the
SUCCESSOR key a retraction must name. Same arity, different meaning — and a field named `figure`
holding a successor is a lie the type system cannot catch.

⚑⚑ AND A `--calls witness` CENSUS MISSED FOUR EMITTERS BECAUSE THEY ARE NAMED DIFFERENTLY.
`witness_library`, `witness_decision`, `witness_retraction` are row emitters; keying the census on
the exact name `witness` reported them absent, and I twice concluded their modules had no
entrypoint. **The census answered the question asked, not the one meant** — a fact about the
spelling reported as a fact about the module.

⚑ AND THESE READERS NEED NO ADAPTER, WHICH IS THE LINE BETWEEN THIS TABLE AND ITS SIBLING. The
census readers produce a RENDERING that `concept_rows` frames into parts and a verdict; these
produce the rows directly. Routing them through the adapter would re-derive a verdict they have
already reached.

⚑ A KEY WITH NO READER IS ABSENT, NOT STUBBED. An entry returning a plausible verdict would
report a measurement nobody took; an absent one reports UNBOUND, which is a fact about this table
and actionable as one.

⚑ EXTRACTED FOR ⟡roster-reduce: `catalog/library/concepts.py` binds keys to readers, and this is
the half that knows how each row-shaped reader is called.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from mikemol.witness import witness_row

from substrate import (
    ban_witness,
    claim_legibility,
    collision_witness,
    edge_witness,
    grade_witness,
    library_witness,
    premise_edge,
    ratchet_family,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


@dataclass(frozen=True, slots=True)
class Family:
    """One key, and how its row-emitting reader is called.

    ⚑ THE THREE ARITIES ARE FIELDS, NOT A UNION OF CALLABLES. A reader needing one extra value and
    one needing two differ in what the BINDING must supply, so stating the arguments is what lets
    one dispatch serve all three without a cast.

    ⚑⚑ `second` AND `third` ARE POSITIONAL NAMES, DELIBERATELY. They hold a figure for most
    readers and a successor key for one, so a name asserting either would be false at some row —
    what the record knows is the POSITION; what the value MEANS is the reader's.
    """

    # The reader answering from the key alone.
    keyed: Callable[[str], Iterator[witness_row.Part | witness_row.Verdict]] | None = None
    # The reader needing one more value.
    paired: Callable[[str, str], Iterator[witness_row.Part | witness_row.Verdict]] | None = None
    # The reader needing two more.
    tripled: Callable[[str, str, str], Iterator[witness_row.Part | witness_row.Verdict]] | None = (
        None
    )
    second: str = ""
    third: str = ""

    def rows(self, key: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
        """Yield this family's rows for one key."""
        if self.tripled is not None:
            yield from self.tripled(key, self.second, self.third)
            return
        if self.paired is not None:
            yield from self.paired(key, self.second)
            return
        if self.keyed is not None:
            yield from self.keyed(key)
            return
        yield witness_row.opened(
            key, f"{key!r} names a family with no reader — UNMEASURED, not satisfied"
        )


# The figure each single-reader family reconciles against. ⚑ NAMED HERE because the claim's tag
# is what the WITNESS must agree with, and a binding that guessed it would compare a value to
# itself.
_EDGE_FIGURE = "unresolvable-edges"
_GRADE_FIGURE = "ungraded-witnesses"
_BAN_FIGURE = "ban-keys-added"
_LIBRARY_FIGURE = "witness-library"

# The retraction whose claim must name what replaced it.
#
# ⚑⚑⚑ THE WORKLIST KEY AND THE BIB KEY ARE DIFFERENT, AND THE SUITE CAUGHT IT. Binding this to
# the worklist's `R14-legible` made the successor read empty — `bibstruct --mentions R14-legible`
# reports **no entry (have 45)**, because the warrant set carries `R14-v1`/`R14-v2`. The dispatch
# roster's own comment already recorded the split: *"R14/R14-legible live here while the bib
# carries R14-v1/R14-v2 — two hand-kept rosters, already disagreeing."*
#
# ⚑ SO THE READ IS KEYED ON THE BIB, and the worklist key is what the ROW is filed under. Reading
# a relation requires the name the relation is written in; reporting it requires the name the
# worklist knows. Conflating them is how the successor came back empty and would have reported a
# claim naming no successor — a finding about a key that does not exist.
_RETRACTED = "R14-legible"
_RETRACTED_BIB = "R14-v2"

# ⚑ THE SECTION THAT MAKES A CLAIM A RETRACTION. `rests-on` alone does NOT: an ordinary claim may
# declare a premise, and keying the retraction binding on that field bound `A5`, `B3` and `DEPS`
# and reported each as failing to name a successor — three sound claims turned into three false
# OPEN items. The rubric already says which claims retract; this reads that rather than guessing.
_RETRACT_SECTION = "retract"


def successor(key: str = _RETRACTED_BIB) -> str:
    """Return the key a retraction rests on, read from the bib.

    ⚑⚑ THE SUCCESSOR IS DECLARED, NOT TYPED HERE. `rests-on` already carries it in the warrant
    set, so a constant at this binding would be a second spelling of a relation the bib holds —
    and the two would disagree the first time either moved.

    ⚑ READ THROUGH `premise_edge.declared`, NOT A FOURTH ACCESSOR. That module already owns the
    `rests-on` read and splits its comma-joined targets; reaching for the field again here would
    be the rival implementation, and my first cut guessed a `warrant_bib.entry` that does not
    exist. An unreadable bib yields the empty string, which the reader reports as a claim naming
    no successor rather than as a pass.
    """
    api, why = premise_edge.bib()
    if api is None:
        del why
        return ""
    targets = premise_edge.declared(api).get(key, ())
    return targets[0] if targets else ""


def _ratchet() -> dict[str, Family]:
    """Bind every ratchet key to the family that owns the roster.

    ⚑ THE MODULE OWNS ITS MEMBERSHIP. Listing the keys here would put the roster in two places,
    and the two would disagree the first time a ratchet moved — the frozen-roster defect this arc
    kept finding.
    """
    return {got.key: Family(keyed=ratchet_family.witness) for got in ratchet_family.ITEMS}


def _ban() -> dict[str, Family]:
    """Bind every ban-family key to its shared dispatch."""
    keys = ("A5", "A5-as-reach", *(f"A5-{kind}" for kind in ban_witness.BUCKETS))
    return {key: Family(paired=ban_witness.witness, second=_BAN_FIGURE) for key in keys}


def _collisions() -> dict[str, Family]:
    """Bind each collision partition to its key and figure.

    ⚑⚑ THE MAPPING IS READ, NOT RESTATED. `collision_witness.KEYS` already says which key and
    figure each partition answers for — it is declared there so the witness cannot drift from the
    roster, and a copy here would be the second authority that drift needs.
    """
    return {
        key: Family(tripled=collision_witness.witness, second=figure, third=kind)
        for kind, (key, figure) in collision_witness.KEYS.items()
    }


def _retractions() -> dict[str, Family]:
    """Bind every retraction in the bib to the witness that checks it names its successor.

    ⚑⚑⚑ DERIVED FROM THE BIB, NOT NAMED HERE — and the two constants above record why. A single
    retraction was bound by a `_RETRACTED`/`_RETRACTED_BIB` pair, whose own comment already
    reported the hazard: *"R14/R14-legible live here while the bib carries R14-v1/R14-v2 — two
    hand-kept rosters, already disagreeing."* Binding a SECOND retraction against that pair would
    reproduce the defect the comment describes, and a seventh would reproduce it sevenfold.

    ⚑⚑ THE SHAPE IS `_ratchet()`'s, FIFTEEN LINES UP: *"the module owns its membership; listing
    the keys here would put the roster in two places."* A retraction is exactly a claim carrying
    `rests-on` — the justification edge IS the membership test — so `premise_edge.declared`
    already returns the roster, keyed, and no reader is added to find it.

    ⚑⚑⚑ THE MEMBERSHIP TEST IS THE `retract` SECTION, NOT THE PRESENCE OF `rests-on` — and the
    first cut got this wrong in the direction that MANUFACTURES FINDINGS. Keying on `rests-on`
    alone bound `A5`, `B3` and `DEPS`, ordinary claims that happen to declare a premise, and the
    retraction witness then reported each as *"does not name its successor — a deletion wearing a
    correction's clothes"*. **A claim with a premise is not a claim that retracts something**, and
    the wrong predicate turned three sound claims into three false OPEN items.

    ⚑ A RETRACTION WITH NO `rests-on` IS STILL NOT BOUND. That is the honest reading rather than
    an omission: `witness_retraction` checks the prose against a DECLARED successor, so a
    retraction whose justification is undeclared has nothing to check against, and binding it
    would ask the witness to verify a name the bib never states.
    """
    api, why = premise_edge.bib()
    if api is None:
        del why
        return {}
    premises = premise_edge.declared(api)
    out: dict[str, Family] = {}
    for key, fields in api.entries().items():
        # ⚑ NARROWED AT THE SEAM. A bib field read returns `Any`; comparing it to the section name
        # inline would carry that into the binding, which the type gate refuses — correctly, since
        # an untyped section makes every membership test silently permissive.
        section = str(fields.get("section", ""))
        targets = premises.get(key, ())
        if section == _RETRACT_SECTION and targets:
            out[key] = Family(paired=claim_legibility.witness_retraction, second=targets[0])
    return out


def families() -> dict[str, Family]:
    """Return every key this table answers, bound to its reader."""
    out: dict[str, Family] = {
        "T28-edges": Family(paired=edge_witness.witness, second=_EDGE_FIGURE),
        "T28-grade": Family(paired=grade_witness.witness, second=_GRADE_FIGURE),
        "T25-library": Family(paired=library_witness.witness_library, second=_LIBRARY_FIGURE),
        "U1": Family(keyed=claim_legibility.witness_decision),
        _RETRACTED: Family(paired=claim_legibility.witness_retraction, second=successor()),
    }
    out.update(_ratchet())
    out.update(_ban())
    out.update(_collisions())
    # ⚑ RETRACTIONS LAST, DELIBERATELY. The explicit `_RETRACTED` binding above is keyed on the
    # WORKLIST spelling and this derivation is keyed on the BIB spelling, so they do not collide —
    # and if a future retraction is ever bound both ways, the derived one wins, which is the half
    # that cannot go stale.
    out.update(_retractions())
    return out


def family(key: str) -> Family | None:
    """Return the binding for one key, or None when nothing answers it."""
    return families().get(key)


def bound_keys() -> tuple[str, ...]:
    """Return every key this table answers, sorted."""
    return tuple(sorted(families()))


def rows(key: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield the rows for one key, or nothing when no family answers it.

    ⚑ SILENCE HERE IS NOT A VERDICT. An unbound key is the library's to report, not this table's
    — putting the UNMEASURED verdict in both places would give one fact two voices.
    """
    found = family(key)
    if found is None:
        return
    yield from found.rows(key)
