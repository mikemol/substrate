# JEA M2 runtime — WAL cotype (the on-device dataflow scheduler)

HONEST SCOPE (read first): the on-device dataflow evaluator ALREADY EXISTS and is more advanced than
these four scripts -- the jea_generator_* ladder (persistent -> exact-Q controller -> cooperative ->
stratified/bucketized ~847M nodes/s -> Ackermann -> byte-limb -> SWAR), and the primary Agda-on-GPU
spit-take is ALREADY CLOSED end-to-end via jea_agda_bridge.py (commit 8046b4c). See the charter memory.
These jea_m2_* scripts are a CLEAN, SELF-CONTAINED, witness-per-script RE-REALIZATION of the core
dataflow (queue -> DAG -> Q-carrier+escalate -> oracle-steered dispatch), useful as a legible reference
build. The genuinely NEW contribution is M2d's live value-window<->trace-window (eager/lazy reduction)
Pareto steering -- a distinct operating-point knob from the existing K-window controller.

Built MATURE per [[feedback_grow_to_maturity_not_approximate]] -- no stubs that become scar tissue.

Shared costructure (strictification): a persistent megakernel draining a lock-free device work-queue
of term-algebra nodes (SPPF: gen / (+) / (*)), steered by the nedge oracle via zero-copy control
(the AI-11b mechanism). Each brick adds one capability over the same queue+kernel.

## Bricks

- **M2a — lock-free work-queue drain. [DONE -> jea_m2_workqueue.py]** Persistent megakernel drains a
  queue of independent term-nodes (gen/+/*) EXACTLY-ONCE via atomicAdd head; 200k nodes, correct vs
  host reference, one launch. The real dataflow core (replaces the AI-11b toy bucket stub). int64
  carrier; generalizes to the bignum/Q carrier.
- **M2b — dependency dataflow. [DONE -> jea_m2_dag.py]** Nodes consume CHILDREN's results (a/b are
  indices into res) -> the SPPF DAG. Persistent DATA-DRIVEN sweep: threads repeatedly scan the node
  array, atomicCAS-claim (PENDING->CLAIMED) any node whose children are DONE, evaluate from children,
  fence, mark DONE; loop until completed==n (fixpoint) or stop. Deadlock-free by construction (leaves
  ready immediately; frontier advances each sweep; DAG = acyclic). 60k nodes, correct vs host DAG
  reference, ONE launch (no per-stratum relaunch). Entailment realized: M2a's claim + a children-done
  ready-gate -> correct DAG evaluation.
- **M2c — gcd-window fusion / real carrier. [DONE -> jea_m2_qcarrier.py]** Carrier = Q=(num,den),
  den>0, kept REDUCED. Each (+)/(*) computed in __int128 (NVRTC --device-int128) then canonicalized by
  an on-device Euclid loop = the FUSED GCD WINDOW (bounded walk, finite-window-constructive). Window
  DEPTH varies per node (min 1 / max 35 / mean 4) = heterogeneous depths absorbed by the sweep.
  ESCALATE-DON'T-TRUNCATE: post-reduction, if |num| or den won't fit int64 -> FLAG (esc=1), never wrap;
  poison-propagates to consumers. Witnesses PASS on a 54k DAG + a distinct-prime chain that forces
  escalation: 54039 exact vs host Fraction + canonical (gcd==1); 10 escalated == the unrepresentable
  set EXACTLY (no silent wrap). The "exactness/canonicality" arm of the value<->trace-window Pareto;
  trace-window dual (CF-shape carrier, compare-by-prefix) is the M2d Pareto knob.
- **M2d — close the dispatch loop. [DONE -> jea_m2_dispatch.py]** The el-atlas nedge oracle steers the
  M2c exact evaluator LIVE via the AI-11b zero-copy channel into a RESIDENT (spin-waiting) kernel. What
  it steers = the value-window<->trace-window PARETO: MODE=1 EAGER (reduce every op -> canonical, costs
  gcd-work) vs MODE=0 LAZY (reduce only when the lane forces it -> throughput, non-canonical, reduce-on-
  demand). Both exact. Measured Pareto (40k DAG): eager 147604 gcd-ops / 0 non-canonical; lazy 5429
  gcd-ops (27x less) / 33887 non-canonical. Oracle (resistance-sum / geodesic settle) picks MODE from
  telemetry + workload canonicality-demand C; decision FLIPS across the bridge-null f*=C*=4.20. Live:
  resident kernel waited 0.10s for the zero-copy GO, then ran the oracle's schedule to completion. NOTE:
  the DAG here is synthetic (SPPF-SHAPED gen/+/*), not wired to the Agda bridge -- the end-to-end Agda
  path is the existing jea_agda_bridge (8046b4c); the new piece is oracle-steered LIVE eager/lazy Pareto.

## Status

**jea_m2_* RE-REALIZATION COMPLETE.** M2a (jea_m2_workqueue.py) -> M2b (jea_m2_dag.py) -> M2c
(jea_m2_qcarrier.py) -> M2d (jea_m2_dispatch.py), all DONE, all mature (no stubs), witness-checked. A
clean self-contained reference build of the on-device dataflow core, with the NEW live eager/lazy
(value<->trace) Pareto knob steered by the nedge oracle via zero-copy. This does NOT supersede the
existing jea_generator_* ladder (more advanced) or the closed Agda bridge (jea_agda_bridge, 8046b4c).

INTEGRATION FOLLOW-ON (the real next step, not blocking): wire M2d's live eager/lazy Pareto steering
into the production evaluator -- i.e., add the value<->trace reduction-mode knob to jea_generator_dag/
strat/bucket's controller (which today steers only K, the gcd-window size), and drive an Agda-bridge-
emitted DAG (jea_agda_bridge) through it. That fuses the new contribution with the existing closed path.
Other follow-ons: trace-window as a literal CF-shape lane (compare-by-prefix, no reduce pass); byte-limb
as the escalation target (the carrier in jea_limb_gpu); het CPU+GPU dispatch (het-dispatch nedge pilot).
