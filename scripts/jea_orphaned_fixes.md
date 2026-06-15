# JEA orphaned-fixes ledger — fixes/disciplines the silo sprawl forgot (re-propagate before claiming unified)

Archaeology (delegated, git history + script markers + charter): the jea work was ~25 silo scripts; bug
FIXES and the structural-modeling DISCIPLINE were written into individual scripts and never propagated to
the unified engine (jea_engine.py / jea_engine_pool.py / jea_engine_tiers.py). This is why audits kept
landing on STALE assumptions (e.g. "coop deadlocks" — long fixed). C5's regression runner MUST assert each
of these is present in the unified engine; until then "unified" overstates.

## ORPHANED FIXES the unified engine is missing (ranked; re-propagate)

1. **Escalation must DELIVER, not just flag** — jea_engine.py only sets esc=1/stores 0/1; arbitrary
   precision lives in jea_carrier_escalate.py (U3) + jea_limb_div.py (U5, afdcf1f). jea_engine_tiers.py
   reaches byte-limb but host-drained. ACTION: wire byte-limb as the production combine's top tier.
2. **Device interning / hash-cons** — jea_intern.py (U7, 7245d3c). The pool engine builds full trees with
   NO sharing -> the 3131x/27594x blow-up on any real rewrite. ACTION: intern-during-spawn in the pool.
3. **Overflow PREDICT-not-detect** — __clzll bit-width routing (jea_engine_tiers.py, 18b52e1). jea_engine.py
   combine_window still computes-wide-then-checks. ACTION: predict-place in the production combine.
4. **Three-state witness verdict (exact/ESCALATED/WRONG)** — bb0c170. jea_engine.py witnesses don't assert
   lazy avoided SILENT escalation; the U2 leniency (fold failure-mode into pass-set) can recur in C5.
5. **Residency invariant assertion** — jea_core.residency + the 1-block/SM floor (c55ac21). jea_engine.py
   coop hard-codes min(20,nsm); should ASSERT launched<=resident or document why revisit-gate makes it moot.
6. **SWAR magnitude-bucket packing + W=pow2 rule** — jea_bucket_msb/jea_carrier_bucketed (U1, 0190fa4) +
   the doubling-overshoot fix (0811851). The 17x/2.46x density win is absent from the unified carrier.

## Already propagated (good): revisit-readiness gate (#3 deadlock fix, IN), 128-bit overflow detect (IN),
## pool seeding fix (IN), the warmed-ablation harness jea_roofline (instrument exists).

## STRUCTURAL-MODELING discipline (forgotten; the pilot regressed to hand-fed ms)

PRINCIPLE: `rate = structural(kernel op-graph + eval strategy) x structural(host conductance) x ephemeral(O(1))`
(kernel_cost_model.py; charter ~709-726). The ephemeral residual self-enumerates (residual_decompose.py).
cost_cotype.py ("monomial-signature prove-or-reveal"): cost = typed product of named factors, each a
monomial in variables; then "X cancels in the ratio" is a THEOREM (net exponent 0), the residual lists its
own suspects, and a mis-specified dependency leaves a non-zero exponent that FLAGS its own broken
assumption. Models PROVE their structure; they don't measure-and-fit. (two_clock_domains: same-domain
ratios cancel the clock; cross-domain scale as clock_core/clock_mem.)

## RECIPE: make jea_consolidation_pilot.py structural (kill the hand-fed ms, AXES lines ~41-70)

Replace `lambda s,w: {...measured ms...}` with cost DERIVED from structure, same `total = launch + work`
shape as jea_nedge_model.total:
  T_coop  = t_L + W/P_coop                  (one persistent launch; P_coop = resident floor = nSM)
  T_strat = S*t_L + sum_strata work_s/P_full (one launch per topological stratum; P_full = full grid)
  T_pool  = t_L + W/P_full + spawn_overhead  (only one that does dynamic-spawn; others = INF there)
=> coop-beats-strat-on-deep-narrow FALLS OUT (deep-narrow: S large -> S*t_L dominates strat; coop pays t_L
once). The crossover is a Wheatstone bridge null in (S*t_L) vs (W*(1/P_coop - 1/P_full)) = the launch<->
occupancy Pareto. S, P_coop=nSM, P_full from topology_breakers.discover(); t_L is the ONE measured O(1) and
it CANCELS in the bridge. mode/repr/K/layout: express each as a cost_cotype factor signature so the bridge
null is a theorem of the signatures and a mis-specified factor self-reveals. carrier: predicted tier via
the migration law (bw(a)+bw(b)), reusing jea_engine_tiers predict-place. Net: zero hand-fed milliseconds;
the audit becomes self-falsifying, immune to the stale-input class (#1) that triggered this archaeology.

## C-ARC IMPACT (revised)

The consolidation is NOT done at "dedup the combine + schedulers." It must RE-PROPAGATE fixes 1-6 into the
unified engine, and make the cost/knob models structural (recipe above), THEN C5's runner asserts every
prior witness AND every orphaned fix passes via the one engine. New C-bricks: C3-rest (escalation-delivers
+ predict-place + bucket-pack into the production combine), C4 (intern + oracle + structural cost as
stages), C5 (runner = the gate). The structural-pilot refactor is a prerequisite for trusting any further
"missed consolidation" audit.
