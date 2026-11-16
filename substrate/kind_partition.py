#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""A COUNT IS NOT A SHAPE — partition a gate's added keys by kind, and by where they concentrate.

⚑⚑⚑ THIS IS A JUDGEMENT THAT WAS BEING MADE IN PROSE, MECHANIZED. Handed *"A5: 216 added"* a
reader writes *"216 is a real population, not the 4-site kind"* — a size classification, made by
eye, deciding whether the work is a SWEEP or a per-site grind, i.e. which tool applies. That is
a read of data already in hand: a key is `<scope>::<…>::<kind>`, so the population's shape is
the partition by its kind field.

⚑⚑ AND THE SPLIT DECIDES THE TOOL. 216 keys over three directives is three sweeps with three
tools; 216 keys of one kind is one. An item was mis-sequenced because the buckets were
conflated — filed as one population behind *"the tree must be green"*, when two of the three
buckets needed no green tree at all.

⚑⚑⚑ CONCENTRATION IS THE SECOND HALF, AND WITHOUT IT THE FIRST IS A REFLEX. `kinds` says
`as x135, using x51, renaming x30`, and picking the biggest bucket is not a measurement: **135
keys against 3 PROVIDERS is three decisions and one sweep; 135 keys against 135 providers is
135 hand-edits.** Size orders the buckets; concentration says which is actually cheap.

⚑⚑ THE PLAN RECORDS THIS EXACT MISTAKE MADE TWICE. A renaming census looked like 3,615
independent clauses and was dominated by ONE replicated prelude over ONE provider — *"434 of 487
blockers are `_+_`, 424 of those from a single module"*. Both times the fix was one decision at
the provider, not a sweep over the consumers. **A count of keys is not a count of decisions.**

⚑ AN UNMEASURABLE CENSUS RETURNS None, NEVER AN EMPTY PARTITION. A gate that cannot be censused
has an UNKNOWN shape, not a uniform one — and printing nothing says so, where printing `1 kind`
would assert exactly the thing that was not measured.

⚑ `n` RATHER THAN `count`, BECAUSE THIS IS A `NamedTuple`. A field called `count` shadows
`tuple.count`, and the type checker caught it — the same shadowing the table reader hit with
`index`. A caller reaching for the method would get a field.

