RUNG: R(observable, transitions)

# JEA-on-GPU unification arc — WAL cotype (the single source of truth)

## == Δ-ARC RETROSPECTIVE LEDGER (labeled; every gate output is a trackable cell) ==

**AIs (G-roster):**
- **AI-Δ0** orchestrator — D1/D2 discharge (jea_live_cost.py), gates, ledgers (main loop).
- **AI-Δ1** interface cartographer — mapped el-atlas live-machinery signatures (Explore; not resumable).
- **AI-Δ2** provenance archaeologist — WAL/git audit of live_dispatcher.decide() constants (general-purpose; resume id ad547863434f51211).

**Findings (G3/G4 — write-once):**
- **Δ-F1** binding_edge used an INCOMPARABLE (superset) perturbation (iMC relax ⊇ PCIe relax → PCIe could never win). CLOSED (719524f: disjoint single-edge relaxations).
- **Δ-F2** W3 was a circular witness (identity tau:=measured−L·t_launch printed as a "prediction" at gnorm=1). CLOSED (719524f: labeled identity + throttle PROJECTION).
- **Δ-F3** live_dispatcher.decide() fstar/bottleneck BYPASS the Kron solve (hand-coded roofline ratio + `g<1`/`link<0.5` ternary); "ONE Kron op" true only for compute_bw. VERDICT recorded (719524f distrust list). FIX = Δ-A1.
- **Δ-F4** decide() dead/inert constants: I=0.1 CANCELS, 150e9 & 10906e9 never bind → fstar reduces to bandwidth ratio PCIe·link/(iMC·g+PCIe·link); only 6e9(measured)+iMC(measured)+trip(GUESSED 100.0) move it; 0.5 threshold GUESSED. VERDICT recorded. FIX = Δ-A1.

**Verdict changes / commits (G7 — done):**
- **Δ-C1** D1/D2 DISCHARGED → jea_live_cost.py + F4/F8/oracle ledger flips (commit 719524f).
- **Δ-C2** live_dispatcher SOUND → poll-sound / decide()-unsound, added to distrust list (719524f).
- **Δ-C3** retrospective + AI roster + this labeled ledger (commit 2aa8764 / current).

**Open action items (G7/G9 — DISCHARGE BRICKS, one-per-turn):**
- **Δ-A1** [CLOSED] wired decide() to the solve: fstar←discovered-conductance load-balance ratio g_gpu/(g_cpu+g_gpu); bottleneck←edge-sensitivity (3-way shift PCIe/link→iMC/iGPU→thermal); trip←discover_thermal(); I/150e9/10906e9/6e9/0.5/100.0 REMOVED. Ground-truth test BUILT (decide_groundtruth.py): W1 formula validated (f* from measured conductances == empirical makespan argmin), W2 GPU branch PCIe-bound. Found+fixed 2 bugs en route (PCIe GB/s-vs-bytes/s unit mismatch → fstar=0; alloc-bound CPU measurement). Spawned Δ-A3.
- **Δ-A3** [CLOSED via P] decide() now takes pcie_eff/cpu_eff (jea_edge_states.measure_edges, D3 micro-ablation):
  each conductance = structural bound × live_state × MEASURED efficiency, consistent base. decide(both effs @
  trained link) reproduces the achieved load-balance 0.30-0.32 == decide_groundtruth's empirical f_emp. The edge
  primitive (scripts/jea_edge_states.py) is the shared P, ready for D4. Measured here: PCIe eff ~20%, DRAM ~15%.
- **D3** [CLOSED] = the efficiency micro-ablation in jea_edge_states.measure_edges (saturating best-of-N per edge).
- **D4** [CLOSED, n-path] FIRST cut routed the schedule axis through live re-measurement -- and the live re-read
  CAUGHT that the frozen "strat wins wide 2.7 vs 3.1" (13%) was WITHIN the noise floor, and the coop/strat verdict
  flickered run-to-run. User: a noise-floor tie in a CHOICE = stop denoising the 1-path; decompose the options as
  an n-path. So coop/strat/pool are NOT 3 strategies to adjudicate -- they are CORNERS of a (launch-granularity
  g∈[1,S], dynamism d) SURFACE over ONE persistent-kernel engine (jea_engine already): coop=(g=1,static),
  strat=(g=S,static), pool=(g=1,spawn). jea_schedule_surface.py measures the g-axis SLOPE per workload: deep S=199
  slope ~4 (STEEP, g*=1 a real ~4x min), wide S=9 slope ~0.15 (≈25x flatter -- the tie is a FLAT region of the
  surface, structural: launch span (S-1)·c_launch negligible for small S). The solve reads g* off the surface; no
  discrete dominance verdict. jea_consolidation_pilot rewritten: audits the DISCRETE axes (mode/repr/K/layout, all
  genuine knobs) and DEFERS schedule to the surface. [[feedback_noise_floor_is_flat_region]]
