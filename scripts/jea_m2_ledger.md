# JEA M2 runtime — WAL cotype (the on-device dataflow scheduler)

Charter M2: the real on-GPU term-algebra evaluator. The kernel-perf nedge arc built the dispatcher
ORACLE (control law); M2 is the actual on-device scheduler the oracle steers. Built MATURE per
[[feedback_grow_to_maturity_not_approximate]] -- no stubs that become scar tissue.

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
- **M2d — close the dispatch loop.** The nedge oracle (live_dispatcher) sets work distribution /
  priority over the queue via the zero-copy control buffer (AI-11b) -- live, anytime. The bottleneck/
  f* decision steers which nodes/strata the kernel prioritizes. This is the "spit-take" demo:
  Agda term -> GPU dataflow -> live-scheduled exact evaluation.

## Status

M2a DONE (jea_m2_workqueue.py); M2b DONE (jea_m2_dag.py); M2c DONE (jea_m2_qcarrier.py). M2d is the
last brick. Each is mature-or-nothing (no stubs). The dispatcher oracle (el-atlas nedge program,
ai_ledger.md) is complete and feeds M2d. Next = M2d: the nedge oracle steers the live sweep via the
zero-copy control buffer (AI-11b mechanism) + the value-window<->trace-window Pareto choice = the
spit-take demo (Agda term -> GPU dataflow -> live-scheduled exact evaluation).
