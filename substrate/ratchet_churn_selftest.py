# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.ratchet_churn` — the churn-versus-real-debt classifier.

⚑ THE LOAD-BEARING CASE IS THE FALSE ABSOLUTION. A shared identity appears in hundreds of
files, so pairing on identity ALONE would call a genuinely-new violation churn because some
unrelated file carrying that identity had moved. The origin measured that on its first live
run. If the unrelated-move case ever passes as churn, this classifier has become a rubber
stamp over exactly the debt it exists to surface.

⚑⚑ AND AN UNPARSEABLE KEY MUST COUNT AS NEW. Absolving a key nobody could read is the same
failure arriving through the error path rather than the happy one.

⚑ THE ORIGIN'S SUITE PASSED WHILE ITS TOOL WAS BROKEN, because the cases covered this pure
half and never reached the live read. That is not an argument against covering the pure
half — it is an argument for saying so: these cases assert the CLASSIFIER, and nothing here
witnesses that a caller can read a baseline.
"""

from __future__ import annotations

from substrate import ratchet_churn


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── moved_from: the two decomposition shapes ─────────────────────────────
    check(
        "a monolith split into its own directory is a move",
        passed=ratchet_churn.moved_from("agda/Substrate/Q.agda", "agda/Substrate/Q/Rat.agda"),
    )
    check(
        "a rename within a directory is a move",
        passed=ratchet_churn.moved_from("agda/Substrate/A.agda", "agda/Substrate/B.agda"),
    )
    check(
        "a path is not a move from itself",
        passed=not ratchet_churn.moved_from("a/X.agda", "a/X.agda"),
    )
    # ⚑ THE PREDICATE THAT PREVENTS FALSE ABSOLUTION: an unrelated directory is not a move.
    check(
        "an unrelated directory is NOT a move",
        passed=not ratchet_churn.moved_from("agda/Substrate/A.agda", "agda/Other/B.agda"),
    )

    # ── churn: a real decomposition ──────────────────────────────────────────
    base = {"agda/Substrate/Q.agda::Rat"}
    cur = {"agda/Substrate/Q/Rat.agda::Rat"}
    verdict = ratchet_churn.classify("public", base, cur)
    check("a decomposition reads as churn, not debt", passed=verdict.queue == 0)
    check(
        "and the churn names the old path it paired with",
        passed=verdict.churn.get("agda/Substrate/Q/Rat.agda::Rat") == ("agda/Substrate/Q.agda",),
    )
    check("and the paid key is consumed, not left unpaired", passed=verdict.unpaired == frozenset())

    # ── THE FALSE ABSOLUTION — the case the origin measured ──────────────────
    # ⚑ A shared identity moved SOMEWHERE ELSE must not absolve a new violation here.
    shared_base = {"agda/Substrate/Old.agda::Substrate.Foundation.Eq::using"}
    shared_cur = {"agda/Elsewhere/New.agda::Substrate.Foundation.Eq::using"}
    shared = ratchet_churn.classify("ban", shared_base, shared_cur)
    check("a same-identity key in an UNRELATED path is genuinely new", passed=shared.queue == 1)
    check("and is not recorded as churn", passed=shared.churn == {})
    # ⚑ The paid key stays UNPAIRED, which is how a reader sees the move was not evidenced.
    check("the unmatched paid key is reported unpaired", passed=len(shared.unpaired) == 1)

    # ── an unparseable key is never absolved ─────────────────────────────────
    bad = ratchet_churn.classify("public", set(), {"no-separator-here"})
    check("an unparseable added key counts as genuinely new", passed=bad.queue == 1)

    # ── strict: the fan-out asymmetry ────────────────────────────────────────
    # ⚑ One old path, two plausible new ones: at most one is the move, so `strict`
    # refuses to absolve both.
    fan_base = {"agda/Substrate/Q.agda::Rat"}
    fan_cur = {"agda/Substrate/Q/A.agda::Rat", "agda/Substrate/Q/B.agda::Rat"}
    lax = ratchet_churn.classify("public", fan_base, fan_cur)
    strict = ratchet_churn.classify("public", fan_base, fan_cur, strict=True)
    check("without strict, a fan-out reads as churn", passed=len(lax.churn) == 2)  # noqa: PLR2004
    check(
        "under strict, the fan-out is SUSPECT instead",
        passed=len(strict.suspect) == 2 and strict.churn == {},
    )  # noqa: PLR2004

    # ── creditable: what a paydown-only BASELINE may absolve ─────────────────
    # ⚑⚑⚑ THE FAN-OUT IS CHURN AND IS NOT CREDITABLE, and holding both at once is the
    # whole point of the property. A reader needs to know these two keys are the same
    # violation relocated; a BASELINE may not absolve either, because one retirement
    # licenses exactly one move and nothing says which. Reporting only the first number
    # made the classifier look like it disagreed with the ratchet.
    check(
        "a fan-out is churn but NOT creditable", passed=len(lax.churn) == 2 and lax.creditable == {}
    )  # noqa: PLR2004
    # ⚑ A 1:1 move IS creditable, and names the retired key — not its path. A credit
    # consumes a specific baseline line, so a path would not identify what to remove.
    check(
        "a 1:1 move is creditable and names the retired KEY",
        passed=verdict.creditable
        == {"agda/Substrate/Q/Rat.agda::Rat": "agda/Substrate/Q.agda::Rat"},
    )
    # ⚑⚑⚑ THE UNRELATED MOVE IS NOT CHURN AND IS STILL CREDITABLE, AND THAT DIVERGENCE IS
    # REAL RATHER THAN A DEFECT IN EITHER. This case was first written asserting the
    # opposite and FAILED, which is how the divergence was found rather than assumed.
    # `split_moves` — the authority a baseline actually obeys — pairs on IDENTITY plus
    # one-to-one and applies NO path test, so a lone same-identity pair credits however far
    # apart the files sit. `churn` refuses it because a reader asking "did this relocate"
    # is owed path evidence. Both are right for their own question, and a case asserting
    # they agree would be asserting a property the ratchet has never had.
    check(
        "an unrelated same-identity 1:1 pair IS creditable, though not churn",
        passed=shared.churn == {} and len(shared.creditable) == 1,
    )
    # ⚑ N→1 IS A GENUINE PAYDOWN AND MUST STAY VISIBLE AS ONE, never collapsed into a
    # move that would consume the wrong retirement.
    merge = ratchet_churn.classify(
        "public",
        {"agda/Substrate/Q/A.agda::Rat", "agda/Substrate/Q/B.agda::Rat"},
        {"agda/Substrate/Q.agda::Rat"},
    )
    check("an N→1 merge credits nothing", passed=merge.creditable == {})

    # ── a clean run says nothing happened ────────────────────────────────────
    same = ratchet_churn.classify("public", base, base)
    check("no change yields no queue and no churn", passed=same.queue == 0 and same.churn == {})

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