- **Δ-F8** [finding] coop/strat/pool are not distinct kinds -- they are corners of the (g,d) schedule surface; the
  launch-granularity g-axis steepness SCALES with S (slope ∝ (S-1)·c_launch/W), so small-S workloads sit on a flat
  region (no choice) and large-S have a real g*=1 minimum. A noise-floor tie was the signal the 1-path was wrong.
- **Δ-F5** [finding] correcting ONE edge's efficiency while leaving another structural gives a WRONG f* — the
  overestimates must move together (ratio-cancellation, the Δ-A1 lesson generalized). Correct all edges or none.
- **Δ-F6** [finding] a LIVE-measured efficiency already SUBSUMES the live_state it was measured at (a saturating
  H2D trains the link to gen4, so pcie_eff bakes in link training). So (bound × eff × live_state) is NOT three
  independent factors — eff × idle-link_state double-counts. (Refines the structural-not-scalar (bound,state)
  pair: state and measured-eff overlap.) **This is a SYMPTOM of Δ-F7** — my "fix" (pin link_state=1.0 for the
  validation) treated the symptom by FORCING a world-state (the rigidification reflex), not the cause.
- **Δ-F7** [finding, the cause] a live reading is DEPENDENTLY TYPED on its read-time state; caching it and
  combining with a separately-read state is a TOCTOU race (poll link@t1, measure eff@t2, decide@t3 — link
  trains/detrains across, so we compose DIFFERENT world-states). efficiency : (link_state,T,gov)→ratio, not a
  scalar; using eff@gen4 where eff@gen1 is required is a type error surfacing as a wrong number. [[feedback_reread_meters_toctou]]
