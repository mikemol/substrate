#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The T28-edges family — every declared edge names targets a reader can actually resolve.

⚑⚑⚑ THE ITEM'S ORIGINAL QUESTION WAS RETIRED BY MEASUREMENT, AND THIS RECORDS THE REPLACEMENT.
`T28_EDGES` asked whether any entry carries an edge field the ENGINE DROPS. Measured on live:
none does. The corpus writes `from`, `rests-on`, `enables`; the engine carries `from`, `rests-on`,
`reads`, `consumes`; and `enables` is DECLARED in `catalog/worklist/paper.toml` as a consumer
field, so it is carried rather than dropped. **The item as posed can only ever report zero.**

⚑⚑ THE LIVE DEFECT IS ONE LAYER IN, AND THE OWNING DOCUMENT ALREADY NAMES IT. A declared consumer
field joins `_SCALAR`, not `_LIST` — so `enables = {A, B}` reaches a consumer as the STRING
`'A, B'`, and `paper.toml` says outright: *"Any consumer MUST re-split."* A consumer that does not
does NOT crash; it reads ONE target named `"A, B"`, matching no entry. A multi-target edge becomes
a single dangling one, the count stays plausible, and only the membership is wrong.

⚑ SO THE FAMILY ASKS: does every declared edge resolve? Each member is one entry, and the parts a
member yields are the unresolvable targets it names — which is a fact a reader can act on, unlike
a roster comparison that agrees by construction.

⚑ THE FAMILY IS PARAMETRIC OVER ITS MEMBERS, WHICH IS THE `_ARMS` SHAPE MADE EXPLICIT. One body,
N members, each carrying its own name and its own prose; the apex states why the family exists and
each member states what it establishes. `parts()` is the parameterized body and `MEMBERS` is the
roster — so adding an entry to the corpus adds a member without touching the body.

⚑⚑ THIS MODULE READS BOTH HALVES OF THE gate-G209 SPLIT, AND THE DIVISION IS THE POINT. `BIB` and
`WarrantError` come from `warrant_bib`, the ENGINE-FREE half — `WarrantError` stays there
deliberately so a caller catching it need not import paperkit. `tag` comes from `warrant_records`,
which imports the engine at module scope. ⚑ A WILDCARD `attr_reads warrant_bib.*` MIXES THE TWO
and reads as though every name should move; naming the attribute is what separates the reads that
must move from the ones that must not.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), on `raw_bib` + `edge_split`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from mikemol.witness import raw_bib, witness_family, witness_row
from mikemol.witness.warrant_bib import WarrantError

from substrate import (
    edge_split,
    engine_edges,
    warrant_bib,
    warrant_records,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

# ⚑⚑ THE FAMILY, DECLARED — the first instance of `witness_family` on a family that already
# existed by convention. The apex states what having the family establishes; `subject` names what
# it is parameterized over, which is why adding a corpus entry adds a member without an edit here.
#
# ⚑ THE MEMBERS ARE THE PROPERTIES, NOT THE CORPUS ENTRIES. A first cut listed one member per
# entry, which made the roster a copy of the bib and the apex a count. The family is
# parameterized OVER entries; what it CLAIMS is these two facts about every one of them.
FAMILY = witness_family.of(
    key="T28-edges",
    apex="every declared edge names a target a reader can resolve — after the re-split a "
    "declared consumer field requires",
    subject="entries in the warrants bib that carry an edge field",
    members=[
        witness_family.Member(
            name="a_multi_target_declared_field_resolves_every_target",
            claim="a declared consumer field arrives as the STRING 'A, B', so a consumer that "
            "does not re-split resolves ONE target named 'A, B' — matching no entry, "
            "raising nothing, and blaming the entry for a defect in the reader",
        ),
        witness_family.Member(
            name="a_dangling_target_is_reported",
            claim="the positive control: a target no entry defines IS named, so the family "
            "discriminates rather than reporting clean by construction",
            premises=("a_multi_target_declared_field_resolves_every_target",),
        ),
    ],
)


@dataclass(frozen=True, slots=True)
class Unresolved:
    """One entry's edge naming a target no entry defines."""

    entry: str
    field: str
    target: str

    @property
    def route(self) -> str:
        """Return the repair a reader should make."""
        return f"define {self.target}, or correct the {self.field} target"


def edge_fields() -> tuple[str, ...]:
    """Return every field either reader treats as an edge.

    ⚑ THE UNION, NOT THE ENGINE'S ALONE. `enables` is a declared consumer field — carried but not
    in `_LIST` — so a family reading only the engine's roster would skip the very field whose
    re-split is the defect this module exists for.
    """
    seen: list[str] = []
    for field in (*raw_bib.EDGE_FIELDS, *engine_edges.edge_fields()):
        if field not in seen:
            seen.append(field)
    return tuple(seen)


def parts(corpus: raw_bib.Corpus) -> tuple[Unresolved, ...]:
    """Return every edge target that no entry in `corpus` defines.

    ⚑⚑ THE TARGETS ARE RE-SPLIT BEFORE RESOLUTION, which is the whole point. Without it a
    two-target `enables` yields one target named `"A, B"` — dangling by construction, and
    reported as a defect in the ENTRY rather than in the reader.
    """
    known = set(corpus.entries)
    out: list[Unresolved] = []
    for entry, fields in sorted(corpus.entries.items()):
        for field, targets in sorted(edge_split.edges(fields, edge_fields()).items()):
            out.extend(
                Unresolved(entry=entry, field=field, target=target)
                for target in targets
                if target not in known
            )
    return tuple(out)


def members(corpus: raw_bib.Corpus) -> tuple[str, ...]:
    """Return the family's members — the entries carrying at least one edge.

    ⚑ AN ENTRY WITH NO EDGE IS NOT A MEMBER, rather than a member that trivially holds. A family
    whose every non-participant passes reports a denominator that measures nothing.
    """
    fields = edge_fields()
    return tuple(
        entry
        for entry, carried in sorted(corpus.entries.items())
        if edge_split.edges(carried, fields)
    )


def witness(key: str, figure: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield one part per unresolvable edge target, then the verdict."""
    try:
        corpus = raw_bib.read(warrant_bib.BIB)
    except raw_bib.BibError as exc:
        yield witness_row.opened(key, f"the bib could not be read: {exc}")
        return

    found = parts(corpus)
    roster = members(corpus)

    try:
        want = warrant_records.tag(key, figure)
    except WarrantError as exc:
        yield witness_row.opened(key, f"the claim carries no [{figure}=N] tag: {exc}")
        return

    for row in found:
        yield witness_row.part(key, f"{row.entry}.{row.field} -> {row.target}", route=row.route)

    if not roster:
        # ⚑ AN EMPTY FAMILY IS UNMEASURED, NOT SATISFIED. No entry carrying an edge means the
        # predicate had nothing to discriminate, and a green verdict there is a fact about the
        # corpus read, not about the edges.
        yield witness_row.opened(
            key, "no entry carries an edge field — the claim is UNMEASURED, not satisfied"
        )
        return

    if len(found) != want:
        yield witness_row.opened(
            key,
            f"claim says {want}; {len(found)} edge target(s) over {len(roster)} entr(ies) "
            f"resolve to nothing: "
            f"{', '.join(f'{r.entry}.{r.field}->{r.target}' for r in found) or 'none'}",
        )
        return
    if found:
        yield witness_row.opened(key, f"{len(found)} edge target(s) resolve to nothing")
        return
    yield witness_row.closed(
        key, f"every edge target across {len(roster)} entr(ies) resolves to a defined entry"
    )
