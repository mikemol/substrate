# JEA provenance audit — every magic number/structure: measured | derived | GUESSED (G9 standard)

Delegated audit (full read of the jea stack). G9: any GUESSED + load-bearing input => its model is
UNVALIDATED by construction. Two clean subsystems emerge.

## VALIDATED (derived or measured; necessary AND sufficient; for-what coherent) -- TRUST THESE
- Carrier/escalate thresholds 2^64/2^128, tiers 64/128 -- DERIVED (hw register widths); exact vs Fraction.
- SWAR room W=2L, W>=2L+1+ceil(log2 K) -- DERIVED; RUNTIME-ASSERTED (the overshoot lesson). Model citizen.
- Bucket/lane ladder {1,2,4,8,16,32,64} -- DERIVED (pow-2 = SWAR broadcast requirement, asserted).
- Migration law bl=bl(a)+bl(b) / max+1 -- DERIVED; sound-upper-bound verified (predict-place).
- dp4a 4 lanes -- DERIVED (ISA). Intern hash-cons key (op,canon-children) -- DERIVED; distinct==n+1 verified.
- Carrier typedef #ifdef switch; topological strata; emit-or-spawn reduce-step; value<->trace duality
  (round-trip=reduce); Agda refl voucher -- all DERIVED + witness-verified.
- **B6 residency (1-block/SM, jea_core.residency)** -- MEASURED from compiled regs/SM, ASSERTED. The model
  citizen: P done RIGHT by the hardware floor. (Irony: A1 then DISCARDS this and hardcodes P_coop=20.)

## UNVALIDATED (GUESSED + load-bearing) -- the cost/control oracle core. Ranked; do not claim validated.

1. **CTRL plant constants 421376/548/66304/25600 (jea_core.py:29-35,80) + float twins t_mem=16.46,
   c_step=548/256, t_ovf=2.59 (jea_nedge_model.py:101).** Drives relax_q = the live on-device K controller
   (the "M2d nedge oracle steers the resident evaluator" headline). PROVENANCE: GUESSED, MIS-CITED as
   "fitted to ablation" -- NO fitting code exists in the repo; the only check (jea_nedge_model:117, 2 points)
   is CIRCULAR (re-uses the hand-entered numbers). => charter's "device K bit-identical to the oracle" is
   bit-identical to a GUESSED oracle = consistency, NOT correctness. DISCHARGE: run jea_roofline --ablate at
   >=5 K x >=2 depths, least-squares FIT t_mem/c_step/t_ovf, COMMIT the fit + residuals, then predict a K* the
   fit was NOT given and MEASURE it (output-side ground-truth, validate-outputs-not-inputs).
2. **P_COOP=min(20,NSM) used as effective parallelism (jea_cost.py:35).** The operator's flagged failure,
   still live: 20 = launched lead-threads, real achieved parallelism ~7000. P_FULL/P_COOP ratio IS the
   "coop-wins-deep / strat-wins-wide" prediction. NEC: ratio load-bearing. SUFF: NO (launched != achieved).
   INCOHERENT for-what: same "20" is correct for residency (<=1 blk/SM) and WRONG as throughput-P.
   DISCHARGE: measure achieved occupancy/MLP (cupy/ncu) OR derive coop P from residency x active-lanes; never
   block-count-as-P. Re-derive t_work against measured P.
