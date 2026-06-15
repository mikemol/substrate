RUNG: R(observable, transitions)

# JEA-on-GPU unification arc — WAL cotype (the single source of truth)

Strictified ledger of the M2-runtime + unification arc. Every brick is an AI with an identifier, rendered
as a TRANSITION (state -> morphism -> state) with its preconditions exposed in the witness column [..] --
the witnesses ARE the DBE entailment (a brick is reachable only once its precondition bricks are done).
Anti-nominalization: no brick is named as a noun ("the packing"); each is a movement. Cotype-as-WAL:
update this file atomically with each brick, commit together. Companion detail: scripts/jea_m2_ledger.md.

## Apex costructure (the strictified shared structure — what every brick composes into)

Decompose-by-entailment costructure. The 7 done bricks + 10 open bricks are not a flat list; they compose
into TWO apex objects, both sitting over the founding primitive.

- **PRIM** `generator_step : state -> (emit, state')` — observe a bounded window of (own residue + shared
  store), step once, publish. Worker / controller / comms are this one primitive at different step_fn
  (charter, increments 1-6). Free-Forgetful term-algebra fold is its denotation.
- **APEX-1 = the UNIVERSAL ENGINE.** One kernel = spawn (dynamic work production) (+) parallel scheduler
  (+) term-rewriting, over the monotonic readiness store. Escalation = recursion = combine = one push.
  Realized partially: spawn loop (sequential, jea_ackermann), scheduler (847M nodes/s, jea_generator_strat)
  -- NOT yet fused into one kernel.
- **APEX-2 = the BUCKETED-LATTICE CARRIER.** ONE magnitude lattice (lane width = MSB+1 on the pow-2 ladder
  {1,2,4,8,16,32,64,...}). pack / escalate / reduce / trace-window are NOT four features -- they are the
  ORBIT of ONE symmetry, MIGRATION on the lattice: mul migrates up, add ~up-1, reduce migrates down,
  escalate = past the top bucket -> next carrier. Realized partially: the migration LAW is proven
  (jea_bucket_msb) -- the carrier is not yet packed by it.

ORBIT-SATURATION DISCIPLINE (shadow-arch rule 6): pack/escalate/reduce/trace are orbit-elements of the
migration symmetry, so the apex IS the migration operator (lattice + direction); do NOT extract a wrapper
"Migration" record above them (that is the false-positive rule-6 guards). Catalogue orbit position (S2G).

## AI ledger (all bricks, R(obs, trans) transitions; [..] = preconditions/witnesses = DBE entailment)

### DONE (frozen, write-once — this arc)

