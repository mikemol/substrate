#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.key_spec` — the reversed gate, and what a wrong path field costs.

⚑⚑⚑ THE REVERSED CASE IS THE ONE A POSITIONAL ASSUMPTION FAILS SILENTLY. Every gate but one
spells a key path-first; the sumtype census builds `name::relpath`. Reading field 0 as the path
there treats every duplicate NAME as a path and every path as an identity — exactly backwards,
and the output still looks like keys.

⚑⚑ AND THE CONSEQUENCE IS WORSE THAN A WRONG LABEL. Identity is what tells CHURN from DEBT: a
decomposition mints a new key for a byte-identical line, and comparing by identity is what
recognises that. A mis-assigned path field makes a genuine violation look like churn — the one
error this module must never make — so a malformed key RAISES rather than being partitioned
best-effort.

⚑ THE NO-KIND CASE PROTECTS A MEASURED MISREAD. An earlier partition took the last field
unconditionally and reported *"35 kind(s), each x1"* for an arity-2 gate: the identity field, one
per key, which is the key's own name re-listed rather than a shape. A 2-field key has NO kind,
which is not the same as having one.

⚑ THE FIXTURE NAMES THE REAL IDENTIFIER IN ITS LATEX SPELLING (operator, 2026-08-31: *"use
whatever would have been used in latex in markdown"*). The Agda name is a double-struck capital,
which the linter flags as ambiguous with the Latin letter — a real hazard in source and noise in
a fixture. A made-up ASCII stand-in would have made the case stop naming the thing it came from;
the LaTeX form is the SAME identifier, written the way this corpus already writes mathematics in
prose, so the fixture keeps its referent and the linter keeps its warning where it matters.
"""

from __future__ import annotations

import sys

from substrate import key_spec

# One key per declared gate, in that gate's own spelling.
_PUBLIC = "agda/Substrate/Q/Rat.agda::\\mathbb{Q}"
_SUMTYPE = "Crumb::agda/Substrate/Category/PrimeSampledChain.agda"
_BAN = "agda/Substrate/A.agda::Substrate.Foundation.Eq::using"


def path_first_gates_parse(out: list[str]) -> int:
    """Check a path-first key splits into path and identity."""
    spec = key_spec.SCHEMA["public"]
    got = key_spec.parse(spec, _PUBLIC)
    if got != ("agda/Substrate/Q/Rat.agda", ("\\mathbb{Q}",)):
        out.append(f"selftest: the public key parsed as {got!r}")
        return 1
    return 0


def the_reversed_gate_parses(out: list[str]) -> int:
    """Check the sumtype key's PATH is field 1, not field 0.

    ⚑ THE RECORDED BACKWARDS CASE. A positional assumption here reports the type NAME as a file
    path, and the resulting churn/debt classification is inverted for every key in that gate.
    """
    spec = key_spec.SCHEMA["sumtype"]
    got = key_spec.parse(spec, _SUMTYPE)
    if got != ("agda/Substrate/Category/PrimeSampledChain.agda", ("Crumb",)):
        out.append(f"selftest: the sumtype key parsed as {got!r}")
        return 1
    return 0


def a_three_field_key_keeps_both_identity_fields(out: list[str]) -> int:
    """Check identity is every non-path field, in order."""
    spec = key_spec.SCHEMA["ban"]
    got = key_spec.identity(spec, _BAN)
    if got != ("Substrate.Foundation.Eq", "using"):
        out.append(f"selftest: the ban identity read as {got!r}")
        return 1
    return 0


def a_malformed_key_raises(out: list[str]) -> int:
    """Check a wrong field count refuses rather than partitioning best-effort.

    ⚑ SILENTLY MIS-ASSIGNING A PATH FIELD is how a real violation becomes apparent churn, so the
    honest response to an unparseable key is a refusal naming the gate and the arity.
    """
    spec = key_spec.SCHEMA["ban"]
    try:
        key_spec.parse(spec, "only::two")
    except key_spec.MalformedKeyError:
        return 0
    out.append("selftest: a malformed key parsed")
    return 1


def identity_survives_a_move(out: list[str]) -> int:
    """Check two keys differing only in path share an identity.

    ⚑ THIS IS THE WHOLE POINT OF THE PARTITION. A decomposition mints a new key for a
    byte-identical line; equal identity is what recognises the pair as churn rather than as new
    debt that blocks paydown from recording.
    """
    spec = key_spec.SCHEMA["ban"]
    moved = key_spec.rekey(spec, _BAN, "agda/Substrate/A/A.agda")
    if key_spec.identity(spec, moved) != key_spec.identity(spec, _BAN):
        out.append("selftest: a moved key lost its identity")
        return 1
    if key_spec.path_of(spec, moved) != "agda/Substrate/A/A.agda":
        out.append("selftest: rekey did not replace the path field")
        return 1
    return 0


def a_two_field_key_has_no_kind(out: list[str]) -> int:
    """Check an arity-2 gate reports no kind rather than its identity field.

    ⚑ THE MEASURED MISREAD: *"35 kind(s), each x1"* — one per key, which is the key's own name
    re-listed. No sub-kind is a fact; one-kind-per-key is an artefact of asking wrongly.
    """
    if key_spec.kind_of(key_spec.SCHEMA["public"], _PUBLIC) is not None:
        out.append("selftest: an arity-2 key reported a kind")
        return 1
    return 0


def a_three_field_key_has_a_kind(out: list[str]) -> int:
    """Check the kind is the trailing field of an arity-3 key."""
    got = key_spec.kind_of(key_spec.SCHEMA["ban"], _BAN)
    if got != "using":
        out.append(f"selftest: the ban kind read as {got!r}")
        return 1
    return 0


def an_undeclared_gate_returns_none(out: list[str]) -> int:
    """Check a gate with no schema entry is reported as undeclared, not defaulted.

    ⚑ SIX OF TEN BASELINES LACKED AN ENTRY, so a default would mis-partition exactly the
    population most in need of a correct answer.
    """
    if key_spec.spec_for("check_some_unknown_ratchet.py") is not None:
        out.append("selftest: an undeclared gate got a spec")
        return 1
    return 0


def a_declared_gate_resolves_by_filename(out: list[str]) -> int:
    """Check the short name matches the module filename a census reports."""
    got = key_spec.spec_for("check_ban_ratchet.py")
    if got is None or got.gate != "ban":
        out.append(f"selftest: check_ban_ratchet.py resolved to {got!r}")
        return 1
    return 0


_ARMS = (
    path_first_gates_parse,
    the_reversed_gate_parses,
    a_three_field_key_keeps_both_identity_fields,
    a_malformed_key_raises,
    identity_survives_a_move,
    a_two_field_key_has_no_kind,
    a_three_field_key_has_a_kind,
    an_undeclared_gate_returns_none,
    a_declared_gate_resolves_by_filename,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 2 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"key-spec selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"key-spec selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
