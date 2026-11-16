# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The KEY SCHEMA of the set-ratchet gates — one place that knows a census key's shape.

A ratchet census key is `<field>::<field>[::<field>]`, and EXACTLY ONE field is a
repo-relative PATH. Which one differs per gate, so a hardcoded split is wrong:

    public            agda/Substrate/Foo.agda::Substrate.Bar        path first
    carrier-locality  agda/Substrate/Foo.agda::_op_                 path first
    sumtype           Crumb::agda/Substrate/Foo.agda                path SECOND
    ban               agda/Substrate/Foo.agda::Substrate.Bar::using path first, 3 fields
    claims            agda/Substrate/Foo.agda::shim::self           path first, 3 fields

⚑⚑⚑ WHY THIS EXISTS, AND IT IS THE DRAIN ARC'S OWN BLOCKER STATED FROM THE GATE SIDE. A
decomposition (`X.agda` → `X/X.agda`) is content-preserving but KEY-CHANGING: the old key
retires and a new one is minted for a byte-identical line. A set ratchet sees only "a key
appeared" and refuses — and because it returns on `added` BEFORE reaching its paydown
branch, the churn also BLOCKS real paydown from recording. So the very act of draining a
monolith makes every gate over it read as growth, and the paydown that drain earns cannot
be banked. Telling churn from genuine debt means comparing keys by the part that SURVIVES
a move: the IDENTITY, every field except the path. That comparison needs to know which
field is the path, which is what this supplies.

⚑⚑ THE REVERSAL IS THE CASE THAT MATTERS. The sumtype census emits `name::relpath`, so
reading field 0 as the path there treats every duplicate NAME as a path and every path as
an identity — exactly backwards, and it would make a genuine violation look like churn.
That is the one error this module must never make, which is why `arity` is checked and a
mismatched key REFUSES rather than being mis-assigned.

⚑ PARSING ONLY, NO I/O. This is the module a pipeline tool imports to ask "would my edit
break this gate?", so it must stay free of gate internals: no census, no baseline
mutation, no reading of a baseline file. A baseline PATH is a string a caller may want,
and it is carried as data rather than resolved here.

⚑ PROMOTED FROM `scripts/gate_keys.py`, which carries over a hundred of its own findings
and cannot take an edit. The schema is re-expressed rather than moved, so the origin stays
until its consumers point here.
"""

from __future__ import annotations

from dataclasses import dataclass

# The separator every declared gate uses today. ⚑ CARRIED PER GATE RATHER THAN GLOBAL,
# because a gate keying on a different separator is a schema entry rather than a rewrite.
_SEP = "::"

# Field counts, named so a reader is not decoding a bare integer at each entry.
_PAIR = 2
_TRIPLE = 3


@dataclass(frozen=True, slots=True)
class KeySpec:
    """One gate's key grammar: where the path sits and how many fields there are."""

    gate: str
    baseline: str
    sep: str
    path_field: int
    arity: int
    noun: str


SCHEMA: dict[str, KeySpec] = {
    "public": KeySpec(
        "public", "public_ratchet_baseline.txt", _SEP, 0, _PAIR, "`open … public` re-export(s)"
    ),
    "private": KeySpec(
        "private",
        "private_ratchet_baseline.txt",
        _SEP,
        0,
        _PAIR,
        "definition(s) hidden in a `private` block",
    ),
    "carrier-locality": KeySpec(
        "carrier-locality",
        "carrier_locality_baseline.txt",
        _SEP,
        0,
        _PAIR,
        "sanctioned exemption(s)",
    ),
    # ⚑ REVERSED — the sumtype census emits `name::relpath`. Reading field 0 as the path
    # here would treat every duplicate NAME as a path and every path as an identity.
    "sumtype": KeySpec(
        "sumtype",
        "sumtype_ratchet_baseline.txt",
        _SEP,
        1,
        _PAIR,
        "duplicate data/record declaration(s)",
    ),
    # ⚑ ALSO REVERSED, and this entry is NEW relative to the origin: the discharge census
    # emits `carrier::module`, so its identity is the leading field.
    "discharge": KeySpec(
        "discharge", "discharge_baseline.txt", _SEP, 1, _PAIR, "undischarged level-poly carrier(s)"
    ),
    "ban": KeySpec(
        "ban", "ban_ratchet_baseline.txt", _SEP, 0, _TRIPLE, "banned import directive(s)"
    ),
    "claims": KeySpec("claims", "claims_baseline.txt", _SEP, 0, _TRIPLE, "unbacked claim(s)"),
}

GATES = tuple(SCHEMA)


class MalformedKeyError(ValueError):
    """Raised for a key whose field count does not match its gate's arity."""


def parse(gate: str, key: str) -> tuple[str, tuple[str, ...]]:
    """Return `(path, identity)` for one key.

    `identity` is every field EXCEPT the path, in order — the part a file move
    preserves. Two keys with equal identity and different paths are the same violation
    seen from two locations.

    ⚑ A FIELD-COUNT MISMATCH REFUSES rather than mis-assigning the path. A wrong path
    field makes a genuine violation look like churn, which is the one error that would
    let real debt be absolved silently.
    """
    spec = SCHEMA[gate]
    fields = key.split(spec.sep)
    if len(fields) != spec.arity:
        msg = (
            f"{gate}: expected {spec.arity} {spec.sep!r}-separated field(s), "
            f"got {len(fields)} in {key!r}"
        )
        raise MalformedKeyError(msg)
    ident = tuple(f for i, f in enumerate(fields) if i != spec.path_field)
    return fields[spec.path_field], ident


def identity(gate: str, key: str) -> tuple[str, ...]:
    """Return the path-independent half of `key` — what survives a file move."""
    return parse(gate, key)[1]


def path_of(gate: str, key: str) -> str:
    """Return the repo-relative path field of `key`."""
    return parse(gate, key)[0]


def rekey(gate: str, key: str, new_path: str) -> str:
    """Return `key` with its path field replaced — the key it WOULD have at `new_path`.

    ⚑ FOR SHOWING A CHURN PAIRING, NEVER FOR REWRITING A BASELINE. A ratchet baseline is
    paydown-only, and a tool that rewrote keys in place would launder a move into an
    absolution nobody reviewed.
    """
    spec = SCHEMA[gate]
    fields = key.split(spec.sep)
    if len(fields) != spec.arity:
        msg = f"{gate}: cannot rekey malformed {key!r}"
        raise MalformedKeyError(msg)
    fields[spec.path_field] = new_path
    return spec.sep.join(fields)
