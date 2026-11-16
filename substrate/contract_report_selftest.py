# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.contract_report` — the mode-contract audit's rendering.

⚑⚑⚑ THE EMPTY-ROSTER CASE IS THE ITEM. Zero violations over zero contracts and zero violations
over many render identically as a count, so a gate reporting the first as a pass is green
exactly when it checked nothing. The verdict must be UNMEASURED, and a case that only asserted
"no failures means clean" would pass on the broken reading.

⚑⚑ AND UNKNOWN IS NOT FAILURE. A row this reader could not resolve is a fact about the reader;
scoring it as debt reports a blind spot as the subject's problem. `ok is False` and `not ok`
differ exactly on that row, which is why the predicate is spelled the strict way.

⚑ THE THREE DEBTS STAY APART. A contract violation, a roster disagreement and an opt collision
have different remedies, and summing them would make a paydown of one read as progress on all
three — the origin's own comments record that reasoning, and these cases hold it.
"""

from __future__ import annotations

from substrate import contract_report as cr

# ⚑ `ok` IS NAMED AT EVERY CONSTRUCTION. A positional boolean beside a string is transposable,
# and a transposed verdict reads entirely plausible — flag and reason stay right while the
# pass/fail inverts.
_OK = cr.Row("--alpha", "declares and honours", ok=True)
_BAD = cr.Row("--beta", "declares and does not", ok=False)
_UNKNOWN = cr.Row("--gamma", "could not resolve", ok=None)
_ROSTER = cr.Row("--delta", "dispatched but undeclared", ok=False)


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the verdict, including the case that must not read as a pass ────────
    check("all honoured is clean", passed=cr.verdict([_OK]) == cr.CLEAN)
    check("any violation fails", passed=cr.verdict([_OK, _BAD]) == cr.FAILED)
    # ⚑ THE LOAD-BEARING BRANCH. An empty roster measured nothing.
    check("an empty roster is UNMEASURED, not clean", passed=cr.verdict([]) == cr.UNMEASURED)
    check(
        "and UNMEASURED is distinct from both other codes",
        passed=len({cr.CLEAN, cr.FAILED, cr.UNMEASURED}) == 3,
    )  # noqa: PLR2004

    # ── unknown is not failure ──────────────────────────────────────────────
    # ⚑ `not ok` WOULD SCORE THIS AS A VIOLATION. The strict test is what keeps a reader's
    # blind spot from being reported as the subject's debt.
    check(
        "an unknown row does not fail the verdict", passed=cr.verdict([_OK, _UNKNOWN]) == cr.CLEAN
    )
    check(
        "and is not counted among the failures", passed=cr.failures([_OK, _UNKNOWN, _BAD]) == [_BAD]
    )
    check("while its mark says UNK rather than FAIL", passed=_UNKNOWN.mark.strip() == "UNK")
    check("and a failing row marks FAIL", passed=_BAD.mark == "FAIL")

    # ── the two debts are partitioned, not summed ──────────────────────────
    contract, roster = cr.partition([_OK, _BAD, _ROSTER], {"--alpha", "--beta"})
    check("declaring modes fall in the contract half", passed=len(contract) == 2)  # noqa: PLR2004
    # ⚑ A ROSTER ROW HAS NO DECLARED CONTRACT TO QUOTE — assuming it did crashed the origin's
    # printer on its first run, on precisely the rows that were the finding.
    check("an undeclared flag falls in the roster half", passed=roster == [_ROSTER])

    # ── rendering ───────────────────────────────────────────────────────────
    text = cr.render([_OK, _BAD, _ROSTER], {"--alpha", "--beta"}, [])
    check("the rendering names each flag", passed="--alpha" in text and "--beta" in text)
    check(
        "and reports the roster disagreement on its own line",
        passed="roster/dispatch disagreement" in text,
    )

    # ⚑ COLLISIONS ARE REPORTED AND NOT SCORED — residue somebody already adjudicated.
    with_coll = cr.render([_OK], {"--alpha"}, [("--x", ["--y"], False, "benign, same meaning")])
    check("a collision is reported", passed="--x" in with_coll)
    check("and named as benign residue rather than a failure", passed="BENIGN" in with_coll)

    # ⚑ AND AN EMPTY ROSTER SAYS SO IN THE TEXT, not only in the exit code — a reader
    # looking at output must not have to infer it from silence.
    check(
        "an empty rendering says it measured nothing",
        passed="measured NOTHING" in cr.render([], set(), []),
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
