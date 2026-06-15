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
                                          [both exact; lazy 349 vs eager 77 M/s (4.5x); lazy 1-pass/stratum non-canon; I1]
                                          (jea_generator_strat_mode.py; jea_generator_bucket variant = follow-on)
U3   host-orch escalate --route-escalate-on-device(u64->u128->byte-limb)-->  carrier migration DELIVERS
                                          [100 combines all exact; tier-2 byte-limb to 1354b; 0 under-routed; M2c,U1,jea_limb_gpu]
                                          (jea_carrier_escalate.py; in-persistent-kernel spawn-on-flag = follow-on -> APEX-1)
```

### OPEN -> APEX-2 (the bucketed-lattice carrier)

```
U4   value-window only   --add-trace-window-lane(CF-shape, compare-by-prefix)-->  value<->trace dual realized
                                          [I1 (lazy = the value side); jea_trace_window]
U5   byte-limb mul/add    --add-byte-limb-division-->  Q reduce at arbitrary precision
                                          [jea_limb_gpu (mul/add/carry done; division OPEN)]
```

### OPEN -> APEX-1 (the universal engine)

```
U6   spawn-seq || sched-sep  --fuse(spawn (+) scheduler (+) rewrite)-->  one universal kernel
                                          [jea_ackermann_spec (spawn loop); jea_generator_strat (scheduler)]
U7   host intern only     --device-side-intern(parallel dedup)-->  irregular-trace sharing
                                          [U6; SPPF/Register intern (host side exists)]
U8   self-contained Emit  --wire-real-substrate-SPPF(+ sharing)-->  real Agda terms on GPU
                                          [jea_agda_bridge (closed); U7 (intern/sharing)]
```

### OPEN -> debts (verification/model, NOT unification)

```
U9   nedge model: no refill   --add-mixed-depth-refill-dynamics-->  complete control model
                                          [jea_nedge_model]
U10  Z-128 tiling unverified   --re-ablate(jea_roofline harness)-->  claim verified or retracted
                                          [jea_roofline --ablate]
```

**Count:** 10 DONE + 7 OPEN (5 unification toward 2 apexes + 2 debts). The "how many un-unified" answer,
strictified: 5 unification bricks, converging on APEX-1 (U6,U7,U8) and APEX-2 (U4,U5 — U1,U2,U3 DONE; the
carrier-side of APEX-2 is now complete: packed + mode + unbounded escalation); 2 debts. Denominator is
OPEN (orbit not saturated — new instances surface as bricks land). Follow-ons logged (not blocking): U1
persistent-pool wiring + sub-byte SWAR floor; U2 jea_generator_bucket variant; U3 in-persistent-kernel
spawn-on-flag (which is itself a step toward APEX-1's dynamic work production).

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

10 DONE (frozen). 7 OPEN, each a named transition with its preconditions = pick up any whose precondition
bricks are DONE (U4,U5,U6,U9,U10 unblocked now; U7 needs U6; U8 needs U7). If context flushes: this file
+ the two apex names reconstruct the whole arc. APEX-2 carrier-side COMPLETE: U1 (packed mixed-width,
2.46x smaller), U2 (MODE in stratified path, 4.5x), U3 (unbounded escalation u64->u128->byte-limb, 1354b
delivered) all DONE. Next natural brick = U4 (the trace-window CF-shape lane = the genuine value<->trace
DUAL, the one APEX-2 piece that is real new structure not a carrier-width extension) or U6 (fuse spawn ⊕
scheduler = the APEX-1 keystone). Follow-ons logged, not blocking.
