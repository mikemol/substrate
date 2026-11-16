#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.concept_families` — three arities, one dispatch.

⚑⚑⚑ THE ARITY CASES ARE THE ITEM. A binding must supply exactly what its reader takes: a key, a
key and one more value, or a key and two. Supplying too few raises at the first call and too many
raises immediately — both invisible to a table typed loosely enough to hold all three. The arms
below drive each shape through a recording reader and assert the arguments arrive.

⚑⚑ AND THE SECOND VALUE IS NOT ALWAYS A FIGURE, WHICH IS WHY THE FIELDS ARE POSITIONAL. Most
readers reconcile against a `[name=N]` tag; the retraction reader takes the SUCCESSOR key its
claim must name. A field named `figure` holding a successor is a lie the type system cannot
catch, so the record names the POSITION and the reader owns the meaning.

⚑⚑ THE ROSTERS ARE READ FROM THE MODULES THAT OWN THEM. Ratchet keys come from the family's own
items, collision keys from its declared mapping, the successor from the bib's `rests-on`. A case
pinning any of those would freeze it — the frozen-roster defect the bindings exist to avoid — so
what is asserted is AGREEMENT with the owner, never a value.

⚑ ONE LIVE FAMILY IS EXERCISED, NOT ALL OF THEM. Running every reader in one suite was killed at
exit 143 under the 192 MB lease; a suite that cannot run is not a stricter suite.

⚑ THE FIXTURES ARE NAMED GENERATORS. A lambda infers `Callable[[Any], Any]` under the strict bar;
a function RETURNING A LIST is refused too, because the record's contract is an `Iterator` — a
list is iterable and is not one, and the checker holding that line keeps a caller's `yield from`
honest.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from mikemol.witness import witness_row

