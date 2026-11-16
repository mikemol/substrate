# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.private_census` — the hidden-definition census.

⚑⚑⚑ THE INDENT CASE IS THE ONE THAT MATTERS, because its absence is the bug this arc keeps
making. The declaration scanners expect column-0 declarations and a `private` block's contents
are indented, so a census that forgets to dedent reports ZERO from a tree full of real blocks —
which reads as a clean gate. It happened twice here and three more times elsewhere in the arc.
Both directions are pinned: dedented text finds the helper, and the same text UNDEDENTED does
not, so a future edit cannot quietly drop the dedent and still pass.

⚑⚑ AND THE LEVEL IDIOM MUST CONTRIBUTE NOTHING. `private variable` is a binding form, not a
hidden helper; censusing it would bank false keys into a paydown-only baseline, where they
could never legitimately be paid. Both spellings are covered — the one-line and the multi-line
`private` / `variable` — because an earlier classifier matched the second as a helper block.

⚑ THE BLOCK EXTRACTION IS TESTED WITHOUT LOADING A SCANNER. `block` is pure text handling, so
its cases need no scratch tool and stay fast; the scanner-dependent half is exercised by the
one case that loads for real, and it SAYS SO when the load fails rather than passing vacuously.
"""

from __future__ import annotations

from substrate import private_census, scratch_module


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── block extraction: pure, no scanner needed ────────────────────────────
    src = ("module M where\nprivate\n  helper : Set → Set\n  helper x = x\n").splitlines()
    blk = private_census.block(src, 1)
    check("the block holds the indented run under `private`", passed=len(blk) == 2)  # noqa: PLR2004
    # ⚑ THE DEDENT, ASSERTED DIRECTLY. This is the property whose absence read as a clean tree.
    check("and it is DE-INDENTED to column 0", passed=bool(blk) and not blk[0].startswith(" "))

    # ⚑ A following column-0 line ENDS the block; without this the census would absorb
    # whatever follows and attribute unrelated definitions to the private block.
    two = ("private\n  hidden : Set\npublic-thing : Set\n").splitlines()
    check("a column-0 line ends the block", passed=private_census.block(two, 0) == ["hidden : Set"])

    # ⚑ A blank line does NOT end it — a helper separated by whitespace is still hidden.
    spaced = ("private\n  a : Set\n\n  b : Set\n").splitlines()
    check("a blank line does not end the block", passed=len(private_census.block(spaced, 0)) == 3)  # noqa: PLR2004

    # ── the regex admits both `private` spellings ────────────────────────────
    check(
        "a bare `private` opens a block", passed=private_census.PRIVATE.match("private") is not None
    )
    check(
        "an indented `private` opens a block",
        passed=private_census.PRIVATE.match("  private") is not None,
    )
    # ⚑ `privately` is not `private` — a prefix match here would census unrelated names.
    check(
        "a longer word starting with `private` does not",
        passed=private_census.PRIVATE.match("privateer : Set") is None,
    )

    # ── the scanner-dependent half, loaded for real ──────────────────────────
    scanner, why = scratch_module.scratch_module("split_lemmas")
    if scanner is None:
        # ⚑ SAID OUT LOUD, NOT SKIPPED. A case that vanishes when its dependency is
        # missing reports the same green as one that ran.
        check(f"split_lemmas loads (got: {why})", passed=False)
        return out

    check(
        "an INDENTED helper inside `private` is seen",
        passed="helper" in private_census.names_in(scanner, blk),
    )
    # ⚑ THE SAME TEXT UNDEDENTED IS INVISIBLE — this is WHY `block` dedents.
    check(
        "without the dedent the same helper is invisible",
        passed="helper" not in private_census.names_in(scanner, src[2:]),
    )

    # ⚑ THE LEVEL IDIOM, BOTH SPELLINGS, CONTRIBUTES NOTHING.
    one_line = ("module M where\nprivate variable a b c : Level\n").splitlines()
    check(
        "`private variable` contributes no keys",
        passed=private_census.names_in(scanner, private_census.block(one_line, 1)) == set(),
    )
    multi = ("module M where\nprivate\n  variable\n    A : Set\n").splitlines()
    check(
        "the multi-line `private` / `variable` idiom contributes no keys",
        passed=private_census.names_in(scanner, private_census.block(multi, 1)) == set(),
    )

    # ── keys carry the relpath, which is what makes them census keys ─────────
    keys = private_census.keys_in(scanner, "agda/Substrate/M.agda", src)
    check("a key is `relpath::name`", passed=keys == {"agda/Substrate/M.agda::helper"})

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
