#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report a claim's grounding: whether its declared premises are satisfied before it is read.

⚑⚑⚑ A `rests-on` EDGE IS AN ENFORCEABLE PRECONDITION, NOT A COMMENT. R12b declares
`rests-on = {CENSUS}` in the warrants bib AND calls the census check first, inheriting its failure
verbatim — so R12b cannot read green off a stale ledger. **Both prior figures for that item (113,
then 345) are void for exactly that reason**: they were measured against a census that had already
moved, and nothing in the number said so.

⚑⚑ THE DECLARATION AND THE ENFORCEMENT ARE TWO DIFFERENT ARTIFACTS, AND EITHER ALONE IS A GAP.
A bib edge nothing checks is documentation that drifts; a check no edge declares is a dependency
no reader can find. MEASURED: 9 of 45 entries declare `rests-on`, so most claims state no
grounding at all — which is a fact about what has been DECLARED, never a proof that the other 36
are ungrounded.

⚑ SO WHAT THIS REPORTS IS THE JOIN. For a claim: what it declares it rests on, which of those
premises are satisfied, and — the direction a per-claim reader cannot see — whether the premise
was checkable at all. An unsatisfiable premise and an unsatisfied one are different findings.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Protocol, cast

from substrate import scratch_module

# The tool that owns the warrants bib.
BIB = "bibstruct"

# The field declaring what a claim rests on.
RESTS_ON = "rests-on"


class Bib(Protocol):
    """The part of the bib reader this witness consults."""

    def entries(self, path: str | None = ...) -> dict[str, dict[str, str]]:
        """Return the parsed entries, keyed."""
        ...


@dataclass(frozen=True, slots=True)
class Premise:
    """One declared premise and whether it holds."""

    claim: str
    premise: str
    # None when the premise could not be evaluated at all.
    satisfied: bool | None
    why: str

    @property
    def checkable(self) -> bool:
        """Report whether the premise could be evaluated.

        ⚑ UNCHECKABLE IS NOT UNSATISFIED. A premise naming a claim nothing can decide leaves the
        grounding UNKNOWN, and reporting that as a failure blames the claim for a gap in the
        reader.
        """
        return self.satisfied is not None


def _split(raw: str) -> tuple[str, ...]:
    """Split a comma-separated edge field into its targets.

    ⚑ THE FIELD ARRIVES AS ONE STRING. `rests-on = {A, B}` is a single value, so a reader taking
    it whole treats `"A, B"` as one premise name that matches nothing — the same shape the edge
    re-split already had to fix once.
    """
    return tuple(part.strip() for part in raw.split(",") if part.strip())


def declared(api: Bib) -> dict[str, tuple[str, ...]]:
    """Read every claim's declared premises."""
    out: dict[str, tuple[str, ...]] = {}
    for key, fields in api.entries().items():
        raw = fields.get(RESTS_ON)
        if raw:
            out[key] = _split(raw)
    return out


def bib() -> tuple[Bib | None, str]:
    """Load the bib reader, narrowed to the one call this witness makes."""
    found, why = scratch_module.scratch_module(BIB)
    if found is None:
        return None, f"{BIB} will not load: {why}"
    return cast("Bib", found), ""


def grounding(
    claim: str,
    decide: dict[str, tuple[bool, str]] | None = None,
) -> tuple[tuple[Premise, ...], str]:
    """Report each declared premise of one claim, and whether it is satisfied.

    ⚑ THE DECIDER IS AN INPUT, NOT A LOOKUP INSIDE. A witness that resolved premises by calling
    other witnesses would run an arbitrary subgraph to answer one question — the loop the B3
    aggregate deliberately refuses. The caller supplies what it has already decided.
    """
    api, missing = bib()
    if api is None:
        return (), missing

    known = decide or {}
    edges = declared(api).get(claim)
    if edges is None:
        return (), f"{claim} declares no {RESTS_ON} — its grounding is UNDECLARED, not absent"

    out = []
    for premise in edges:
        verdict = known.get(premise)
        if verdict is None:
            out.append(
                Premise(
                    claim=claim,
                    premise=premise,
                    satisfied=None,
                    why="no verdict supplied — UNCHECKABLE, not failing",
                )
            )
        else:
            holds, why = verdict
            out.append(Premise(claim=claim, premise=premise, satisfied=holds, why=why))
    return tuple(out), ""


def blocked(rows: tuple[Premise, ...]) -> tuple[Premise, ...]:
    """Return the premises that are known NOT to hold.

    ⚑ ONLY THE DECIDED FAILURES. An unchecked premise is not evidence of a broken grounding, and
    folding it in here would make an unmeasured claim indistinguishable from a refuted one.
    """
    return tuple(row for row in rows if row.satisfied is False)


def render(claim: str, rows: tuple[Premise, ...], why: str = "") -> str:
    """Render the grounding, keeping undeclared and unchecked distinct from failing."""
    if why:
        return f"  {claim}: UNGROUNDED — {why}"
    if not rows:
        return f"  {claim}: no premise declared"

    out = [f"  {claim} rests on {len(rows)} premise(s):"]
    for row in rows:
        if row.satisfied is None:
            out.append(f"    ? {row.premise} — {row.why}")
        elif row.satisfied:
            out.append(f"    ✓ {row.premise} — {row.why}")
        else:
            out.append(f"    ⚑ {row.premise} — {row.why}")
    return "\n".join(out)


if __name__ == "__main__":
    _api, _missing = bib()
    if _api is None:
        sys.stdout.write(f"  UNREAD — {_missing}\n")
        sys.exit(0)
    _edges = declared(_api)
    sys.stdout.write(f"  {len(_edges)} claim(s) declare {RESTS_ON}\n")
    for _key, _targets in sorted(_edges.items()):
        sys.stdout.write(f"    {_key} → {', '.join(_targets)}\n")
    sys.exit(0)
