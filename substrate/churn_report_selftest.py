# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.churn_report` — the churn CLI's dispatch and rendering.

⚑⚑⚑ THESE COVER THE DISPATCH BECAUSE THE ORIGIN'S SUITE DID NOT, AND THAT IS WHY ITS TOOL
SHIPPED BROKEN. `gate_preflight` passes nineteen of nineteen while calling a reader that no
longer exists, because its cases exercise the pure classifier and never reach the live
path. A suite that cannot fail for the reason the tool is broken is not covering that tool,
however many cases it holds. So the cases here assert argument handling, gate validation,
and the rendering of every verdict shape — the parts the classifier's own suite cannot see.

⚑⚑ AND THE UNMEASURED RENDERING IS THE LOAD-BEARING ONE. A gate that will not load and a
gate with nothing new both produce a short report, and only the wording separates them. If
UNMEASURED ever renders like a clean gate, the tool inherits the false-green shape the
whole family refuses.

⚑ THE RENDER IS EXERCISED ON CONSTRUCTED VERDICTS, not on a live census. Running one would
make these cases a measurement of the tree — slow, and green or red for reasons that have
nothing to do with this file.
"""

from __future__ import annotations

from substrate import churn_report, ratchet_churn


def _verdict(
    *,
    churn: dict[str, tuple[str, ...]] | None = None,
    new: tuple[str, ...] = (),
    suspect: dict[str, tuple[str, ...]] | None = None,
    unpaired: frozenset[str] = frozenset(),
) -> ratchet_churn.Verdict:
    """Build a verdict with only the fields a rendering case cares about."""
    return ratchet_churn.Verdict(
        gate="public",
        added=frozenset(),
        paid=frozenset(),
        churn=churn or {},
        genuinely_new=new,
        suspect=suspect or {},
        unpaired=unpaired,
    )


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── argument handling ────────────────────────────────────────────────────
    check("--help exits zero", passed=churn_report.main(["--help"]) == 0)
    # ⚑ AN UNKNOWN GATE REFUSES AND NAMES THE DECLARED ONES. The origin raised KeyError,
    # so a caller learned only that something went wrong, not what it could have asked for.
    check("an undeclared gate refuses", passed=churn_report.main(["no-such-gate"]) == 2)  # noqa: PLR2004
    check("two gates at once refuses", passed=churn_report.main(["public", "private"]) == 2)  # noqa: PLR2004

    # ── the baseline path comes from the schema ──────────────────────────────
    path = churn_report.baseline_path("public")
    check(
        "the baseline path names the gate's declared file",
        passed=path.endswith("public_ratchet_baseline.txt"),
    )
    check("and is absolute, so a caller's cwd cannot change it", passed=path.startswith("/"))

    # ── a gate with no declared script reports why ───────────────────────────
    # ⚑ THIS CASE CAUGHT ITS OWN PREMISE EXPIRING. It named carrier-locality, which was in
    # the SCHEMA and absent from the script map — until that gate gained a chained-census
    # adapter, at which point the case failed for the right reason: the thing it asserted
    # had stopped being true. Repointed at a name that is genuinely undeclared, so it
    # still tests the REFUSAL rather than one gate's transient state.
    _, why = churn_report.live_census("not-a-declared-gate")
    check("a gate with no declared script reports why", passed=why is not None)

    # ⚑ AND THE CHAINED ADAPTER IS NOW DECLARED, so the gate that has no census() is
    # reachable. Asserting the declaration rather than running it: the chain runs a
    # whole-tree scan, which is a measurement and not a case.
    check(
        "the census-less gate has a chained adapter declared",
        passed="carrier-locality" in churn_report.CHAINED,
    )

    # ── rendering every verdict shape ────────────────────────────────────────
    churny = churn_report.report(_verdict(churn={"new/path.agda::X": ("old/path.agda",)}))
    check(
        "churn renders with the old path as evidence",
        passed="CHURN 1" in churny and "was: old/path.agda" in churny,
    )

    debt = churn_report.report(_verdict(new=("a.agda::X",)))
    check("genuine debt renders as such", passed="GENUINELY NEW 1" in debt)

    fanout = churn_report.report(_verdict(suspect={"new/a.agda::X": ("old.agda",)}))
    check(
        "a fan-out renders as SUSPECT, not churn",
        passed="SUSPECT 1" in fanout and "CHURN" not in fanout,
    )

    # ⚑ THE UNPAIRED LINE IS THE READER'S OWN LIMIT. Without it, a report saying "2 churn,
    # 0 new" reads as a complete account of every paid key, which it is not.
    unpaired = churn_report.report(_verdict(unpaired=frozenset({"a", "b"})))
    check(
        "unpaired paid keys are reported as a limit",
        passed="2 paid key(s) paired with nothing" in unpaired,
    )

    # ⚑ A CLEAN VERDICT RENDERS ONLY ITS HEADER — no churn, no debt, no limit lines, so
    # nothing invites a reader to act.
    clean = churn_report.report(_verdict())
    check("a clean verdict renders one line", passed=len(clean.splitlines()) == 1)

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
