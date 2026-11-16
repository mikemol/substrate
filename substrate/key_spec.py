#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""A ratchet census key's SHAPE — which field is the path, and what survives a file move.

⚑⚑⚑ EXACTLY ONE FIELD IS A PATH AND WHICH ONE DIFFERS PER GATE, so a hardcoded
`partition("::")` is wrong. The sumtype census emits `name::relpath` while every other gate
emits path-first — reading field 0 as the path there would treat every duplicate NAME as a path
and every path as an identity: exactly backwards.

⚑⚑ THE REASON THIS DISTINCTION EXISTS AT ALL. A decomposition (`X.agda` → `X/X.agda`) is
content-preserving but KEY-CHANGING: the old key retires and a new one is minted for a
byte-identical line. A ratchet sees only *"a key appeared"* and refuses — and because it returns
on `added` BEFORE reaching its paydown branch, the churn also BLOCKS real paydown from
recording. Telling churn from genuine debt means comparing keys by the part that SURVIVES a
move: the IDENTITY, every field except the path.

⚑⚑ AND A WRONG PATH FIELD MAKES A GENUINE VIOLATION LOOK LIKE CHURN, which is the one error this
module must never make. That is why a malformed key RAISES rather than being partitioned
best-effort: a key with the wrong field count is malformed *for that gate*, and silently
mis-assigning its path field would produce a confident wrong answer.

⚑ RE-DECLARED RATHER THAN IMPORTED, AND THE REASON IS MECHANICAL. `scripts/gate_keys.py` holds
the same schema as an untyped `namedtuple`, so every `KeySpec` reference it hands out is `Any` —
importing it drags that (and its module's 119 findings) through the type check of any clean file
that touches it. ⚑⚑ THIS IS THEREFORE A SECOND SPELLING OF ONE FACT, which this repo normally
forbids: the resolution is that the OLD one retires when its consumers move, not that two
authorities coexist. Recorded here so the duplication is a stated debt with an end, rather than
a drift nobody noticed.

⚑ EXTRACTED FROM `catalog/library/figures.py` and `scripts/gate_keys.py` (⟡items-n-split).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class MalformedKeyError(ValueError):
    """A key whose field count does not match its gate's arity."""


@dataclass(frozen=True, slots=True)
class KeySpec:
    """One gate's key shape.

    ⚑ `arity` IS THE EXPECTED FIELD COUNT, and it is checked rather than assumed. A key with a
    different count is malformed for this gate, and refusing is what keeps a mis-assigned path
    field from turning a real violation into apparent churn.
    """

    gate: str
    baseline: str
    sep: str
    path_field: int
    arity: int
    noun: str


# Where the gates keep their baselines — the directory this repo's ratchet gates live in.
_GATE_DIR = "scripts"

# ⚑ THE DECLARED SCHEMA. Each entry says how that gate spells a key; the comments name the ones
# that are not path-first, because those are where a positional assumption goes wrong silently.
SCHEMA: dict[str, KeySpec] = {
    "public": KeySpec(
        gate="public",
        baseline=f"{_GATE_DIR}/public_ratchet_baseline.txt",
        sep="::",
        path_field=0,
        arity=2,
        noun="`open … public` re-export(s)",
    ),
    "carrier-locality": KeySpec(
        gate="carrier-locality",
        baseline=f"{_GATE_DIR}/carrier_locality_baseline.txt",
        sep="::",
        path_field=0,
        arity=2,
        noun="sanctioned exemption(s)",
    ),
    # ⚑ REVERSED — this census builds `f"{name}::{rel}"`, so the PATH IS FIELD 1. Reading field
    # 0 as the path here is the recorded backwards case.
    "sumtype": KeySpec(
        gate="sumtype",
        baseline=f"{_GATE_DIR}/sumtype_ratchet_baseline.txt",
        sep="::",
        path_field=1,
        arity=2,
        noun="duplicate data/record declaration(s)",
    ),
    "ban": KeySpec(
        gate="ban",
        baseline=f"{_GATE_DIR}/ban_ratchet_baseline.txt",
        sep="::",
        path_field=0,
        arity=3,
        noun="banned import directive(s)",
    ),
    "claims": KeySpec(
        gate="claims",
        baseline=f"{_GATE_DIR}/claims_baseline.txt",
        sep="::",
        path_field=0,
        arity=3,
        noun="unbacked claim(s)",
    ),
}


def spec_for(name: str) -> KeySpec | None:
    """Return the schema for a gate module filename, or None when undeclared.

    ⚑ THE SCHEMA IS KEYED BY SHORT NAME (`ban`) AND A CENSUS BY MODULE FILENAME
    (`check_ban_ratchet.py`), so matching them is a LOOKUP rather than a guess.

    ⚑⚑ AND AN UNDECLARED GATE RETURNS None RATHER THAN A DEFAULT. Six of ten baselines lacked an
    entry, so defaulting would silently mis-partition exactly those — the population most in need
    of a correct answer would get the least reliable one.
    """
    stem = Path(name).name.replace("-", "_")
    for short, spec in SCHEMA.items():
        if short.replace("-", "_") in stem:
            return spec
    return None


def parse(spec: KeySpec, key: str) -> tuple[str, tuple[str, ...]]:
    """Split one key into `(path, identity)` — identity is every field except the path."""
    fields = key.split(spec.sep)
    if len(fields) != spec.arity:
        msg = (
            f"{spec.gate}: expected {spec.arity} {spec.sep!r}-separated fields, "
            f"got {len(fields)} in {key!r}"
        )
        raise MalformedKeyError(msg)
    path = fields[spec.path_field]
    identity = tuple(f for i, f in enumerate(fields) if i != spec.path_field)
    return path, identity


def identity(spec: KeySpec, key: str) -> tuple[str, ...]:
    """Return the path-independent half of `key` — what survives a file move."""
    return parse(spec, key)[1]


def path_of(spec: KeySpec, key: str) -> str:
    """Return the repo-relative path field of `key`."""
    return parse(spec, key)[0]


def rekey(spec: KeySpec, key: str, new_path: str) -> str:
    """Return `key` with its path field replaced — the key this violation WOULD have there.

    ⚑ FOR SHOWING A CHURN PAIRING, NEVER FOR REWRITING A BASELINE. A baseline rewritten by a
    tool is a record of what the tool believed, not of what was measured.
    """
    fields = key.split(spec.sep)
    if len(fields) != spec.arity:
        msg = f"{spec.gate}: cannot rekey malformed {key!r}"
        raise MalformedKeyError(msg)
    fields[spec.path_field] = new_path
    return spec.sep.join(fields)


def kind_of(spec: KeySpec, key: str) -> str | None:
    """Return the KIND field — the trailing field of an arity-3 key, else None.

    ⚑⚑ A COUNT IS NOT A SHAPE, and this is the read that turns one into the other. Handed
    *"216 added"* a reader classifies it in prose — *"a real population, not the 4-site kind"* —
    and that judgement decides whether the work is a SWEEP or a per-site grind, i.e. which tool
    applies. The partition answers it from data already in hand.

    ⚑ AND A 2-FIELD KEY HAS NO KIND, WHICH IS NOT THE SAME AS ONE KIND. An earlier partition
    took the last field unconditionally and reported *"35 kind(s), each x1"* for an arity-2
    gate — the identity field, one per key, which is the key's own NAME re-listed rather than a
    shape at all. The honest answer for those gates is that the population has no sub-kind.
    """
    min_arity_with_kind = 3
    if spec.arity < min_arity_with_kind:
        return None
    fields = key.split(spec.sep)
    if len(fields) != spec.arity:
        return None
    return fields[-1]