⚑ EXTRACTED FROM `catalog/library/figures.py` (⟡items-n-split). Six ratchet witnesses read this.
"""

from __future__ import annotations

from dataclasses import dataclass

from mikemol.ratchet import keys

from substrate import ratchet_census

# The bucket label given to keys that do not parse for their gate's schema.
MALFORMED = "(malformed)"

# ⚑ The separator every `substrate:` gate schema declares, used only to RENDER an identity tuple
# back into one label. The schema owns parsing; this joins what the schema already split.
_IDENTITY_SEP = "::"

# Why a gate has no partition when its module filename declares no schema.
_UNDECLARED = "no key schema for this gate — the key's fields are undeclared"


@dataclass(frozen=True, slots=True)
class Bucket:
    """One partition bucket: its label, how many keys carry it, and one of them."""

    label: str
    n: int
    sample: str


def _by_size(bucket: Bucket) -> tuple[int, str]:
    """Sort key: largest bucket first, then by label.

    ⚑ THE TIE-BREAK IS THE LABEL, NOT INSERTION ORDER, so two runs over one census produce the
    same report. A report whose row order moves for no reason reads as a moving population.
    """
    return (-bucket.n, bucket.label)


def bucketed(rows: dict[str, list[str]]) -> list[Bucket]:
    """Return buckets ordered by size, then by label."""
    out = [Bucket(label=label, n=len(ks), sample=min(ks)) for label, ks in rows.items()]
    out.sort(key=_by_size)
    return out


def _schema(name: str) -> keys.KeySchema | None:
    """Return the schema a gate module's filename declares, or None when it declares none.

    ⚑ `mikemol.ratchet.keys` owns the table (W41, retiring `substrate.key_spec`); a filename
    naming two schemas is REFUSED there rather than resolved by table order.
    """
    declared = keys.spec_for(name)
    return keys.schema_named(declared) if declared is not None else None


def _parsed(schema: keys.KeySchema, key: str) -> keys.ParsedKey | None:
    """Parse one key, or None when the schema refuses it.

    ⚑ THE SCHEMA RAISES; A PARTITION BUCKETS. A malformed key is a finding about the census, so it
    is carried as its own bucket rather than aborting the whole partition.
    """
    try:
        return schema(key)
    except keys.MalformedKeyError:
        return None


def kinds(name: str) -> tuple[list[Bucket] | None, str | None]:
    """Partition a gate's ADDED keys by kind, or say why the shape is unknown.

    ⚑ A GATE WHOSE KEYS HAVE NO KIND FIELD RETURNS None WITH A REASON, not an empty list. An
    earlier partition took the last field unconditionally and reported *"35 kind(s), each x1"*
    for an arity-2 gate — the identity field, one per key, which is the key's own NAME re-listed
    rather than a shape at all.
    """
    census, why = ratchet_census.census(name)
    if census is None:
        return None, why

    schema = _schema(name)
    if schema is None:
        return None, _UNDECLARED

    by: dict[str, list[str]] = {}
    kindless = 0
    for key in census.added:
        parsed = _parsed(schema, key)
        kind = keys.kind_of(parsed) if parsed is not None else None
        if parsed is not None and kind is None:
            kindless += 1
            continue
        # ⚑ A MALFORMED KEY IS ITS OWN BUCKET, NOT A SILENT DROP. Keys that do not parse are a
        # finding about the census, and discarding them would make the partition's total
        # disagree with the census's count for no visible reason.
        by.setdefault(kind if kind is not None else MALFORMED, []).append(key)

    # ⚑⚑ A KEY THAT PARSES AND HAS NO KIND IS WELL-FORMED, NOT MALFORMED (W41 collapse audit).
    # For a 2-field gate every key is kindless, and this module used to bucket them all as
    # "(malformed)" and report a well-formed census as broken; `key_partition` refused it
    # correctly, and that refusal is carried here so it can retire.
    if kindless:
        return None, f"{kindless} added key(s) parse with no kind field — no kind to partition by"
    if not by:
        return [], None
    if list(by) == [MALFORMED]:
        return None, (
            f"every added key is malformed for this gate "
            f"(schema {keys.spec_for(name)!r} refuses each one)"
        )
    return bucketed(by), None


def concentration(name: str, kind: str) -> tuple[list[Bucket] | None, str | None]:
    """Partition ONE kind's keys by IDENTITY — where the decisions actually are.

    ⚑ IDENTITY, NOT PATH, BECAUSE IDENTITY IS WHAT A DECISION IS ABOUT. For a banned import the
    identity is the PROVIDER MODULE plus the directive; the path is merely where one consumer
    happens to sit. Partitioning by path would count consumers and call it decisions, which is
    the sweep-vs-grind error with the arrow reversed.
    """
    census, why = ratchet_census.census(name)
    if census is None:
        return None, why

    schema = _schema(name)
    if schema is None:
        return None, _UNDECLARED

    by: dict[str, list[str]] = {}
    for key in census.added:
        parsed = _parsed(schema, key)
        if parsed is None or keys.kind_of(parsed) != kind:
            continue
        identity = _IDENTITY_SEP.join(parsed.identity)
        by.setdefault(identity, []).append(key)
    return bucketed(by), None


def render(buckets: list[Bucket], *, limit: int = 4) -> str:
    """Render a partition as one line — the summary a witness prints.

    ⚑ THE LIMIT IS AN EARLY STOP, NOT A SLICE OF A RENDERED STRING. A truncation written as a
    slice is invisible in the output; written as a bound it is a stated `+N more`, which is what
    lets a reader tell a short population from a truncated one.
    """
    if not buckets:
        return "no added keys"
    shown = ", ".join(f"{b.label} x{b.n}" for b in buckets[:limit])
    rest = len(buckets) - limit
    tail = f", +{rest} more" if rest > 0 else ""
    return f"{len(buckets)} kind(s): {shown}{tail}"