```
M2a  no-dataflow-core   --build-lockfree-queue(atomicAdd dequeue)-->  exactly-once node drain
                                                          [200k nodes exact vs host ref; each claimed once]
M2b  flat nodes         --add-readiness-gate(atomicCAS, children-done)-->  SPPF-DAG dataflow
                                                          [60k exact; deadlock-free by construction; M2a]
M2c  int64 wrap         --swap-carrier(Q=(num,den), __int128 detect)-->  exact Q + escalate
                                          [54k exact; 10 escalated == unrepresentable set; M2b]
M2d  fixed schedule     --wire-oracle(zero-copy GO/MODE into resident kernel)-->  live-scheduled
                                          [f*=4.20; resident kernel honors host push; M2c; closes AI-11b]
I1   eager-only prod    --add-MODE-slot(read live, eager/lazy)-->  eager/lazy in production + Agda path
                                          [Agda 7/40 both modes; M2d-oracle; jea_generator_dag]
I2   detect-by-int128   --bitwidth-predicate(__clzll, SWAR W>=2L dynamic)-->  predicted fast-path
                                          [bit-identical results; escalation unchanged; I1]
I3   flat-u64 (no map)  --bucket-by-MSB(pow-2 ladder) + migration-law-->  bucketing structure proven
                                          [law sound pred>=actual; 17x denser pack; reduce=down-migrate; I2]
U1   flat-u64 lanes     --pack-lanes-by-bucket(native dtype, working=2w) + migrate-->  data-driven mixed-width carrier
                                          [100k exact; 2.46x smaller; mig sound 0-undersized; 29 escalate>64->byte-limb; I3]
                                          (jea_carrier_bucketed.py; combine the CARRIER -- persistent-pool wiring = follow-on)
U2   MODE in dag_mode   --port-MODE(into strat: stratified high-throughput path)-->  MODE in strat
                                          [CORRECT both modes (exact OR correctly-flagged escalation, never silent-WRONG);
                                           EAGER exact ~0.9 Gnode/s@2^20; LAZY faster but RANGE-LIMITED (unreduced escalates
                                           at L>=256 where eager still exact); 1-pass/stratum, non-canonical; I1]
                                          (jea_generator_strat_mode.py; CORRECTED -- earlier "both exact 4.5x" masked lazy escalation)
U3   host-orch escalate --route-escalate-on-device(u64->u128->byte-limb)-->  carrier migration DELIVERS
                                          [100 combines all exact; tier-2 byte-limb to 1354b; 0 under-routed; M2c,U1,jea_limb_gpu]
                                          (jea_carrier_escalate.py; in-persistent-kernel spawn-on-flag = follow-on -> APEX-1)
U4   value-window only  --add-trace-window-lane(CF on GPU = the discarded gcd residue)-->  value<->trace DUAL realized
                                          [50k exact; canonical-on-GPU scale-free (no reduce); CF == value-window's
                                           DISCARDED gcd residue (free, same Euclid); round-trip=reduce; compare-by-prefix
                                           no cross-mult; reaches fast+canonical corner lazy can't; I1, jea_trace_window]
                                          (jea_carrier_trace.py; Gosper Mobius CF arithmetic = follow-on, trace-window's costly arm)
U5   byte-limb mul/add   --add-byte-limb-division(restoring-doubling)-->  Q reduce at ARBITRARY precision
                                          [divmod exact to 398b; gcd exact; reduce k*p/k*q exact to 381b >>2^128;
                                           CF (U4) past 128b; reuses the byte-limb adder; jea_limb_gpu]
                                          (jea_limb_div.py; sub-quadratic/parallel division Knuth-D/Newton = perf follow-on)
```

### APEX-2 (the bucketed-lattice carrier) -- COMPLETE

U1 (packed mixed-width) + U2 (MODE in stratified path) + U3 (unbounded escalation arithmetic) + U4
(trace-window dual = discarded gcd residue) + U5 (byte-limb division -> reduce) = the full Q carrier,
arithmetic AND canonical, at arbitrary precision. Migration lattice realized end to end (pack/escalate/
reduce/trace all migrations on it). No open bricks remain on APEX-2.

### DONE -> APEX-1 (the universal engine)

```
U6   spawn-seq || sched-sep --fuse(spawn(+)scheduler(+)rewrite, shared GROWING pool)-->  one universal kernel
                                          [128 roots E(n)->2^n exact; pool grew 128->400864 (3131x) AT RUNTIME;
                                           full-grid parallel, deadlock-free (monotonic readiness gate, no blocking);
                                           jea_ackermann_spec (spawn) + jea_generator_strat (scheduler)]
                                          (jea_universal_engine.py; Ackermann rule set = follow-on; the 3131x is the
                                           NO-SHARING cost -> U7 interning collapses it to linear)
U7   host intern only    --device-side-intern(parallel hash-cons, GPU sort+unique)-->  irregular-trace sharing
                                          [E(18): 524287 nodes -> 19 distinct (27594x collapse); semantics preserved;
                                           distinct == structural min n+1 (maximal sharing, no false merges); TREE->SPPF bridge; U6]
                                          (jea_intern.py; intern-DURING-spawn (U6+U7 fused, never build the blowup) = follow-on)
U8   self-contained Emit --emit-shared-SPPF-from-Agda(node-list, refl-vouched)-->  real Agda SPPF on GPU
                                          [EmitDAG.agda --safe vouchers; 6 DAG vs 31 tree (5.2x sharing); shared nodes
                                           computed ONCE; GPU == Agda value (7/6)^8 = 5764801/1679616 exact; canonical; U6,U7]
                                          (scratch/jea/EmitDAG.agda + jea_agda_dag.py)
```

