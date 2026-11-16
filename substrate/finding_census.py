#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Count the ledger's witnesses BY KIND, printing the kinds nobody uses.

⚑⚑⚑ THE ZERO ROW IS THE WHOLE CONTRACT. *"No witness uses this kind"* and *"the counter
stopped seeing this kind"* are different facts, and only a printed zero keeps them apart.
Iterating the grouping dict instead drops an empty kind silently, so a `refuses:` population
that fell to zero — by deletion, by a rename, or by the matcher breaking — would read as a
roster that simply never had one.

⚑⚑ AND THIS CENSUS HAS ALREADY PRINTED FIVE ZEROES ONCE. The probe that classified each
witness omitted the helpers' leading underscore, so every witness landed in the unknown
bucket. It was caught only because a five-way zero is absurd on its face — **a census that had
merely UNDERCOUNTED would have banked.** That is why the rows are a SEAM a suite can call
rather than a loop inside a print block: an aggregate printed and discarded cannot be audited
against a case.

⚑⚑⚑ `BEHAVIOURAL` IS DERIVED FROM `KIND_ORDER`, NEVER RESTATED, and the slice point is the
declaration. Two hand-kept lists of one fact is the defect this ledger records elsewhere as
`swarm-F3`; here the falsifiable kinds are exactly the prefix before `mode_undocumented`, so
adding a kind in the right position puts it on the right side by construction.

⚑ AND `mode_undocumented` IS DELIBERATELY OUTSIDE THE BEHAVIOURAL PREFIX. It asks whether a
mode is DOCUMENTED, which a mechanism's repair does not move — the measured `swarm-F12` case,
where a cgroup cap being enforced was filed as `mode:` and returned green for the unrelated
reason that its selftest flag was documented. `unwitnessed` is always UNRUNNABLE by
construction and `standing` never flips, so neither is behavioural either.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

# ⚑ THE DECLARED KINDS, IN REPORT ORDER. The order is not cosmetic: the falsifiable kinds lead,
#   and `BEHAVIOURAL` is the prefix before the first non-falsifiable one.
KIND_ORDER: tuple[str, ...] = (
    "selftest", "refuses", "excludes", "agda_lacks_field", "agda_grep_count",
    "mode_undocumented", "unwitnessed", "standing",
)

#: The kinds a CODE CHANGE can flip — derived from `KIND_ORDER` rather than restated.
BEHAVIOURAL: tuple[str, ...] = KIND_ORDER[:KIND_ORDER.index("mode_undocumented")]


def rows(by_kind: Mapping[str, Sequence[str]]) -> list[tuple[str, int]]:
    """Return `[(kind, count)]` over EVERY declared kind, then any surplus kind observed.

    ⚑ A DECLARED KIND WITH NO MEMBERS STILL GETS A ROW, which is the point. A surplus kind —
    one the grouping produced that no declaration names — is appended rather than dropped,
    because an unrecognised kind is a finding about the classifier and not something to hide.
    """
    declared = [(kind, len(by_kind.get(kind, ()))) for kind in KIND_ORDER]
    surplus = [(kind, len(members)) for kind, members in by_kind.items()
               if kind not in KIND_ORDER]
    return declared + surplus


def behavioural_total(by_kind: Mapping[str, Sequence[str]]) -> int:
    """Return how many witnesses a code change could flip.

    ⚑ THE FIGURE THE LEDGER LEADS WITH, and it is a floor on the ledger's own honesty: the
    complement is witnesses that assert only that a finding is still WRITTEN DOWN.
    """
    return sum(len(by_kind.get(kind, ())) for kind in BEHAVIOURAL)


def vacuous_total(by_kind: Mapping[str, Sequence[str]]) -> int:
    """Return how many witnesses no code change can flip — `standing` alone.

    ⚑ `unwitnessed` IS NOT COUNTED HERE, and the distinction is load-bearing. An unwitnessed
    finding reports an HONEST GAP and says so on every read; a `standing` one passes at 0 and
    looks like a verdict. Folding them together would report the honest kind as debt.
    """
    return len(by_kind.get("standing", ()))
