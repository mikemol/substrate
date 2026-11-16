# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.ratchet_key` — the ratchet key schema.

⚑ THE LOAD-BEARING CASE IS THE REVERSAL. Two declared gates put the path SECOND, and
reading field 0 as the path there would treat a duplicate name as a path and a path as an
identity — making a genuine violation look like churn, which is the one error this schema
must never make. If that case ever passes with the fields the other way round, the module
has quietly become a hardcoded split.

⚑⚑ AND THE ARITY REFUSAL IS ITS GUARD. A key with the wrong field count must raise rather
than be mis-assigned, because a silently mis-parsed key is absolution without review.

⚑ THE IDENTITY CASES ARE THE POINT OF THE WHOLE SCHEMA: identity must SURVIVE a move and
must DISTINGUISH different names. Either half alone is useless — one that never changes
absolves everything, one that always changes credits nothing.

⚑ THE FIXTURE NAMES ARE ASCII. The origin's cases used a double-struck Agda identifier
verbatim, which the linter flags as confusable with its ASCII twin; these cases are about
FIELD POSITION, so the glyph carried no weight and keeping it would trade a real property
for a decorative one.
"""

from __future__ import annotations

from substrate import ratchet_key

DECLARED_GATES = 7


def _rekey_refuses(gate: str, key: str) -> bool:
    """Report whether `rekey` refuses a malformed key."""
    try:
        ratchet_key.rekey(gate, key, "new.agda")
    except ratchet_key.MalformedKeyError:
        return True
    return False


def _parse_refuses(gate: str, key: str) -> bool:
    """Report whether `parse` refuses a key of the wrong arity."""
    try:
        ratchet_key.parse(gate, key)
    except ratchet_key.MalformedKeyError:
        return True
    return False


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── path-first grammars ──────────────────────────────────────────────────
    check(
        "public: path first",
        passed=ratchet_key.parse("public", "agda/Substrate/Q/Rat.agda::Rat")
        == ("agda/Substrate/Q/Rat.agda", ("Rat",)),
    )
    check(
        "private shares the public grammar",
        passed=ratchet_key.path_of("private", "agda/Substrate/A.agda::foo")
        == "agda/Substrate/A.agda",
    )

    # ── THE REVERSAL — path SECOND ───────────────────────────────────────────
    check(
        "sumtype: path SECOND, identity leading",
        passed=ratchet_key.parse("sumtype", "Crumb::agda/Substrate/Category/Chain.agda")
        == ("agda/Substrate/Category/Chain.agda", ("Crumb",)),
    )
    check(
        "discharge is reversed too",
        passed=ratchet_key.parse("discharge", "Carrier::Substrate.Mod")
        == ("Substrate.Mod", ("Carrier",)),
    )

    # ── three-field grammars ─────────────────────────────────────────────────
    check(
        "ban: 3 fields, identity keeps BOTH non-path fields",
        passed=ratchet_key.parse("ban", "agda/Substrate/A.agda::Substrate.Foundation.Eq::using")
        == ("agda/Substrate/A.agda", ("Substrate.Foundation.Eq", "using")),
    )
    check(
        "claims: 3 fields",
        passed=ratchet_key.parse("claims", "agda/Substrate/A.agda::shim::self")
        == ("agda/Substrate/A.agda", ("shim", "self")),
    )

    # ── identity: the two halves that make it useful ─────────────────────────
    check(
        "identity SURVIVES a move",
        passed=ratchet_key.identity("public", "agda/Substrate/Q/Rat.agda::Rat")
        == ratchet_key.identity("public", "agda/Substrate/Q.agda::Rat"),
    )
    check(
        "identity DISTINGUISHES different names",
        passed=ratchet_key.identity("public", "agda/Substrate/A.agda::X")
        != ratchet_key.identity("public", "agda/Substrate/A.agda::Y"),
    )

    # ── rekey ────────────────────────────────────────────────────────────────
    check(
        "rekey rebuilds the moved key",
        passed=ratchet_key.rekey(
            "public", "agda/Substrate/Q.agda::Rat", "agda/Substrate/Q/Rat.agda"
        )
        == "agda/Substrate/Q/Rat.agda::Rat",
    )
    # ⚑ And it must respect the reversed field, or a rekey writes the path into the
    # identity slot and mints a key naming a violation that does not exist.
    check(
        "rekey respects the reversed field",
        passed=ratchet_key.rekey("sumtype", "Crumb::old.agda", "new.agda") == "Crumb::new.agda",
    )

    # ── THE ARITY REFUSAL ────────────────────────────────────────────────────
    check("too few fields refuses", passed=_parse_refuses("ban", "only::two"))
    check("too many fields refuses", passed=_parse_refuses("public", "a::b::c"))
    check("a rekey of a malformed key refuses too", passed=_rekey_refuses("public", "a::b::c"))

    # ── the schema is complete and self-consistent ───────────────────────────
    check("every declared gate is in GATES", passed=len(ratchet_key.GATES) == DECLARED_GATES)
    check(
        "every spec's path_field is within its arity",
        passed=all(0 <= s.path_field < s.arity for s in ratchet_key.SCHEMA.values()),
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
