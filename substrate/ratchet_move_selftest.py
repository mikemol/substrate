# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.ratchet_move` — a gate's `key_move`, derived not hand-written.

⚑⚑⚑ THE REVERSAL CASE IS WHY THIS MODULE EXISTS, so it goes first. The live hand-written
lambda is `k.split("::", 1)[1]`, which is right for a path-first key and returns the PATH as
the identity for `sumtype`'s `name::relpath`. A case that only checked path-first grammars
would pass on the exact copy-paste this replaces.

⚑⚑ AND THE TWO ERROR DIRECTIONS ARE NOT SYMMETRIC. Reporting churn as genuine debt costs an
operator one read; absolving genuine debt as churn writes an unrecoverable absolution into a
paydown-only baseline. So the cases assert that DIFFERENT violations never share a move
token, more carefully than that matching ones do.

⚑ THE MOVE TOKEN'S EXACT SPELLING IS NOT ASSERTED, only that it AGREES across a relocation
and DIFFERS across a genuine violation. Pinning the string would freeze an internal join
format that nothing outside this module reads.
"""

from __future__ import annotations

from substrate import ratchet_move

# One key per gate, and the same violation after its file was decomposed.
_MOVES = [
    (
        "public",
        "agda/Substrate/Quotient.agda::Substrate.Bar",
        "agda/Substrate/Quotient/Canonical.agda::Substrate.Bar",
    ),
    ("private", "agda/Substrate/Foo.agda::helper", "agda/Substrate/Foo/Helper.agda::helper"),
    (
        "carrier-locality",
        "agda/Substrate/Nat.agda::_div-suc_",
        "agda/Substrate/Nat/DivSuc.agda::_div-suc_",
    ),
    (
        "ban",
        "agda/Substrate/Foo.agda::Substrate.Bar::using",
        "agda/Substrate/Foo/Leaf.agda::Substrate.Bar::using",
    ),
    ("claims", "agda/Substrate/Foo.agda::shim::self", "agda/Substrate/Foo/Leaf.agda::shim::self"),
    # ⚑ REVERSED GRAMMAR — `name::relpath`. The hand-written lambda gets this backwards.
    ("sumtype", "Crumb::agda/Substrate/Foo.agda", "Crumb::agda/Substrate/Foo/Crumb.agda"),
    ("discharge", "Carrier::agda/Substrate/Foo.agda", "Carrier::agda/Substrate/Foo/Carrier.agda"),
]


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── a relocation is recognised, for every declared gate ──────────────────
    for gate, old, new in _MOVES:
        move = ratchet_move.key_move(gate)
        check(
            f"{gate}: a decomposed file's key keeps its move token", passed=move(old) == move(new)
        )

    # ── and the reversal is not merely handled, it is CHECKED ────────────────
    # ⚑ The failing spelling, asserted directly: were the path field read as field 0
    # for sumtype, the move token would BE the path and two relocations of different
    # names would collide.
    sumtype = ratchet_move.key_move("sumtype")
    check(
        "sumtype: the move token is the NAME, not the path",
        passed=sumtype("Crumb::a/B.agda") != sumtype("Other::a/B.agda"),
    )
    public = ratchet_move.key_move("public")
    check(
        "public: the move token is the OPENED name, not the path",
        passed=public("a/B.agda::Substrate.X") != public("a/B.agda::Substrate.Y"),
    )

    # ── a genuine violation never pairs with a different one ─────────────────
    ban = ratchet_move.key_move("ban")
    check(
        "ban: a different directive is a different violation",
        passed=ban("a/B.agda::Substrate.X::using") != ban("a/B.agda::Substrate.X::hiding"),
    )
    check(
        "ban: a different imported module is a different violation",
        passed=ban("a/B.agda::Substrate.X::using") != ban("a/B.agda::Substrate.Y::using"),
    )

    # ── a malformed key maps to itself rather than aborting the gate ─────────
    # ⚑ THE CONSERVATIVE DIRECTION: it pairs with nothing, so it stays reported as
    # growth. Absolving it would be the unrecoverable error.
    check(
        "a malformed key maps to itself", passed=ban("no-separators-here") == "no-separators-here"
    )
    check("and so pairs with no other malformed key", passed=ban("bad-one") != ban("bad-two"))

    # ── an undeclared gate refuses at construction ───────────────────────────
    try:
        ratchet_move.key_move("not-a-gate")
    except KeyError:
        check("an undeclared gate refuses", passed=True)
    else:
        check("an undeclared gate refuses", passed=False)

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