from substrate import (
    ban_witness,
    collision_witness,
    concept_families,
    ratchet_family,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

# A key no family answers.
_ABSENT = "no-such-family-key-8c02"

# The family exercised live. ⚑ THE RATCHET FAMILY reads one baseline and compares it, where the
# corpus-walking readers are what put an exhaustive run over its lease.
_LIVE = ratchet_family.ITEMS[0].key

# The retraction key whose successor the bib declares.
_RETRACTED = "R14-legible"

# What each recording fixture saw, cleared per case.
_SEEN: list[tuple[str, ...]] = []


def _record_keyed(one: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Record a key-only call."""
    _SEEN.append((one,))
    yield witness_row.closed(one, "recorded")


def _record_paired(
    one: str,
    two: str,
) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Record a two-argument call."""
    _SEEN.append((one, two))
    yield witness_row.closed(one, "recorded")


def _record_tripled(
    one: str,
    two: str,
    three: str,
) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Record a three-argument call."""
    _SEEN.append((one, two, three))
    yield witness_row.closed(one, "recorded")


def _seen(binding: concept_families.Family, key: str) -> list[tuple[str, ...]]:
    """Run a binding and return the arguments its reader received."""
    _SEEN.clear()
    list(binding.rows(key))
    return list(_SEEN)


def a_keyed_family_receives_the_key(out: list[str]) -> int:
    """Check a key-only reader is called with the key alone."""
    binding = concept_families.Family(keyed=_record_keyed)
    got = _seen(binding, "X")
    if got != [("X",)]:
        out.append(f"selftest: a keyed family received {got!r}")
        return 1
    return 0


def a_paired_family_receives_its_second(out: list[str]) -> int:
    """Check a two-argument reader is called with the declared second value.

    ⚑⚑ A BINDING PASSING THE WRONG ONE makes a witness compare against something nobody wrote,
    and the mismatch then reads as a finding about the tree rather than about the binding.
    """
    binding = concept_families.Family(paired=_record_paired, second="a-second")
    got = _seen(binding, "X")
    if got != [("X", "a-second")]:
        out.append(f"selftest: a paired family received {got!r}")
        return 1
    return 0


def a_tripled_family_receives_both(out: list[str]) -> int:
    """Check a three-argument reader is called with both extra values.

    ⚑ THE THIRD ARITY IS REAL. One body serves three collision partitions, and the partition is
    what selects which — a binding dropping it would measure whichever the reader defaults to.
    """
    binding = concept_families.Family(tripled=_record_tripled, second="a-second", third="a-third")
    got = _seen(binding, "X")
    if got != [("X", "a-second", "a-third")]:
        out.append(f"selftest: a tripled family received {got!r}")
        return 1
    return 0


def an_unbound_family_opens(out: list[str]) -> int:
    """Check a record with no reader emits an UNMEASURED verdict.

    ⚑ AN EMPTY RECORD IS CONSTRUCTIBLE, so it must not yield silence — a family bound to nothing
    would otherwise read as a clean item.
    """
    rows = list(concept_families.Family().rows("X"))
    if len(rows) != 1 or not isinstance(rows[0], witness_row.Verdict):
        out.append(f"selftest: an unbound family emitted {rows!r}")
        return 1
    if rows[0].state != witness_row.OPEN:
        out.append(f"selftest: an unbound family read as {rows[0].state!r}")
        return 1
    return 0


def the_successor_is_read_from_the_bib(out: list[str]) -> int:
    """Check the retraction's successor comes from the declared relation.

    ⚑⚑ A CONSTANT HERE WOULD BE A SECOND SPELLING of a relation the warrant set already carries,
    and the two would disagree the first time either moved. What is asserted is that the value
    RESOLVES — never which key it is, since that is the bib's to say.
    """
    if not concept_families.successor():
        out.append("selftest: the retraction names no successor — the relation did not resolve")
        return 1
    return 0


def the_retraction_binding_carries_its_successor(out: list[str]) -> int:
    """Check the bound retraction row passes the successor it read."""
    found = concept_families.family(_RETRACTED)
    if found is None:
        out.append("selftest: the retraction key is unbound")
        return 1
    if found.second != concept_families.successor():
        out.append(f"selftest: the retraction binding carries {found.second!r}")
        return 1
    return 0


def the_ratchet_keys_come_from_the_family(out: list[str]) -> int:
    """Check every ratchet item is bound, with no key typed here.

    ⚑⚑ THE MODULE OWNS ITS MEMBERSHIP. A roster in two places disagrees the first time a ratchet
    moves, and asserting agreement rather than a count is what keeps the upstream free to change.
    """
    bound = set(concept_families.bound_keys())
    owed = {got.key for got in ratchet_family.ITEMS}
    if not owed <= bound:
        out.append(f"selftest: unbound ratchet key(s): {sorted(owed - bound)!r}")
        return 1
    return 0


def the_collision_keys_come_from_the_mapping(out: list[str]) -> int:
    """Check every declared collision partition is bound to its own key and figure."""
    for kind, (key, figure) in collision_witness.KEYS.items():
        found = concept_families.family(key)
        if found is None:
            out.append(f"selftest: collision key {key} is unbound")
            return 1
        if found.third != kind or found.second != figure:
            out.append(
                f"selftest: {key} bound to {found.third!r}/{found.second!r}, "
                f"expected {kind!r}/{figure!r}"
            )
            return 1
    return 0


def the_ban_keys_come_from_the_buckets(out: list[str]) -> int:
    """Check each ban bucket has a key, plus the aggregate and the reach row."""
    bound = set(concept_families.bound_keys())
    owed = {"A5", "A5-as-reach", *(f"A5-{kind}" for kind in ban_witness.BUCKETS)}
    if not owed <= bound:
        out.append(f"selftest: unbound ban key(s): {sorted(owed - bound)!r}")
        return 1
    return 0


def an_absent_key_binds_to_nothing(out: list[str]) -> int:
    """Check an unlisted key returns None rather than a plausible reader."""
    if concept_families.family(_ABSENT) is not None:
        out.append("selftest: an absent key resolved to a family")
        return 1
    return 0


def an_absent_key_yields_no_rows(out: list[str]) -> int:
    """Check an unbound key is silent here rather than emitting a verdict.

    ⚑ THE LIBRARY OWNS THE UNMEASURED VERDICT. Emitting one here too would give a single fact two
    voices, and they would drift the first time either was reworded.
    """
    if list(concept_families.rows(_ABSENT)):
        out.append("selftest: an absent key yielded rows")
        return 1
    return 0


def the_key_list_is_sorted(out: list[str]) -> int:
    """Check the enumeration is ordered, so two runs read the same."""
    got = concept_families.bound_keys()
    if list(got) != sorted(got):
        out.append(f"selftest: the keys are unsorted: {got!r}")
        return 1
    return 0


def the_table_is_not_empty(out: list[str]) -> int:
    """Check the table holds entries.

    ⚑ AN EMPTY TABLE PASSES EVERY SUBSET ARM ABOVE, vacuously — the collection-destruction shape
    only a non-empty claim can catch.
    """
    if not concept_families.families():
        out.append("selftest: the family table is empty")
        return 1
    return 0


def a_live_family_emits_a_verdict(out: list[str]) -> int:
    """Check one real binding produces rows ending in a verdict.

    ⚑⚑⚑ A WELL-TYPED BINDING CAN STILL FAIL AT THE FIRST CALL. Wiring is what the checker proves;
    that the composition survives contact with the tree is what only running it shows.
    """
    try:
        rows = list(concept_families.rows(_LIVE))
    except Exception as exc:  # noqa: BLE001 — any failure is this case's finding
        out.append(f"selftest: {_LIVE} raised {type(exc).__name__}: {exc}")
        return 1
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append(f"selftest: {_LIVE} emitted no trailing verdict: {rows!r}")
        return 1
    return 0


_ARMS = (
    a_keyed_family_receives_the_key,
    a_paired_family_receives_its_second,
    a_tripled_family_receives_both,
    an_unbound_family_opens,
    the_successor_is_read_from_the_bib,
    the_retraction_binding_carries_its_successor,
    the_ratchet_keys_come_from_the_family,
    the_collision_keys_come_from_the_mapping,
    the_ban_keys_come_from_the_buckets,
    an_absent_key_binds_to_nothing,
    an_absent_key_yields_no_rows,
    the_key_list_is_sorted,
    the_table_is_not_empty,
    a_live_family_emits_a_verdict,
)

_CASE_COUNT = 1 + 1 + 1 + 2 + 1 + 1 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"concept-families selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"concept-families selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
