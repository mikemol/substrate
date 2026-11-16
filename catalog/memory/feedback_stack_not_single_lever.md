---
name: feedback_stack_not_single_lever
description: "no SINGLE technique moves a peak/cost — a STACK applied to a fixed point does; judge at the CENSUS after a COMPLETE run, never at a mid-edit ledger tail"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
  modified: 2026-07-27T00:17:04.755Z
---

USER (2026-07-26), verbatim: *"no **single** technique addressed peak consumption. Multiple techniques, in
concert, applied to a fixed point, did."*

**Why:** I measured one lever (⟡graded-laws-noreexport — the Laws chain off `open Prev.Over … public`) and
wrote it up as *"REFUTED — peaks unchanged."* Wrong twice over: (1) I read `.agda-times.tsv` TAILS from a
build that had ABORTED at `[NotInScope]`, so the numbers were pre-rewire for every module the aborted build
never reached; (2) I judged the lever SOLO. The complete build showed the census going 5 NEW → 1, and with one
more technique → 0. The AES precedent is the same shape: ~5 techniques (thin-poly-type · gunit-slice ·
defproof-split · schedule-seal · il-shard) stacked to reach 66-68 MiB; no one of them did it.

**How to apply:**
- A lever's verdict comes from the GATE/CENSUS after a **complete** run, never from a ledger tail mid-edit.
  Here that is `check_cap_ratchet.py` (census = `peaks[-1] > cap`, the LATEST peak — a stale high ages out the
  moment a module re-typechecks, and a partial build leaves stale tails that read exactly like "no change").
- Expect a lever to be net-neutral ALONE and decisive IN A STACK. Do not retire it on a solo measurement.
- Beware plan-file headings like "LEVERS TRIED AND REFUTED BY MEASUREMENT" — they invite solo-lever verdicts.
  Record a lever as *measured-in-this-stack-at-this-point*, not as universally refuted.
- The sibling failure is enumerate-by-recall: building a completeness-critical list (e.g. a re-export `ALL`
  list) by hand instead of from the directory. Use the same source the build generator uses.

Relates to [[feedback_measure_instrument_before_theorize]], [[feedback_plan_notes_are_hypotheses]],
[[feedback_cost_is_structural_times_live]], [[declaring-wall-rebuild-reflex]].
