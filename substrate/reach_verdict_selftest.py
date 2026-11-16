#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.reach_verdict` — every kind it can return, and the measured one.

⚑⚑ THE `bibstruct` CASE IS THE ONE THAT MATTERS, because it is the one that was MEASURED. A
raw `shed >= lost` compare refused an honest deletion — 56 of 96 call sites removed, 57 cases
genuinely gone — and the starve harness caught it. Every other arm here would pass against a
classifier that lost the slack calibration; this one would not.

⚑⚑⚑ AND THIS SUITE ITSELF HAD NEVER RUN, WHICH IS THE ⟡the-stranded-extraction FAILURE. It was
written calling `reach_verdict.reach_verdict(label, ran, static, base) -> (kind, detail)` — the
monolith's private signature, transcribed rather than read off the module that actually landed,
whose API is `classify(label, Reading, baseline) -> Verdict`. Every arm raised `AttributeError`
at the first call. **A case that has never executed is a case in name only**, and the stranding
is what kept anyone from finding out: an extracted module with no consumer is never imported,
and a suite nobody dispatches is never run. The green a suite prints is a fact about the run
that produced it, and there had been none.

⚑ NO AGREEMENT ARM HERE, DELIBERATELY. Comparing against the pre-split classifier means running
it as a subprocess (it lives in an unpackaged 1832-finding file, so importing it yields `Any`),
and that needs an `S603` exemption. A per-file exemption over a file that also holds unit cases
would grant it to both responsibilities — the shape this repo retires. The comparison belongs
with the other cross-implementation checks, in `promote_agree`, which owns that exemption
because running the prior implementation is its ONE job.