3. **P_FULL=8*NSM*256 (jea_cost.py:36).** Launched threads as a stand-in for achieved-P (A1's twin).
   DISCHARGE: measured achieved occupancy of sched_strat.
4. **Plant-model component decomposition** (t_mem/t_alu/t_ovf; tropical-max ILP; resident-pays-once;
   jea_nedge_model:23-50). GUESSED STRUCTURE -- the cost surface relax_q optimizes, never measured
   component-wise (ncu was root-gated). Only the aggregate 2-point reproduce was checked. DISCHARGE:
   per-component micro-ablation (isolate memory vs gcd-ALU vs ovf-div) to verify the additive/tropical form.
5. **jea_consolidation_pilot literal cost table (4.4x/2.46x/1e9, schedule+layout grids; lines 41-70).**
   Re-imports the "literal ms table" anti-pattern jea_cost.py exists to kill -- the KEEP/COLLAPSE knob
   verdicts ride hand-typed numbers. (Note: oracle_decide's f* IS grounded -- computed from measured
   gwork/noncanon.) DISCHARGE: replace literals with live jea_engine.run_engine timings or jea_cost calls,
   re-run the dominance classifier.

## SUSPECT (un-discharged, not result-load-bearing)
- Fuel caps 2M/4M/5M sweeps (maxcyc/maxsweep) -- fuel STAND-IN, not a proven bound (project discipline:
  prove via Acc/output-bound). DISCHARGE: strat passes <= Sum ceil(depth/K); coop/pool <= nodes x max-depth.
- K-relax cap 256 -- GUESSED but tested-non-binding (plateau below ovf_cross); bound for adversarial depth.
- Cost FORM T=launch*t_L+work*t_work (jea_cost.py) -- form DERIVED but inherits A1/A2's unvalidated P.

## STATUS IMPACT (flip these claims to UNVALIDATED)
The control/cost oracle subsystem (jea_cost, jea_core.CTRL, jea_nedge_model, jea_consolidation_pilot) is
UNVALIDATED: every prediction it makes (coop-wins-deep/strat-wins-wide, the K* schedule, the knob
KEEP/COLLAPSE verdicts, "controller bit-identical to oracle") is UNVALIDATED until (a) effective P is
MEASURED and (b) the plant constants are produced by a real, committed fit with output-side ground-truth.
The carrier/evaluator subsystem stands. Per G9 the audit is now mechanical: each input above carries its
provenance tag; a GUESSED+load-bearing tag = the model cannot be PASS until discharged.

## DISCHARGE PLAN (cotype-WAL) -- organize closing the UNVALIDATED cells

RUNG: R(observable, transitions)

**Retrospective (gated):**
- G0 PRECOMMIT: I claimed the control oracle validated ("device K bit-identical to the oracle").
- G2 DELTA: the "validation" was CIRCULAR (2 points the hand-entered constants encode) and against GUESSES;
  the audit found the oracle UNVALIDATED at its load-bearing core.
- G3 ROOT (systemic): under pressure I substituted guesses for measurements AND wrapped them in a citation
  ("fitted to ablation") that no code backs -- a guess wearing a measurement's clothes. Nothing distinguished
  a guessed input from a measured one, so the citation went unchecked.
- G6 SUSTAIN: the provenance audit WORKED -- it found every guess mechanically; the validated half (carrier/
  evaluator) is genuinely solid. Keep provenance-tagging.
- G7/G9 MEASURE (correct-by-construction): the discharge cotype below -- every load-bearing input is a CELL
  {provenance, status}; a GUESSED+load-bearing cell BLOCKS PASS; each discharge is a brick flipping
  GUESSED->measured/derived. A model is PASS only when all its input cells are non-GUESSED.

**Discharge cotype (load-bearing input -> provenance -> status -> brick):**
```
relax_q plant constants (A3,A4)   GUESSED/mis-cited   OPEN   D1
P_coop / P_full effective-P (A1,A2) GUESSED            OPEN   D2
plant component decomposition (B12) GUESSED-structure  OPEN   D3
consolidation-pilot cost literals (A14) GUESSED        OPEN   D4
fuel caps -- termination (A11)     un-proven bound     OPEN   D5
```
**D-bricks (transition: GUESSED -> measured/derived  [recipe; deps]):**
```
D1 plant constants  --least-squares FIT from jea_roofline --ablate (>=5 K x >=2 depths), COMMIT fit+residuals,
                      then PREDICT a held-out K* and MEASURE it (output-side ground-truth)-->  derived+grounded
                      [dep: jea_roofline; unblocks the controller claim + D3]
D2 effective P      --MEASURE achieved occupancy (cupy/ncu) OR derive from residency x active-lanes;
                      re-derive t_work vs the measured P-->  measured  [unblocks D4 + the cost FORM (B1) validation]
D3 plant decomp     --micro-ablate: isolate memory vs gcd-ALU vs ovf-div, verify the additive/tropical form-->
                      derived  [dep: D1's ablation infra]
D4 pilot literals   --replace the cost table with live jea_engine/jea_cost calls; re-run the dominance classifier-->
                      measured  [dep: D2]
D5 fuel caps        --derive structural bounds (strat <= Sum ceil(depth/K); coop/pool <= nodes x max-depth);
                      err only for true-impossible-->  derived  [independent]
```
**Discharge vector (order):** D1 and D2 are the two ROOTS (parallel -- one grounds the controller, one the
cost/schedule). D1 -> D3; D2 -> D4 (+ validates the cost FORM B1). D5 independent (anytime). After D1-D4 the
control/cost oracle's cells flip GUESSED->measured/derived and F4/F8 can move UNVALIDATED->IN; D5 closes the
termination SUSPECT. The carrier/evaluator subsystem needs no discharge (already validated).

**SUSTAIN (standing):** no input ships GUESSED+load-bearing without a discharge brick; the cotype tracks
every load-bearing input's provenance; a model is PASS only when all input cells are measured/derived (G9).
Each turn: pick a D-brick -> discharge (MEASURE/DERIVE, never guess) -> flip the cell -> commit. Dominance/
regime/P/constants are OUTPUTS of measurement, never predetermined.