- **Δ-A4** [CLOSED host-side; AI-11b actuator remains] resolved by the CONTROLLER/ACTUATOR split (jea_telemetry.py),
  not my factor-out patch: the on-GPU evaluator CANNOT call off-GPU, so the HOST listens for events (timer/thermal/
  ASPM/GPU poll-trigger), re-reads ALL meters in ONE epoch, composes the decision (achieved = bound × live_state@now
  × intrinsic_eff), and ATOMICALLY SWAPS the telemetry PACKAGE resident in GPU memory (double-buffer: write inactive,
  flip pointer). GPU is a pure consumer of the active package. Closes Δ-F7 BY CONSTRUCTION (consumer only ever reads
  a whole single-epoch package -- can't compose t1/t2/t3) and Δ-F6 (eff & state combined once, in-epoch). The fork I
  posed (GPU re-measure vs cache scalar) was wrong -- the answer is host-reads-on-events + atomic package replace.
  Remaining: the device-resident buffer + actuator acting on pkg.fstar/bottleneck = AI-11b (standing on-device debt).
- **Δ-A2** [CLOSED; = the G9 escalation] witness-sanity CONTRACT built (scripts/witness_sanity.py): callable
  helpers same_scale (catches the Δ-A1 GB/s-vs-bytes/s unit bug), single_edge_gains (makes the Δ-F1 superset
  relaxation UNREPRESENTABLE -- disjoint by construction), not_calibration_identity (catches the Δ-F2 circular
  W3). __main__ is a REGRESSION proving it fires on all 3 historical bugs + passes their fixed forms. ADOPTED:
  jea_live_cost.binding_edge routes through single_edge_gains; decide_groundtruth guards its ratio with
  same_scale. Bonus (applying Δ-A2's own lesson to my test): decide_groundtruth's W1 was a single-shot
  luck-dependent verdict on a noisy laptop -- denoised to a median-of-K verdict with disclosed noise floor.
  (3rd check -- decision-path-not-name audit of SOUND deps -- stays a manual checklist item; not mechanizable.)

**Handoff (G8 — exhausted-from-inside, NOT verified):**
- **Δ-H1** ALL validation used ONE idle host's telemetry. The "PCIe structurally dominated / binding edge ∈ {iMC,thermal}" (W2) and "fstar = bandwidth ratio" (Δ-F4) claims are host-specific, untested on discrete-GPU / no-iGPU hardware or under real thermal load. For an external reviewer with such hardware.

## == REFINED TRAJECTORY — the polytope-cotype (sustainable, anti-shedding) ==

**Retrospective (gated) — why we kept shedding parts:**
- G0 PRECOMMIT: per-brick WAL + commit keeps everything; "unified" was near-done.
- G2 DELTA: fixes got ORPHANED in silos; audits ran from memory and went stale (coop "deadlocks").
- G3 ROOT CAUSE (systemic): the cotype was a LINEAR brick-LIST. A list cannot SEE an orphaned cell -- only an
  enumerated incidence MATRIX (faces x meets) can. We tracked the trajectory's steps, not its OBJECT.
- G6 SUSTAIN: per-brick WAL+DBE kept us context-stable across ~30 turns -- KEEP it; only upgrade the cotype's
  SHAPE from list -> polytope (the object the silos are projections of).
- G9 ESCALATE (the anti-shedding measure, correct-by-construction): make the cotype the POLYTOPE INCIDENCE
  MATRIX (every face + every meet = a CELL with status); C5's runner = the CLOSURE GATE asserting every cell
  is realized via the ONE engine. Then a fix is a cell-status update visible to the whole -> cannot orphan.
  This is registry-as-Pi ([[feedback_registry_as_pi_not_markdown]]), not a prose list. The cone's universal
  property mechanized = the unification's actual done-criterion.

**RETRO (recurring, G9 measure) -- PREDETERMINING inputs:** 5+ times this arc I substituted a GUESS for a
measured/derived value (either/or splits; detect-not-predict; "bucket dominates"; "coop deadlocks"; now
"work negligible" + P_coop=20) -- the model's STRUCTURE looked principled but an INPUT was guessed, so it
"validated" against my guess or mispredicted when measured. Root: no provenance distinguishes a measured
input from a guessed one, so under pressure the guess is the path of least resistance. MEASURE (correct-by-
construction): **every model/audit input carries PROVENANCE {measured:how | derived:from-what | GUESSED}**,
and a model with ANY guessed input is UNVALIDATED by construction (verdict can't be PASS). registry-as-Pi
for inputs + cost_cotype prove-or-reveal. Would have flagged P_coop=20 GUESSED -> C4 UNVALIDATED mechanically.
Dominance/regime is ALWAYS an OUTPUT of the full model, never predetermined (the fix witness 3 enforces).

**FACES (status in the ONE engine):** IN=in unified engine | SILO=lives in a silo only | HAND-FED=non-structural
```
F0 Evaluation     IN     (combine_window)                              genuine base 0-cell
F1 Carrier        PARTIAL (u64/u128 IN; byte-limb SILO jea_limb*)      genuine knob (predicted by magnitude)
F2 Schedule       IN     (coop/strat IN; pool in jea_engine_pool)      genuine knob (coop/strat/pool, MEASURED)
F3 Growth         SILO   (spawn in jea_engine_pool, not jea_engine)    genuine (fixed/spawn = one reduce-step)
F4 Control        VALIDATED-w/-residual (D1/D2 DISCHARGED as reframed, jea_live_cost.py: control reads the LIVE
                  Kron g_eff -- the binding edge derived by edge-sensitivity over discover()'s graph, re-polled,
                  NOT relax_q's GUESSED scalars and NOT decide()'s magic-constant ternary. The scalar fit stays
                  FALSIFIED (correct state). RESIDUAL: cross-thermal extrapolation synthetic-only on idle host.)
F5 Sharing        SILO   (jea_intern U7)                               not yet a knob in the engine
F6 Representation PARTIAL (value IN; trace SILO jea_carrier_trace)     genuine knob (value/trace, f*)
F7 Resource       SILO   (bucket U1; residency NOT asserted)           genuine knob (layout) + invariant
F8 Cost           VALIDATED-w/-residual (jea_live_cost.py: total_time = L·t_launch + tau/gnorm; t_launch MEASURED
                  (noop ~7us), tau MEASURED per schedule, gnorm = LIVE compute_bw ratio (the only per-window var).
                  GUESSED P_coop=20 + FALSIFIED t_work RETIRED. Oracle matches measurement at live state. RESIDUAL:
                  W3 live match is by-construction identity + labeled throttle projection; hot-state not validated.)
```
**INCIDENCES (face-meets; status = realized as its named construct in the ONE engine?):**
```
F1∩F3 escalation      IN (jea_engine_apex: deliver via byte-limb)   fix#1   [C3-apex DONE]
F3∩F5 interning       IN (jea_engine_apex: device hash-cons during spawn) fix#2 [C3-apex DONE]
F1   predict-place    IN (jea_engine_apex: tier by bit-width)        fix#3   [C3-apex DONE]
   ^^ these THREE were ONE vertex: Growth x Carrier x Sharing -- CLOSED as one brick (jea_engine_apex.py):
   E(120) interned to 121 nodes (vs 2.66e36 full tree = 2.2e34x collapse), root 2^120 exact, tiers predicted
   (u64x64/u128x57, err=0 sound), 2^150 delivered via byte-limb. The missing apex is closed.
F1∩F6 value<->trace   SILO   (jea_carrier_trace)                  -> C4/C-rep
F1∩F7 bucket-pack     SILO   (U1)                          fix#6   -> C-resource
F2∩F7 residency       ORPHAN (not asserted)               fix#5   -> C4/C5
F4∩F8 oracle          IN-w/-residual (jea_live_cost.py: argmin total_time over the live Kron-solve, NO guessed
                  input -- matches measured coop/strat winner on deep+wide at the live state. coop/strat/pool = ONE
                  series decomposition over shared live edges (the common structure). RESIDUAL: hot-state synthetic.)
F4∩F2 K-adapt         PARTIAL (Kbuf/relax IN; refill SILO U9)     -> C4
witness three-state   ORPHAN (engine can mask escalation) fix#4   -> C5
```
**THE VECTOR (ordered closure trajectory toward the apex = the closed n-cell):**
1. **C3-apex** [DONE -> jea_engine_apex.py] — Growth x Carrier x Sharing closed: device hash-cons interns
   during spawn (E(120): 121 nodes vs 2.66e36, 2.2e34x collapse), predict-place tier by bit-width (sound,
   err=0), byte-limb delivers 2^150. fixes #1+#2+#3 closed as ONE vertex.
2. **C4** [CORE DONE -> jea_cost.py] — Control∩Cost: structural schedule cost (launch_count(S)·t_L + fixed,
   2 machine constants, crossover S*=38 DERIVED) + oracle (argmin), validated by EXTRAPOLATION (calib deep,
   predicts wide). F8->structural, F4∩F8 oracle IN. C4-REST (still open): residency-assert (F2∩F7),
   K-refill (F4∩F2, launch_count = U9 refill makespan), point jea_consolidation_pilot at jea_cost.
3. **C-rep / C-resource** — fold value<->trace (F1∩F6) and bucket-pack (F1∩F7) into the carrier as params.
4. **C5** — the regression runner = the universal-property check: every prior witness AND every incidence
   cell above is realized via the ONE engine. Closure gate; only then is "unified" honest.

**SUSTAIN (anti-shedding discipline, standing):**
- The cotype IS this polytope matrix (faces + incidences as cells with status), NOT a brick list -- every
  fix/build is a cell-status update; an orphan shows up as a SILO/ORPHAN cell that the matrix forces visible.
- Ground every face/meet on CURRENT CODE + MEASUREMENT, never remembered history.
- Cost models STRUCTURAL (self-revealing factor-signatures), never hand-fed numbers.
- Each turn: read the matrix -> close ONE cell -> flip its status -> commit (WAL atomicity, now over cells).
- "Unified" is FALSE until C5's gate shows every cell IN. Do not re-claim completion before the gate passes.



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
claim, jea_roofline --ablate) -- a pure verification debt, not modeling or unification.

CORRECTION (user caught it): "both apexes complete" was an over-claim -- complete as PROOFS, NOT as a
unified ARTIFACT. See the CONSOLIDATION ARC below: the unification is enacted only when ONE engine
reproduces every brick witness. The U-bricks stand as proofs/regression-witnesses; the engine is unbuilt.

## CONSOLIDATION ARC (C-bricks) -- enact the unification as ONE artifact

RUNG: R(observable, transitions)

**Retrospective (gated, on the silo-sprawl finding):**
- G0 PRECOMMIT: I claimed "both apexes complete."
- G1 FREEZE: ~dozen jea_* scripts; jea_core shares the CONTROL law but combine BODIES are duplicated
  (dag_mode + strat_mode each bolted MODE on separately; 3 carrier scripts; engine/intern/oracle separate).
- G2 DELTA: complete as PROOFS (every piece demonstrated + composes) but NOT as a unified ARTIFACT --
  unification narrated, never enacted. U6 ("the universal engine") is itself just one more demo script.
- G3 CAUSE: trigger = narrating "fused" on conceptual composition. Root (systemic): the per-brick WAL/DBE
  discipline that kept the arc context-flush-stable REWARDS silos (one brick = one standalone artifact);
  it optimizes verifiability -- the OPPOSITE of "fold into one kernel." Contributing: jea_core shared the
  control law but not the combine bodies, so the shared spine looked more complete than it was.
- G5 BLAMELESS: no gate required a unification CLAIM to produce the unified ARTIFACT.
- G6 SUSTAIN: the scripts are correct + witness-bearing -- keep them AS the regression suite, not delete.
- G7 COMMIT: build the consolidated engine; scripts reduce to thin callers + a regression runner.
- G9 ESCALATE (correct-by-construction): C5's regression runner IS the binding gate -- the unification is
  "done" only when ONE engine reproduces EVERY brick witness; a brick that won't fold FAILS the gate.
  Claim-requires-artifact, mechanized (not a narrated "complete").

**DBE costructure (the apex):** ONE parameterized engine on jea_core --
`Engine(carrier, mode, schedule, layout, repr) -> evaluator`. The ~dozen scripts are ORBIT-ELEMENTS of
this parameter space (RFS: extract the universal above >=3 instances; NOT a wrapper -- the axes are the
generators). The Agda bridge (jea_agda_*) + ablation harness (jea_roofline) stay separate (not engine
internals). Composition = each axis lifted to a parameter/step_fn; entailment = consolidation is correct
IFF the engine reproduces every prior brick's committed witness (so C5 is the proof the fold is faithful).

**C-brick transitions (state -> morphism -> state  [preconditions = entailment]):**

```
C1  duplicated combine bodies  --carrier-typedef + mode/K runtime params, ONE CUDA source-->  one parameterized combine  [DONE]
                                          [jea_engine.py: ONE _SRC compiled per carrier (-DCARRIER_U128); reproduces dag(u64 eager)
                                           canonical / dag_mode(eager,lazy, 84 non-canon) / dag128(u128 escalate); CARRIER WIDENS proven
                                           (81b DAG: carrier64 escalates, carrier128 exact); u128 240b all-mul escalates; jea_core,I1,dag128]
C2  separate schedulers        --schedule as a STRATEGY over the C1 combine-->  one driver, schedule param  [DONE]
                                          [jea_engine.py: combine_window = ONE device fn; sched_coop + sched_strat CALL it (no copied
                                           combine); coop==strat on same DAG both carriers (schedule orthogonal to combine); reproduces
                                           dag/dag_mode (coop) + strat (strat); C1, strat]
                                          RE-SCOPE RETRACTED (user: "when faced with an either-or, find the common structure, recursively"):
                                          I wrongly called spawn "a distinct axis" -- that WAS the either/or fallacy. The common structure
                                          (jea_engine_pool.py, PASS): ONE reduce-step `reduce(node) -> EMIT value | SPAWN children`, scheduled by
                                          readiness over a pool that GROWS iff a rule spawns. Fixed-DAG fold = every rule TERMINAL (no spawn,
                                          pool static) = the SPECIAL CASE; rewrite = a spawn rule (pool grows); escalation = spawn a wider-carrier
                                          node = the same act. It is the generator_step primitive (emit-or-carry) recursively: residue = (a,b) gcd
                                          pair at the VALUE level (combine_window already carries it), = spawned children at the STRUCTURE level.
                                          Proven: one kernel runs BOTH the Q-fold (70785/8 exact) AND E(n)->2^n. The growable pool is the GENERAL
                                          scheduler; coop/strat (C2) are no-spawn special cases of it. [revises the C-arc -- see C3'/below]
C3  carrier ladder, separate   --escalate-tier as a SPAWN, PREDICTED (u64->u128->byte-limb)-->  carrier ladder folded  [PARTIAL]
                                          [jea_engine_tiers.py: the result tier is PREDICTED from operand bit-widths (migration law) BEFORE
                                           computing -- the combine is PLACED at the right tier, never compute-narrow-overflow-retry (I2:
                                           predict don't detect; user caught my detect regression). 8-prime all-mul (240b root): predicted
                                           tiers {12 u64,2 u128,1 byte-limb}, 3 spawns, prediction SOUND (>=actual, no overflow), root exact,
                                           byte-limb DELIVERS via jea_limb GPU; same reduce->emit|spawn as E(n). Folds U3+I2]
                                          DONE: escalate-tier-as-(predicted)-spawn. FOLLOW-ONS (carrier storage/repr params, orthogonal to the
                                          reduce-step): U1 bucket-pack lanes; U4 trace-window lane; on-device byte-limb tier.
C4  intern + oracle separate   --wire intern (pre-pass) + nedge oracle (live steer) as engine STAGES-->  one pipeline
                                          [reproduces U7 collapse + M2d/U9 steering; C2, U7, M2d, U9]
C5  N demo scripts             --demos -> thin callers + a REGRESSION RUNNER over the single engine-->  unification ENACTED
                                          [every prior brick witness passes via the ONE engine = the G9 gate; C1-C4]
```

**CONSOLIDATION AUDIT (jea_consolidation_pilot.py -- nedge knobs+measures, dominance check):** validated the
unification has NO missed consolidations EXCEPT one. A "knob" is genuine iff its winner FLIPS across the
config space; a setting that wins under all circumstances is a FALSE knob (collapse it). Findings (bounded
to the modeled space + cost models, grounded in U1/U2/U9/trace-window/charter):
- GENUINE knobs (winner flips -> oracle-steered, correctly kept): mode (eager/lazy), repr (value/trace),
  K (window), layout (flat/bucket -- flat wins uniform-large where bucketing gives no density gain; this
  CORRECTED my pre-baked "bucket dominates" assumption -- the pilot caught it; borderline on bucket overhead).
- DERIVED (data-determined, not a free knob): carrier (predicted by magnitude, C3).
- schedule (coop/strat/pool): GENUINE 3-way knob -- CORRECTED. My first audit called coop "dominated" on the
  STALE grounding that "coop deadlocks past ~3/SM" -- but that deadlock was FIXED (revisit-readiness gate, no
  spin-wait; user caught the stale assumption). RE-GROUNDED BY MEASUREMENT: on a deep-narrow chain coop is
  3.2 ms vs strat 14.0 ms = 4.4x FASTER (one persistent launch vs launch-per-stratum); strat wins wide
  (occupancy); pool wins dynamic. The launch<->occupancy<->dynamic Pareto -- a real knob the oracle steers.
- MISSED CONSOLIDATIONS: NONE. Every axis is a genuine knob or data-derived. The earlier "coop dominated"
  was an audit built on a FIXED bug -- retracted.
FOUR pre-judgments the discipline caught this arc (either/or->common structure; detect->predict; bucket-
dominates->knob; coop-dominated-from-stale-deadlock->measured-genuine-knob). The last is the sharpest:
I asserted dominance from a stale INPUT (a fixed deadlock) instead of MEASURING the output. LESSON: ground
audits on measurement, not remembered history -- and there are likely MORE forgotten fixes (the silo sprawl
wrote fixes to individual scripts that never propagated). [-> dispatching fix-archaeology over git history.]

**Status (consolidation):** C1 (jea_engine.py: one parameterized combine, carrier typedef + mode/K) + C2
(combine_window = one device fn, sched_coop/sched_strat call it; coop==strat). C-arc REVISED by the
common-structure finding (jea_engine_pool.py): the GENERAL scheduler is the GROWABLE POOL with reduce-step
`reduce -> emit|spawn`; coop/strat are its NO-SPAWN special cases, and spawn/rewrite (U6) + escalation are
the spawn case -- ONE engine, proven on both the Q-fold and E(n). So C2's "spawn is distinct" is retracted;
the real apex scheduler is the pool. REMAINING C-bricks (re-cast on the pool engine): C3 carrier OPS
(bucket/escalate-tier/trace as carrier params -- escalation now = a spawn), C4 oracle/intern as stages,
C5 regression runner (one engine reproduces every witness = the gate). After C1-C5, "both apexes
complete" becomes true as an ARTIFACT (one engine, the scripts its callers/tests), not just a proof.
Trailing: U10 (re-ablate Z-128) -- cleaner once there's a single kernel to ablate. Caveats held: one
parameterized kernel FAMILY (shared body, compiled per carrier), not literally one launch for all carriers
(the residency cliff); find the real seams while building.