⚑⚑ THE BOUNDARY ARMS ARE INHERITED FROM `scripts/run_selftests._selftest`, whose copies go with
the monolith's private classifier when it is trimmed. They are carried here rather than dropped:
a case retired along with the duplicate it tested is coverage lost silently, which is exactly
the `deleted`-vs-`shrank` distinction this module was built to make visible.
"""

from __future__ import annotations

import sys

from substrate.reach_verdict import (
    DELETED,
    GREW,
    HELD,
    NEW,
    SHRANK,
    UNKNOWN,
    Reading,
    advanced,
    classify,
    may_advance,
    regressions,
)

# The baseline the cases are read against: {label: (reached, static)}.
_BASE: dict[str, Reading] = {
    "a.py": Reading(50, 48),
    "bib.py": Reading(97, 96),
    "u.py": Reading(12, None),
    # ⚑ A SUITE WITH NO LOOPS RECORDS (N, N). It is here so the zero-slack arm has a row whose
    # slack really is zero — `a.py` records (50, 48) and carries a slack of 2, which is enough
    # to reclassify a one-site-short drop as `deleted`. The first cut of that arm used `a.py`
    # and read `deleted`, so the case that was supposed to prove the allowance is per-suite was
    # instead measuring another suite's inflation.
    "flat.py": Reading(40, 40),
}

# (label, key, ran, static, expected kind)
_CASES: tuple[tuple[str, str, int | None, int | None, str], ...] = (
    ("a first sighting is recorded, never refused", "new.py", 10, 10, NEW),
    ("reaching more advances the ratchet", "a.py", 60, 50, GREW),
    ("unchanged holds", "a.py", 50, 48, HELD),
    # ⚑ THE DEFECT THE GATE EXISTS FOR: fewer cases reached, the source still holds them.
    ("fewer reached with the cases still present REFUSES", "a.py", 40, 48, SHRANK),
    # ⚑ AN UNCOUNTABLE SOURCE CANNOT DISTINGUISH fewer-RAN from fewer-EXIST, and saying so is
    # what keeps `census-green-is-a-fact-about-the-census` off the gate itself.
    ("an uncountable source is UNKNOWN, not a pass", "a.py", 40, None, UNKNOWN),
    ("a reading with no total is UNKNOWN", "a.py", None, 48, UNKNOWN),
    # ⚑ AND AN UNCOUNTABLE *RECORDED* ROW IS EQUALLY UNKNOWN — the ignorance can sit on either
    # side of the compare, and only one of the two was ever pinned.
    ("a drop against an uncountable recorded row is UNKNOWN", "u.py", 5, 5, UNKNOWN),
    # ⚑ SHEDDING MORE SITES THAN CASES LOST IS STILL DELETION — a loop-registered case makes
    # one site worth several, so the inequality is `>=`, never `==`.
    ("shedding MORE call sites than cases lost is still deletion", "bib.py", 90, 70, DELETED),
    # ⚑ AND SHEDDING FEWER IS NOT. A partial explanation is not an explanation.
    ("shedding FEWER sites than cases lost does NOT excuse the drop", "bib.py", 81, 95, SHRANK),
    # ⚑⚑ THE SLACK CANNOT SWALLOW A LOSS NOTHING WAS SHED FOR. `bib.py`'s slack is ONE case; a
    # 57-case drop with every call site still standing is still refused, which is the property
    # that keeps the allowance from becoming a hole.
    ("...and the slack cannot excuse a loss nothing was shed for", "bib.py", 40, 96, SHRANK),
    # ⚑ THE ALLOWANCE IS EXACT, NOT A MARGIN AROUND THE INFLATION. One case past it refuses,
    # so the boundary is asserted rather than assumed.
    ("the allowance is exact: one case past it still REFUSES", "bib.py", 39, 40, SHRANK),
    # ⚑ A 1:1 SUITE RECORDS (N, N), SO ITS SLACK IS ZERO AND NOTHING IS LOOSENED FOR IT. The
    # allowance is derived per suite from its OWN recorded pair, never a global fudge factor —
    # there is no number here to go stale.
    ("a 1:1 suite gets NO slack — one site short is still SHRANK", "flat.py", 30, 31, SHRANK),
)

# ⚑ THE MEASURED ROW. `bibstruct` recorded (97 reached, 96 sites); deleting 56 sites removes
# 57 cases. slack = 97-96 = 1, shed = 56, explained = 57 >= lost = 57 — it passes by exactly
# the loop inflation the recorded pair calibrates.
_BIB = ("bib.py", 40, 40, DELETED)


def semantics(out: list[str]) -> int:
    """Check every kind the classifier can return."""
    bad = 0
    for label, key, ran, static, want in _CASES:
        got = classify(key, Reading(ran, static), _BASE)
        if got.kind != want:
            out.append(f"selftest: {label}: expected {want!r}, got {got.kind!r}")
            bad += 1
    return bad


def loop_slack(out: list[str]) -> int:
    """Check an honest deletion passes by the recorded loop slack.

    ⚑ WITHOUT THE SLACK TERM THIS IS `shrank` — a false refusal on honest paydown, which is
    the failure mode that teaches people to route around a gate whose own refusal text forbids
    lowering the baseline. They would have no legitimate move left.
    """
    key, ran, static, want = _BIB
    got = classify(key, Reading(ran, static), _BASE)
    bad = 0
    if got.kind != want:
        out.append(f"selftest: the bibstruct deletion classified {got.kind!r}, not {want!r}")
        bad += 1
    if "slack" not in got.detail:
        out.append("selftest: the deletion detail does not report the slack it used")
        bad += 1
    return bad


def refusals_are_distinct(out: list[str]) -> int:
    """Check `shrank` and `unknown` stay different verdicts.

    ⚑ BOTH REFUSE, AND COLLAPSING THEM WOULD LOSE THE ONLY DISTINCTION THAT MATTERS TO A
    READER: `shrank` says the cases exist and the run stopped reaching them; `unknown` says
    nobody can tell. The second is a fact about the INSTRUMENT and the first about the tree.
    """
    shrank = classify("a.py", Reading(40, 48), _BASE)
    unknown = classify("a.py", Reading(40, None), _BASE)
    bad = 0
    if shrank.kind == unknown.kind:
        out.append(f"selftest: shrank and unknown collapsed to {shrank.kind!r}")
        bad += 1
    if not (shrank.refuses and unknown.refuses):
        out.append("selftest: a refusing kind did not report `refuses`")
        bad += 1
    return bad


def the_run_verdict(out: list[str]) -> int:
    """Check the run-level readers agree with the per-suite kinds.

    ⚑ THE CLASSIFIER PASSING IS NOT THE GATE PASSING, and `regressions` / `may_advance` are the
    seam between them. A census holding one refusal must both name that suite and forbid the
    census advancing — including the growth beside it, which is `set_ratchet`'s rule that
    paydown cannot record while a new key is present, in the mirror.
    """
    clean = {"a.py": classify("a.py", Reading(60, 58), _BASE)}
    mixed = {
        "a.py": classify("a.py", Reading(40, 48), _BASE),
        "c.py": classify("c.py", Reading(9, 9), _BASE),
    }
    bad = 0
    if regressions(clean):
        out.append("selftest: an unregressed census reported a regression")
        bad += 1
    if not may_advance(clean):
        out.append("selftest: an unregressed census was forbidden from advancing")
        bad += 1
    if [row.label for row in regressions(mixed)] != ["a.py"]:
        out.append(f"selftest: the refusing suite was not named: {regressions(mixed)!r}")
        bad += 1
    if may_advance(mixed):
        out.append("selftest: a census holding a regression was allowed to advance")
        bad += 1
    # ⚑ AND AN ABSENT SUITE'S ROW SURVIVES THE MERGE — the single most important property, and
    # the opposite of what a naive `{label: reading}` rebuild does.
    merged = advanced(_BASE, {"a.py": Reading(60, 58)})
    if merged.get("bib.py") != Reading(97, 96):
        out.append(f"selftest: an absent suite's row did not survive: {merged!r}")
        bad += 1
    if merged.get("a.py") != Reading(60, 58):
        out.append(f"selftest: the reporting suite's row did not advance: {merged!r}")
        bad += 1
    return bad


_ARMS = (semantics, loop_slack, refusals_are_distinct, the_run_verdict)

_CASE_COUNT = len(_CASES) + 2 + 2 + 6


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"reach-verdict selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"reach-verdict selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
