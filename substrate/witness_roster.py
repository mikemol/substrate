#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read a witness roster — resolve, group, pair — with the roster passed IN, never imported.

⚑⚑⚑ THE PARAMETER IS THE WHOLE DESIGN (Ⓝ137-prime step 3-prime ⟡drain-the-dispatch). Every
reader left in the findings ledger reaches the module-level `WITNESSES` dict directly:
`resolve`, and the `--pairing` / `--kinds` / `--list` arms of `main`. That shared dependency
is why extracting any one of them strands — the roster cannot move (its writer locates the
insertion point inside the same file), so an importing module would have to reach back into
the origin, which is the coupling the drain exists to remove.

⚑⚑ SO THE READERS TAKE THE ROSTER AS AN ARGUMENT, AND THE ORIGIN KEEPS THE DATA. That
inverts the usual extraction: nothing here imports the ledger, and the ledger will call in.
The model is already in the origin — `_kinds_rows(by)` takes its grouping as a parameter,
and its docstring names the reason: *"a SEAM a suite can call rather than a loop inside a
print block."* This is that shape applied to the readers that were not given it.

⚑ WHICH MAKES EVERY READER TESTABLE ON A FIXTURE. The origin's equivalents can only be
exercised against the live 5800-line roster, so a case pinning `resolve`'s ambiguity refusal
has to find real keys that collide. Here a three-entry fixture states the property directly.

⚑⚑⚑ AND THE REFUSALS ARE THE PART THAT MUST SURVIVE VERBATIM. `resolve` refuses an ambiguous
prefix rather than picking one, because a wrong witness reads exactly like a right one; it
distinguishes an UNKNOWN key (exit 2) from an OPEN finding (exit 1), because collapsing them
lets a typo read as debt. `pairing` refuses to report over an UNREADABLE bib, because an
unreadable bib is not an empty one. Each of those is a measured incident, not a preference.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

# A witness is a nullary callable returning (exit_code, explanation).
Witness = Callable[[], tuple[int, str]]
Roster = dict[str, Witness]

# ⚑ ONE AUTHORITY FOR THE KIND ORDER, and `BEHAVIOURAL` is DERIVED from it rather than
# spelled beside it. The origin's summary line once hardcoded ("selftest", "refuses") and
# went stale the hour `excludes` was added — a third falsifiable kind reported as if it were
# not one. Deriving the prefix means adding a kind updates the count and the sentence
# together.
KIND_ORDER: tuple[str, ...] = (
    "selftest",
    "refuses",
    "excludes",
    "agda_lacks_field",
    "agda_grep_count",
    "mode_undocumented",
    "unwitnessed",
    "standing",
)
BEHAVIOURAL: tuple[str, ...] = KIND_ORDER[: KIND_ORDER.index("mode_undocumented")]


@dataclass(frozen=True)
class Resolved:
    """A key that names exactly one witness."""

    key: str
    witness: Witness


@dataclass(frozen=True)
class Unresolved:
    """Why a key names no single witness. Carries the text a caller should print."""

    reason: str


@dataclass(frozen=True)
class Pairing:
    """The roster-versus-ledger census, de-duplicated before counting."""

    spelling_pairs: list[tuple[str, str]]
    witness_only: list[str]
    bib_only: list[str]
    raw_unpaired: int

    @property
    def true_drift(self) -> int:
        """Return the row count after de-duplication, which is the actionable number."""
        return len(self.witness_only) + len(self.bib_only) + len(self.spelling_pairs)


def resolve(roster: Roster, want: str) -> Resolved | Unresolved:
    """Return the witness `want` names — exact, else a UNIQUE PREFIX — or why not.

    ⚑ AMBIGUITY IS REFUSED, NEVER RESOLVED BY A RULE. `tmi-F1` prefixes `tmi-F10`, `tmi-F11`
    and more, so picking shortest or first would silently answer about a DIFFERENT finding.
    Exact match always wins outright, so a bare stem that is also a prefix of longer keys
    still resolves to itself.
    """
    if want in roster:
        return Resolved(want, roster[want])
    hits = sorted(k for k in roster if k.startswith(want))
    if len(hits) == 1:
        return Resolved(hits[0], roster[hits[0]])
    if hits:
        listing = "\n".join("    " + k for k in hits)
        return Unresolved(
            f"findings.py: {want!r} is an AMBIGUOUS prefix over {len(hits)} key(s) — refusing "
            f"rather than picking one, since a wrong witness reads like a right one:\n{listing}",
        )
    # ⚑ AN UNKNOWN KEY IS 2, NOT 1. "This finding is open" and "I have never heard of this
    # finding" are different facts, and collapsing them lets a typo read as debt.
    return Unresolved(
        f"findings.py: no witness registered for {want!r}, and no key begins with it — "
        "a bib entry with no witness is a roster/record disagreement (see --list)",
    )