### APEX-1 (the universal engine) -- COMPLETE

U6 (fuse spawn⊕scheduler⊕rewrite, one kernel, dynamic pool, deadlock-free) + U7 (device interning =
TREE->SPPF, 27594x collapse) + U8 (real shared SPPF from Agda, refl-vouched, evaluated exact, sharing
exploited) = the universal engine, end to end. No open bricks remain on APEX-1.

### OPEN -> debts (verification/model, NOT unification)

```
U9   nedge model: no refill  --add-mixed-depth-refill-dynamics-->  distribution-aware control [DONE]
                                          [makespan = max(deep-tail, shallow-throughput); validated EXACT (0%) vs
                                           ground-truth refill sim; model K* == sim K* (bisimulation); shallow-heavy
                                           K*=64 while max-depth-model picks 256 -> 1.15x over-window; jea_nedge_model]
                                          (jea_nedge_refill.py; debugging caught an LPT pop-order bug in the sim -- the
                                           failing witness exposed it, validate-outputs-not-inputs)
U10  Z-128 tiling unverified   --re-ablate(jea_roofline harness)-->  claim verified or retracted
                                          [jea_roofline --ablate]
```

**Count:** 16 DONE + 1 OPEN (0 unification + 1 debt: U10). **BOTH APEXES COMPLETE** -- APEX-2 (U1-U5, the full
Q carrier: arithmetic AND canonical at arbitrary precision) and APEX-1 (U6-U8, the universal engine: spawn
⊕ scheduler ⊕ rewrite + interning + real Agda SPPF). The "how many un-unified" answer, strictified: ZERO
unification bricks left -- both attractors realized. Only 2 DEBTS remain (U9 nedge-model refill, U10
re-ablate Z-128 tiling), neither a unification. Follow-ons logged (not blocking): U1 persistent-pool +
sub-byte SWAR; U2 jea_generator_bucket variant; U3 spawn-on-flag; U4 Gosper CF arithmetic; U5
sub-quadratic division; U6 Ackermann rule set; U7 intern-during-spawn; U8 deeper substrate terms.

## Retrospective ritual (gated — on the M2a -> bucketing arc)

- **G0 PRECOMMIT.** Prior expectation (from the compaction handoff): "Go for it on the M2 runtime — build
  the real on-device dataflow scheduler, replacing the AI-11b toy stub; this closes the primary goal."
- **G1 FREEZE (actual).** Built M2a-d (clean reference) -> reading the charter revealed the dataflow
  evaluator ALREADY existed (jea_generator_* ladder) and the primary Agda-on-GPU goal was ALREADY closed
  (jea_agda_bridge, 8046b4c) -> corrected the over-frame in ledger/script/charter/commit -> integrated the
  genuinely-new piece (eager/lazy MODE) into production + Agda (I1) -> user proposed predict-from-bitwidth
  (I2) -> user proposed magnitude-bucketing (I3) -> enumerated remainder + the two apexes.
- **G2 DELTA.** Expected "the runtime is missing, build it." Actual "the runtime existed; the new value was
  the eager/lazy Pareto knob." Divergence: I initially framed M2a-d as closing the primary goal.
- **G3 STRUCTURE-CAUSE.** Trigger: wrote "M2 CLOSED / spit-take end to end" in M2d's ledger+script. Root
  (systemic): I scoped the arc from the compaction SUMMARY's framing, not the authoritative charter/code;
  no step in the loop forced "read authoritative state before a closure claim." Contributing: the summary
  genuinely conflated the toy stub with the mature evaluator.
