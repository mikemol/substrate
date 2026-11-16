#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which suites owe a tenant declaration — REACHES-A-STORE against DECLARES-A-TENANT.

⚑⚑ A 2x2, NOT A LIST. `OWED` is reaches-and-does-not-declare (a suite that will `sys.exit(2)`
under ⟡tenant-mandatory); `STRAY` is declares-and-does-not-reach, which is what makes the
declaration FALSIFIABLE rather than decorative. A census that only reported the first would
let a wrong declaration sit forever.

⚑⚑⚑ AND THE `if-it-runs` ROWS ARE ADJUDICATED BY A JOIN, NOT BY HAND (⟡rulings-deterministic).
Seven rows reach a store only through a DEFERRED edge, and each carried a hand-written ruling
in a table keyed on filename. The operator's read was that this would need replacing with
something deterministic — and it does, but the deterministic thing already existed unjoined:

    import_edges  answers  *what does importing this execute*     (misses deferred calls)
    store_calls   answers  *does this file name a store-opener*   (over-reports by name)

The hand rulings asked exactly *"does the executed path reach `store.tenant` or a live
connect"* — one hop past what import-reach can show, and precisely what the CALL lens sees.
Two decorrelated instruments existed; nothing joined them on the rows where they disagree.

⚑ THE JOIN IS A CANDIDATE, NOT A VERDICT, AND THAT DISTINCTION SURVIVES. `store_calls` is
name-keyed and cannot resolve which `connect` is the store's without importing the module —
which is what the subprocess design exists to avoid. So a joined row says *this file reaches a
store through a deferred edge AND names a store-opener*, which is strictly more than either
lens alone and still short of proof. What it replaces is a ruling nobody can re-derive; what it
does not replace is a reader's judgement on the residue.

⚑ WHAT NEITHER LENS SEES: a raw driver call that names none of these — measured on
`query_defs._cost_connect`, an inlined `sandbox_connect(...) if ... else connect(...)` whose
tenant was unsayable. Coverage is the UNION of blind spots, and this reports that union rather
than claiming to close it.
"""

from __future__ import annotations

from dataclasses import dataclass

from substrate import store_calls, store_reach, tenant_pragma


@dataclass(frozen=True, slots=True)
class Row:
    """One suite's tenant standing, from both lenses.

    ⚑ BOTH LENSES ARE CARRIED, NEVER REDUCED TO ONE FLAG. A row where they disagree is the
    finding; collapsing it to a verdict would delete the only thing worth reading.
    """

    label: str
    declared: str | None
    reaches: bool
    via: tuple[str, ...]
    deferred_only: bool
    opens: frozenset[str]

    @property
    def verdict(self) -> str:
        """Classify this row: owed, stray, if-it-runs, declared, or clear."""
        if self.deferred_only:
            # ⚑ THE JOIN. A deferred-only reacher that also NAMES a store-opener is the row
            # the hand rulings called OWED-UNSTATABLE; one that names none is `not-owed`.
            return "if-it-runs/opens" if self.opens else "if-it-runs/inert"
        if self.reaches and not self.declared:
            return "OWED"
        if self.declared and not self.reaches:
            return "STRAY"
        if self.declared:
            return "declared"
        return "clear"


def opens_along(via: tuple[str, ...], index: dict[str, str], path: str) -> frozenset[str]:
    """Return the store-opening names mentioned ANYWHERE ON the reaching route.

    ⚑⚑⚑ THE CALL LENS MUST BE TRANSITIVE BECAUSE REACH IS, AND THE FIRST CUT WAS NOT.
    MEASURED on the live tree: joining a per-FILE call census against a transitive reach
    disagreed with the hand ruling for `pycodemod.py` — hand `OWED-UNSTATABLE`, join
    `if-it-runs/inert`. The hand ruling was right and the join was wrong, for a reason its own
    text states: the connect is in `_pycodemod_selftest.py`, a DIFFERENT FILE the suite
    invokes. Asking only the entry file whether it names an opener answers about the wrong
    module.

    ⚑ SO THE ROUTE IS THE POPULATION. `via` already names every hop the reach walk crossed, so
    the opener census follows the same path rather than a second one — which keeps the two
    lenses decorrelated in WHAT they look for while agreeing on WHERE.

    ⚑ AND THE SIX AGREEMENTS WERE NOT EVIDENCE THE JOIN WAS SOUND. Six rows agreed under the
    per-file form and one did not; the six agreed because their openers happen to be in the
    entry file. A disagreement in ONE row is what exposed a defect the other six could not.

    ⚑⚑⚑ BUT GOING TRANSITIVE MADE AGREEMENT WORSE — 6/7 to 3/7, MEASURED — AND THAT IS THE
    REAL FINDING RATHER THAN A TUNING PROBLEM. The four new disagreements all have the same
    shape: `query_builders` reaches `~query_defs`, and `query_defs` names `tenant`, so this
    reports an opener on a route whose FIRST HOP IS DEFERRED and may never fire. The hand
    ruling says the suite never runs that hop.

    ⚑⚑ SO NEITHER FORM IS RIGHT, AND THE MISSING PREDICATE IS NAMEABLE: *is the opener
    reachable through hops that ACTUALLY EXECUTE*, which needs per-hop eagerness carried
    through the walk rather than a mark on the final seed. Both lenses answer questions about
    the whole route when the question is about a prefix of it.

    ⚑ RECORDED, NOT TUNED. Fitting this predicate until it reproduces seven hand rulings would
    make the instrument agree with the answer it was built to check — and the rulings are what
    is under review.

    ⚑⚑ THE RESOLUTION IS `eager_prefix` (⟡eager-prefix-reach): the census follows only the
    hops that ALL execute, stopping at the first `~`. Hops after a cut are not "less certain",
    they are UNREACHED unless the cut fires — so crediting an opener there answers about a
    route the suite may never take.
    """
    prefix = store_reach.eager_prefix(via)
    hops = [index[name] for name in prefix if name in index]
    found: set[str] = set()
    for hop in [path, *hops]:
        found |= store_calls.connect_sites(hop)
    return frozenset(found)


def row(label: str, path: str, index: dict[str, str]) -> Row:
    """Measure one suite against both lenses."""
    strict, via = store_reach.reaches(path, index)
    loose, loose_via = store_reach.reaches(path, index, through_cuts=True)
    route = via if strict else loose_via
    return Row(
        label=label,
        declared=tenant_pragma.tenant(path),
        reaches=strict,
        via=route,
        deferred_only=loose and not strict,
        opens=opens_along(route, index, path),
    )


def census(suites: list[tuple[str, str]], index: dict[str, str]) -> list[Row]:
    """Measure every suite. Returns rows in the order given."""
    return [row(label, path, index) for label, path in suites]
