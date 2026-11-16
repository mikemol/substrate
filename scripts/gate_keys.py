#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The KEY SCHEMA of the set-ratchet gates — one place that knows a census key's shape.

A ratchet census key is `<field>::<field>[::<field>]`, and EXACTLY ONE field is a
repo-relative PATH.  Which one differs per gate, so a hardcoded `partition("::")`
is wrong:

    public            agda/Substrate/Foo.agda::Substrate.Bar        path first
    carrier-locality  agda/Substrate/Foo.agda::_op_                 path first
    sumtype           Crumb::agda/Substrate/Foo.agda                path SECOND
    ban               agda/Substrate/Foo.agda::Substrate.Bar::using path first, 3 fields
    claims            agda/Substrate/Foo.agda::shim::self           path first, 3 fields

WHY THIS EXISTS.  A decomposition (`X.agda` → `X/X.agda`) is content-preserving but
KEY-changing: the old key retires and a new one is minted for a byte-identical line.
`ratchet.set_ratchet` sees only "a key appeared" and refuses — and because it returns
on `added` BEFORE reaching its paydown branch, the churn also BLOCKS real paydown from
recording.  Telling churn from genuine debt means comparing keys by the part that
SURVIVES a move: the IDENTITY (every field except the path).  That comparison needs to
know which field is the path, which is what this module supplies.

This is the module a pipeline tool imports to ask "would my edit break this gate?" —
so it must stay free of gate internals: no census, no baseline mutation, no I/O beyond
reading a baseline path string.  Parsing only.
"""

import os
from collections import namedtuple

HERE = os.path.dirname(os.path.abspath(__file__))

# arity is the EXPECTED field count.  A key with a different count is malformed for
# this gate; `parse` refuses rather than silently mis-assigning the path field (a
# wrong path field would make a genuine violation look like churn — the one error
# this module must never make).
KeySpec = namedtuple("KeySpec", "gate baseline sep path_field arity noun")

SCHEMA = {
    "public": KeySpec(
        "public",
        os.path.join(HERE, "public_ratchet_baseline.txt"),
        "::",
        0,
        2,
        "`open … public` re-export(s)",
    ),
    "carrier-locality": KeySpec(
        "carrier-locality",
        os.path.join(HERE, "carrier_locality_baseline.txt"),
        "::",
        0,
        2,
        "sanctioned exemption(s)",
    ),
    # ⚑ REVERSED — the sumtype census emits `name::relpath` (check_sumtype_ratchet.py
    # builds `f"{name}::{rel}"`).  Reading field 0 as the path here would treat every
    # duplicate NAME as a path and every path as an identity: exactly backwards.
    "sumtype": KeySpec(
        "sumtype",
        os.path.join(HERE, "sumtype_ratchet_baseline.txt"),
        "::",
        1,
        2,
        "duplicate data/record declaration(s)",
    ),
    "ban": KeySpec(
        "ban",
        os.path.join(HERE, "ban_ratchet_baseline.txt"),
        "::",
        0,
        3,
        "banned import directive(s)",
    ),
    "claims": KeySpec(
        "claims", os.path.join(HERE, "claims_baseline.txt"), "::", 0, 3, "unbacked claim(s)"
    ),
}

GATES = tuple(SCHEMA)


class MalformedKey(ValueError):
    """A key whose field count does not match its gate's arity."""


def parse(gate, key):
    """`key` -> (path, identity_tuple).

    `identity` is every field EXCEPT the path, in order — the part a file move
    preserves.  Two keys with equal identity and different paths are the same
    violation seen from two locations.
    """
    spec = SCHEMA[gate]
    fields = key.split(spec.sep)
    if len(fields) != spec.arity:
        raise MalformedKey(
            f"{gate}: expected {spec.arity} {spec.sep!r}-separated fields, "
            f"got {len(fields)} in {key!r}"
        )
    path = fields[spec.path_field]
    ident = tuple(f for i, f in enumerate(fields) if i != spec.path_field)
    return path, ident


def identity(gate, key):
    """The path-independent half of `key` — what survives a file move."""
    return parse(gate, key)[1]


def path_of(gate, key):
    """The repo-relative path field of `key`."""
    return parse(gate, key)[0]


def rekey(gate, key, new_path):
    """`key` with its path field replaced — the key this violation WOULD have
    at `new_path`.  Used to show a churn pairing, never to rewrite a baseline."""
    spec = SCHEMA[gate]
    fields = key.split(spec.sep)
    if len(fields) != spec.arity:
        raise MalformedKey(f"{gate}: cannot rekey malformed {key!r}")
    fields[spec.path_field] = new_path
    return spec.sep.join(fields)


def _selftest():
    """Counted — a hardcoded total once hid an added case (prune_imports.py:332)."""
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    check(
        "public: path first",
        parse("public", "agda/Substrate/Q/Rat.agda::ℚ"),
        ("agda/Substrate/Q/Rat.agda", ("ℚ",)),
    )
    check(
        "sumtype: path SECOND (reversed)",
        parse("sumtype", "Crumb::agda/Substrate/Category/PrimeSampledChain.agda"),
        ("agda/Substrate/Category/PrimeSampledChain.agda", ("Crumb",)),
    )
    check(
        "ban: 3 fields, identity keeps both non-path",
        parse("ban", "agda/Substrate/A.agda::Substrate.Foundation.Eq::using"),
        ("agda/Substrate/A.agda", ("Substrate.Foundation.Eq", "using")),
    )
    check(
        "claims: 3 fields",
        parse("claims", "agda/Substrate/A.agda::shim::self"),
        ("agda/Substrate/A.agda", ("shim", "self")),
    )
    check(
        "identity survives a move",
        identity("public", "agda/Substrate/Q/Rat.agda::ℚ")
        == identity("public", "agda/Substrate/Q.agda::ℚ"),
        True,
    )
    check(
        "identity distinguishes different names",
        identity("public", "agda/Substrate/A.agda::X")
        != identity("public", "agda/Substrate/A.agda::Y"),
        True,
    )
    check(
        "rekey rebuilds the moved key",
        rekey("public", "agda/Substrate/Q.agda::ℚ", "agda/Substrate/Q/Rat.agda"),
        "agda/Substrate/Q/Rat.agda::ℚ",
    )
    check(
        "rekey respects the reversed field",
        rekey("sumtype", "Crumb::old.agda", "new.agda"),
        "Crumb::new.agda",
    )

    malformed = False
    try:
        parse("public", "no-separator-here")
    except MalformedKey:
        malformed = True
    check("malformed key REFUSES (never mis-assigns the path field)", malformed, True)

    # Every live baseline must parse at its declared arity.  A schema that drifts
    # from a gate's real key shape is the one failure that silently inverts the
    # churn verdict, so it is pinned against the real files.
    for gate, spec in SCHEMA.items():
        if not os.path.exists(spec.baseline):
            check(f"{gate}: baseline present", f"missing {spec.baseline}", "present")
            continue
        with open(spec.baseline) as fh:
            keys = [ln.strip() for ln in fh if ln.strip()]
        bad = []
        for k in keys:
            try:
                parse(gate, k)
            except MalformedKey:
                bad.append(k)
        check(f"{gate}: all {len(keys)} live baseline keys parse", bad, [])

    ok = sum(1 for _, good, _, _ in cases if good)
    for name, good, got, want in cases:
        if not good:
            print(f"  FAIL {name}\n       got  {got!r}\n       want {want!r}")
    print(f"gate_keys selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    import sys

    sys.exit(_selftest() if "--selftest" in sys.argv else _selftest())