- **G4 DECORRELATE (subtract G3, find another).** Second, independent finding: the bucketing W2 metric
  initially used pred->actual bucket gap as "reduction migrates down" -- but that gap is dominated by
  POW-2 ROUNDING, not reduction, so the metric did not isolate the variable it named. Caught only because
  the witness FAILED (eager 2.45 vs lazy 2.11, both nonzero). Class: metric-does-not-isolate-its-variable
  (sibling of [[feedback_validate_outputs_not_inputs]]), distinct from the over-claim class.
- **G5 BLAMELESS.** Not "I was careless." Systemic: (a) no gate forcing authoritative-source read before
  closure claims; (b) no check that a witness metric isolates the variable it asserts (confounds:
  pow-2 rounding, turbo, P/E heterogeneity).
- **G6 SUSTAIN (== weight as improve).** What worked, protect it: (1) reading the charter BEFORE writing
  M2d's closure note caught the over-frame pre-commit; (2) bit-exact-vs-Python verification on every brick;
  (3) FORCING escalation to actually fire (the distinct-prime chain) rather than a vacuous witness
  ([[feedback_test_the_wall_before_declaring_it]]); (4) WAL-cotype kept the arc stable across many
  context-bottom turns ([[feedback_wal_cotype_context_stability]]); (5) the user's structural suggestions
  (I2, I3) folded cleanly BECAUSE the prior bricks were grown mature ([[feedback_grow_to_maturity_not_approximate]]
  paying off in real time).
- **G7 COMMIT.** (a) Over-frame -> already corrected across ledger/script/charter/commit (checkable: the
  honest-scope notes are in 3b... commits). Standing measure = G8-gate below. (b) W2 metric -> already
  fixed to direct eager-vs-lazy lane-bits (checkable: jea_bucket_msb re-run PASSES). Standing measure: a
  witness metric must isolate the variable it names; enumerate confounds before trusting it.
- **G8 FIXPOINT / HANDOFF.** Cross-pass blind spot for an external reviewer: EVERY verification used MY
  reference (Python Fraction / host fold) over MY synthetic DAGs (random balanced trees + a crafted prime
  chain). Shared assumption no pass could question: that synthetic trees exercise the same regimes as a
  REAL substrate-emitted SPPF (sharing, irregular depth, adversarial heterogeneity). HANDOFF: validate
  MODE/bucketing/escalate on a real substrate SPPF with sharing (= brick U8). Labeled exhausted-from-
  inside, NOT verified.
- **G9 ESCALATE / ACCUMULATE.** Both class-level findings are JUDGMENT disciplines, not automatable
  predicates, so they legitimately terminate at the discipline/memory layer (escalating a non-mechanizable
  check to a hook would be theater). Both are ALREADY in the standing ledger: over-claim ->
  [[feedback_test_the_wall_before_declaring_it]] + [[feedback_hunt_opacity_after_green]]; metric-isolation
  -> [[feedback_validate_outputs_not_inputs]]. Read-the-ledger-first confirms no NEW memory warranted (the
  metric-isolation angle is a refinement of validate-outputs, not a new class). Declared: no new gate.

## Status / abort-residue

15 DONE (frozen). 2 OPEN. **BOTH APEXES COMPLETE.** APEX-2 (U1-U5): the full Q carrier, arithmetic AND
canonical, at arbitrary precision -- the migration lattice end to end. APEX-1 (U6-U8): the universal
engine -- spawn⊕scheduler⊕rewrite fused, device interning (TREE->SPPF), real Agda shared SPPF evaluated
exact. THE UNIFICATION WORK OF THIS ARC IS DONE: every U-brick landed, both attractors realized, zero
unification bricks remain. Only 2 DEBTS left (neither a unification): U9 (nedge-model mixed-depth refill
dynamics) + U10 (re-ablate the Z-128 tiling claim). If context flushes: this file + the two apex names
reconstruct the whole arc. U9 DONE (jea_nedge_refill.py: distribution-aware control, validated exact vs the
refill sim; max-depth model over-windows shallow-heavy by 1.15x). Only U10 left (re-ablate the Z-128 tiling
claim, jea_roofline --ablate) -- a pure verification debt, not modeling or unification. The arc's structural
goal is reached; U10 is optional cleanup.
