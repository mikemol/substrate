---
name: feedback_silo_sprawl_orphans_fixes
description: "building as many silo scripts orphans hard-won fixes + disciplines; auditing/modeling from MEMORY then yields stale conclusions — on unification, re-propagate every fix and derive models from structure, don't hand-feed"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

When work accumulates as many separate silo artifacts (the jea arc: ~25 scripts, each a per-brick witness),
bug FIXES and hard-won DISCIPLINES get written into individual files and NEVER PROPAGATE to the others or
to my working model. Then, reasoning/auditing/modeling FROM MEMORY (the charter narrative, "what I recall")
instead of from the current code yields STALE conclusions — I re-assert properties of bugs we already fixed.

Recurred sharply (2026-06-15): in the consolidation audit I declared the "coop scheduler dominated" because
"it deadlocks past ~3/SM" — but that deadlock had been FIXED long ago (the revisit-readiness gate). MEASUREMENT
showed coop is 4.4x FASTER than strat on deep-narrow DAGs (one persistent launch vs launch-per-stratum) = a
genuine knob, not a false one. The user caught it; delegated archaeology then found ~6 orphaned fixes the
unified engine is missing (escalation-delivers, device-interning, predict-not-detect, three-state witness,
residency-assert, SWAR bucket-pack) + the forgotten structural-modeling discipline. Ledger: scripts/
jea_orphaned_fixes.md.

This is the silo-sprawl twin of [[feedback_grow_to_maturity_not_approximate]] (mature pieces fold into a
tight kernel) and a concrete cause of the [[feedback_validate_outputs_not_inputs]] failure (I grounded a
verdict on a stale INPUT — a fixed bug — instead of MEASURING the output). Fourth pre-judgment one arc caught
this way (either/or→common-structure; detect→predict; bucket-dominates→knob; coop-dominated→measured-knob).

**How to apply:**
1. **Ground audits/claims on MEASUREMENT or the CURRENT CODE, never remembered history.** Before asserting a
   property ("X is slow/broken/dominated"), check it still holds in the code as-is, or measure it.
2. **On unification/consolidation, RE-PROPAGATE every orphaned fix** — dedup is not enough; the unified
   artifact must inherit ALL fixes, asserted by a regression runner (claim-requires-artifact), or "unified"
   overstates. Do fix-archaeology (git history + script markers) FIRST.
3. **Derive models from STRUCTURE, don't hand-feed measurements.** A pilot/cost-model that depends on typed-in
   numbers (e.g. measured ms) is not structural and will go stale. Use rate = structural(op-graph/launches/
   occupancy) x ephemeral(O(1) that cancels in ratios); cost_cotype's monomial prove-or-reveal makes
   "X cancels" a theorem and self-reveals broken assumptions. (kernel_cost_model.py / cost_cotype.py.)
4. Run the standing principles (common-structure, predict-don't-detect, validate-outputs) as a PRE-COMMIT
   pass on my own work, not post-hoc after the user points at the lapse.

**Regrounding maps re-surface DONE arcs (2026-06-20, △).** A regrounding/retrospective forward-map,
reconstructed from open-threads prose, listed △ (⊢-arc truth-correction) as "open, highest" — but it
was DONE+committed (`1eac16c` + ŝ `ba2728d`), correctly recorded in [[project_overclaim_witness_arc]],
4 modules green on the tree. The stale source was an open_threads entry still framed as "7 streams to
dispatch". **Before tackling a dispatched symbol, GROUND IT ON THE TREE** (git log for the commit +
grep the lemma) — a reconstructed map is point-in-time prose, not live state; a "tackle X" may already
be X. Verifying first cost one probe; building first would have re-proved a theorem. Same root as
above: status lives in the code, not the map.

**MECHANIZED (2026-06-20): `scripts/worklist.py`.** The remedy is now a command, not discipline:
status is DERIVED from the tree (commit/lemma/module/linter predicates), never hand-edited, so it
can't go stale. `worklist.py --open` = what's actually open; `--update` regenerates the status block in
project_open_threads.md (idempotent). The regrounding ritual should RUN it for live status, not
reconstruct from the hand-authored prose (the prose is the items' DESCRIPTION; the tree is their
STATUS). Sibling of decomposition/'s build_*_db + interpret_*_retrospective (records regenerated from
durable artifacts). This is judgement-is-demechanization applied to the worklist itself.