def group_by_kind(roster: Roster) -> dict[str, list[str]]:
    """Group keys by the helper each witness actually CALLS, read off its code object.

    ⚑⚑ IT READS THE REGISTERED CLOSURE, NOT THE SOURCE. Each witness's `__code__` names the
    helper it calls, so this cannot drift from what runs — a source census would be a second
    authority for one relation.

    ⚑ THE LEADING UNDERSCORE IS LOAD-BEARING AND ITS OMISSION ONCE RETURNED EVERY WITNESS AS
    UNKNOWN. The helpers are `_standing` / `_refuses` / …; matching the bare stem matched
    nothing and the census printed five zeroes. It was caught only because a five-way zero is
    absurd on its face — a census that had merely UNDERCOUNTED would have banked.
    """
    by: dict[str, list[str]] = {}
    for key in sorted(roster):
        names = roster[key].__code__.co_names
        kind = next((o for o in KIND_ORDER if ("_" + o) in names), "?")
        by.setdefault(kind, []).append(key)
    return by


def kind_rows(by: dict[str, list[str]]) -> list[tuple[str, int]]:
    """Return (kind, count) over EVERY declared kind — the zero rows included — then surplus.

    ⚑ THE ZERO ROW IS THE WHOLE CONTRACT. "No witness uses this kind" and "the counter
    stopped seeing it" are different facts, and only a printed zero keeps them apart.
    """
    rows = [(k, len(by.get(k, []))) for k in KIND_ORDER]
    return rows + [(k, len(by[k])) for k in by if k not in KIND_ORDER]


def behavioural_count(by: dict[str, list[str]]) -> int:
    """Return how many witnesses are FALSIFIABLE, derived from the kind order."""
    return sum(len(by.get(k, [])) for k in BEHAVIOURAL)


def restem(no_entry: list[str], no_witness: list[str]) -> Pairing:
    """Split two unpaired lists into spelling pairs, true witness-only, true bib-only.

    ⚑⚑ DE-DUPLICATE BEFORE COUNTING. Four findings once appeared on BOTH lists under two
    spellings — a bare stem in the roster, a descriptive key in the bib — so thirty raw rows
    were twenty-six findings, and a naive paydown of the thirty would file eight duplicates.

    ⚑ THE TRAILING HYPHEN IS LOAD-BEARING. Without it `tmi-F1` prefixes `tmi-F10`, so two
    unrelated findings pair up and the report claims a spelling relation between different
    subjects.

    ⚑ AMBIGUITY IS REPORTED, NOT RESOLVED. If one unpaired stem prefixes several unpaired bib
    keys, no rule picks one — the row stays in the honest witness-only list.
    """
    pairs: list[tuple[str, str]] = []
    used_bib: set[str] = set()
    for w in no_entry:
        hits = [b for b in no_witness if b.startswith(w + "-")]
        if len(hits) == 1:
            pairs.append((w, hits[0]))
            used_bib.add(hits[0])
    paired_w = {w for w, _ in pairs}
    return Pairing(
        spelling_pairs=pairs,
        witness_only=[k for k in no_entry if k not in paired_w],
        bib_only=[k for k in no_witness if k not in used_bib],
        raw_unpaired=len(no_entry) + len(no_witness),
    )


def pairing(roster: Roster, bibkeys: set[str]) -> Pairing:
    """Return the de-duplicated roster-versus-ledger census.

    ⚑ THE CALLER MUST ESTABLISH THAT `bibkeys` WAS READABLE. An unreadable bib is not an
    empty one, and passing an empty set here would report every witness as unpaired. The
    origin guards that at the read site by returning None, and this signature cannot express
    the difference — which is why it is stated rather than assumed.
    """
    return restem(
        sorted(k for k in roster if k not in bibkeys),
        sorted(k for k in bibkeys if k not in roster),
    )
