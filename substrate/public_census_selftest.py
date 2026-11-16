# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.public_census` — every `open … public` as debt.

⚑⚑⚑ THE STATEMENT-NOT-LINE CASES ARE LOAD-BEARING. Agda accepts import directives across
continuation lines, so `public` may sit on the line after the `open`. A line-anchored scan finds
the `open`, misses the keyword, and reports a real re-export as clean — which once let a hundred
and fifty-eight narrowed re-exports escape this census entirely. Both spellings are pinned.

⚑⚑ AND THE ROOT-MODULE CASE RECORDS A LIVE DEFECT IN THE GATE THIS REPLACES. The origin
enumerates from `agda/Substrate`, so `agda/Substrate.agda` — the tree's top-level module, one
directory ABOVE that root — is outside its census by construction, and the wholesale re-export
it carries has never been in the baseline. The extraction walks `agda/` and finds it. That is a
SCOPE defect, not a predicate defect, and a case asserting the key is present is what keeps a
future narrowing from silently reintroducing it.

⚑ THE PREDICATE CASES RUN ON CONSTRUCTED LINES, not on the tree. Running the corpus census to
assert a three-line rule would make these cases a measurement — slow, and red for reasons that
have nothing to do with this file.
"""

from __future__ import annotations

from substrate import public_census


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the predicate: what counts as a re-export ────────────────────────────
    plain = ["open import Substrate.Foo public"]
    check(
        "a wholesale re-export is debt",
        passed=public_census.reexports_in("a/B.agda", plain) == {"a/B.agda::Substrate.Foo"},
    )

    # ⚑ A NARROWED RE-EXPORT IS STILL DEBT. Counting only wholesale ones made narrowed ones
    # INVISIBLE rather than exempt — absent from the baseline entirely.
    narrowed = ["open import Substrate.Foo using (x) public"]
    check(
        "a narrowed re-export is also debt",
        passed=len(public_census.reexports_in("a/B.agda", narrowed)) == 1,
    )

    check(
        "an ordinary open is not debt",
        passed=public_census.reexports_in("a/B.agda", ["open import Substrate.Foo"]) == set(),
    )

    # ⚑ THE BUILTIN EXCLUSION — the one the policy licenses, since there is no owner to bind at.
    builtin = ["open import Agda.Primitive public"]
    check(
        "the compiler builtin is excluded",
        passed=public_census.reexports_in("a/B.agda", builtin) == set(),
    )

    # ── STATEMENT, NOT LINE ─────────────────────────────────────────────────
    # ⚑ `public` ON A CONTINUATION LINE. The head alone shows a clean open.
    wrapped = ["open import Substrate.Foo", "  using (x)", "  public"]
    check(
        "a `public` on a continuation line is found",
        passed=public_census.reexports_in("a/B.agda", wrapped) == {"a/B.agda::Substrate.Foo"},
    )

    # ⚑ AND THE STATEMENT ENDS AT THE DEDENT, so a LATER file-level `public` cannot be
    # attributed to an earlier open. Without this the scan would over-report as badly as the
    # line-anchored one under-reports.
    separate = ["open import Substrate.Foo", "  using (x)", "record R : Set where public"]
    check(
        "a dedented line does not extend the statement",
        passed=public_census.reexports_in("a/B.agda", separate) == set(),
    )

    # ⚑ A NAME CONTAINING THE KEYWORD IS NOT THE KEYWORD.
    lookalike = ["open import Substrate.PublicApi"]
    check(
        "a module named after the keyword is not debt",
        passed=public_census.reexports_in("a/B.agda", lookalike) == set(),
    )

    # ── opened_by narrows the match, and says so ────────────────────────────
    check(
        "opened_by names what is opened",
        passed=public_census.opened_by("open import Substrate.Foo") == "Substrate.Foo",
    )
    check(
        "and returns None for a line that opens nothing",
        passed=public_census.opened_by("module M where") is None,
    )

    # ── the live tree: the root module the origin cannot see ────────────────
    keys, why = public_census.census_or_why()
    if why is not None:
        check(f"the census can be taken (got: {why})", passed=False)
        return out

    check("the census is non-empty", passed=bool(keys))
    # ⚑⚑ THE DEFECT THIS EXTRACTION FOUND. `agda/Substrate.agda` is the top-level module,
    # ABOVE the origin's `agda/Substrate` enumeration root, and its wholesale re-export has
    # never been censused. Asserting the KEY, not a count, so the case names what it protects.
    check(
        "the tree's root module is censused",
        passed="agda/Substrate.agda::Substrate.Cocycle" in keys,
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
