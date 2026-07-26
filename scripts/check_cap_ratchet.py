#!/usr/bin/env python3
"""check_cap_ratchet.py — per-module elaboration PEAK is DEBT; ratchet it toward the 128MiB cap.

The 4th sibling of the set-ratchet family (carrier-locality / sumtype / Set₁). Those govern
structural debt; this one governs MEMORY debt — the per-module Agda elaboration peak that the
`+RTS -M<MEM_CAP>` forcing function bounds.

WHY A RATCHET (not a scalar). `MEM_CAP = "256m"` is a HARDCODED SCALAR in
scripts/gen_build_makefiles.py — the anti-pattern this repo has already killed three times: a
decision's cost is never a frozen number (feedback_cost_is_structural_times_live), and a gate over
accumulating debt is a paydown-only ratchet over a MATERIALIZED census
(feedback_policy_is_a_ratchet_over_census). Because the offender list lived only in prose it went
STALE — a session carried "MixColumns/Proof ~203, SBoxTable/Properties ~138" while the truth was
FIVE modules at 427/213/151/143/129, the largest of which was never on the list. This gate makes
"which modules block 128" a GATE OUTPUT instead of something to remember.

CENSUS (materialized from the ledgers, not a frozen list): the SET of module relpaths whose
recorded peak exceeds TARGET (128 MiB). The census is DEBT — it may only be PAID DOWN (shard the
module, split def/proof, seal a heavy neutral), never grown: a NEW module crossing 128 is REFUSED.
A paydown auto-lowers the baseline. When the census empties, MEM_CAP can descend to 128
mechanically (⟡cap128-flip) rather than by a flag day.

⚑ THE STATISTIC IS THE LATEST ROW — measured, not assumed; the other two candidates are WRONG:
  · MEDIAN is fooled by the ledger's BIMODALITY (a sub-second/~90MB row is a cheap `.agdai`
    re-check; a 5-18s/130-430MB row is a real elaboration). Graded's last-5 are
    93, 298, 90, 89, 427 — median 93 would silently miss a 427MB offender.
  · MAX-over-last-K NEVER FORGETS. Flat.mk uses real-file `.agdai` targets, so an UNCHANGED module
    is never re-invoked and appends no row; its old high rows sit in the window indefinitely.
    Measured: KAT/Full's window is [214, 206, 190, 193, 75] — max would report 214 forever even
    though the sharded Full now costs 75. Taking max made the census 28 modules, 23 of them
    ALREADY PAID (SBoxTable [160,…,78], JacobianCounterexample [.,317,.,109], Round6/7/9 [131,…,78]).
    A gate that reports paid debt as owed reproduces the very stale-list failure it exists to kill.
  · LATEST row = the last real compile of the CURRENT source, which under the post-b57985f build is
    exactly the freshness the post-full-build gate placement guarantees. It yields the true current
    blocker set (5), and a paydown shows up immediately as an auto-lower.
RESIDUAL RISK (accepted, documented): a cheap re-check row landing last can under-report a heavy
module for one cycle — the ratchet then auto-lowers and refuses re-entry on its next real
elaboration. That is visible churn, not a silent pass, and it is the recoverable direction.

The existing offenders are GRANDFATHERED at the baseline (legacy debt frozen, like Set₁ and the
carrier-locality ALLOW set); the ratchet does not adjudicate which are worth fixing, it only
forbids GROWTH and rewards paydown.

Blocking gate. Exit 0 = clean, 1 = a new module crossed the cap (or the census is unmeasurable).
Usage: check_cap_ratchet.py [--quiet] [--target N]
"""
import os
import sys

import buildtime
import ratchet

TARGET = 128                                      # MiB — the cap we are ratcheting toward
BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "cap_ratchet_baseline.txt")


def census(target=TARGET):
    """The over-cap set: {module_rel} whose LATEST recorded peak > target.

    Keys are full relpaths (buildtime.read_mem joins reldir + basename), so the dozens of
    `Properties.agda` do not collide. Stale rows persist for DELETED modules (a removed probe
    leaves its ledger rows behind), so filter to modules that still exist on disk.
    """
    out = set()
    for mod, peaks in buildtime.read_mem().items():
        if not peaks:
            continue
        if peaks[-1] > target and os.path.exists(os.path.join(buildtime.AGDA, mod)):
            out.add(mod)
    return out


def main():
    quiet = "--quiet" in sys.argv
    target = TARGET
    if "--target" in sys.argv:                    # test hook for the refusal path
        target = int(sys.argv[sys.argv.index("--target") + 1])

    # COMPLETENESS GUARD (mirrors set1_ratchet_cores': an incomplete census is not a low count).
    # A fresh clone has no ledgers; recording {} as the baseline would then REFUSE every real
    # offender on the first build. Cannot measure is not no-debt.
    if not buildtime.read_mem():
        print("cap-ratchet: NO peak-mem ledger rows — census unmeasurable; not certifying.")
        print("  Run a build first (`make -C agda -j`); membudget records peaks per module.")
        return 1

    return ratchet.set_ratchet(
        census(target), BASELINE, "cap-ratchet", quiet,
        noun=f"module(s) over {target}MB",
        refuse_hint="A module crossed the cap. SHARD it (split the elaboration unit at an "
                    "associative boundary and seal the parts — cf. KAT.Full's fold-++ shards), "
                    "split def/proof, or seal the heavy neutral `opaque`. Do NOT raise the cap.")


if __name__ == "__main__":
    sys.exit(main())
