#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Partition a ratchet's added keys - by KIND, then by IDENTITY within a kind - under its KeySpec.

THE THIRD CUT OF THE DRAIN'S FIFTH FILE (`catalog/library/figures.py:249-347`, W4 tick 60), and
the only part of the ratchet census family that was not already in the package: `ratchet_gates`
is `gate_population.gates`, `_gate_module` is `gate_module.gate_module`, `ratchet_census` is
`ratchet_census.census`, `gates_without_universal_flags` is `universal_flags.lacking`, `_key_spec`
is `key_spec.spec_for`. Those bind; this is the judgement they fed.

A COUNT IS NOT A SHAPE. Handed "216 added" a reader decides in prose whether the item is a SWEEP
or a per-site grind, and that decision picks the tool. A ratchet key is `<scope>::...::<kind>`,
so the population's shape is its partition by the kind field - 216 keys over three directives is
three sweeps, 216 of one kind is one. And within a kind, SIZE orders the buckets while
CONCENTRATION says which is cheap: 135 keys against 3 providers is three decisions, against 135
providers it is 135 hand-edits. The origin records both mistakes being made by eye, twice.

THE FIELDS ARE THE SCHEMA'S, NEVER POSITIONAL. The first partition took the last `::` field
unconditionally and reported "35 kind(s), each x1" for an arity-2 gate - the key's own name
re-listed. `key_spec.SCHEMA` records which field is the path and how many fields a key has; a
2-field key has NO kind, which is not the same as one kind, and is refused with the reason.
Both partitions return `(rows, None)` or `(None, why)` - never an empty partition for an
unavailable census, because a gate that cannot be read has an UNKNOWN shape, not a uniform one.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    from substrate.key_spec import KeySpec

# One bucket: (label, count, the smallest key in it as a sample).
Bucket = tuple[str, int, str]
Partition = tuple[list[Bucket] | None, str | None]
# Where a key with the wrong field count lands in the kind partition.
MALFORMED = "(malformed)"
# The smallest arity that carries a kind field beside path and identity.
MIN_ARITY_WITH_KIND = 3


def _buckets(by: dict[str, list[str]]) -> list[Bucket]:
    """Render buckets largest first, ties by label."""
    rows = [(label, len(v), min(v)) for label, v in by.items()]
    return sorted(rows, key=_order)


def _order(row: Bucket) -> tuple[int, str]:
    """Sort key: descending count, then label."""
    return (-row[1], row[0])


def by_kind(keys: Iterable[str], spec: KeySpec | None) -> Partition:
    """Partition keys by their KIND field; refuse when the schema declares no such field."""
    if spec is None:
        return None, "no gate_keys.SCHEMA entry -- the key's fields are undeclared"
    if spec.arity < MIN_ARITY_WITH_KIND:
        shape = spec.sep.join(["path", "name"][: spec.arity])
        return None, f"keys are {spec.arity}-field ({shape}) -- no kind field to partition by"
    by: dict[str, list[str]] = {}
    for k in keys:
        parts = k.split(spec.sep)
        label = parts[-1] if len(parts) == spec.arity else MALFORMED
        by.setdefault(label, []).append(k)
    return _buckets(by), None


def concentration(keys: Iterable[str], spec: KeySpec | None, kind: str) -> Partition:
    """Partition one kind's keys by IDENTITY (every field but the path) - where they concentrate."""
    if spec is None:
        return None, "no gate_keys.SCHEMA entry -- the key's fields are undeclared"
    by: dict[str, list[str]] = {}
    for k in keys:
        parts = k.split(spec.sep)
        if len(parts) != spec.arity:
            continue
        if spec.arity >= MIN_ARITY_WITH_KIND and parts[-1] != kind:
            continue
        ident = spec.sep.join(p for i, p in enumerate(parts) if i != spec.path_field)
        by.setdefault(ident, []).append(k)
    return _buckets(by), None
