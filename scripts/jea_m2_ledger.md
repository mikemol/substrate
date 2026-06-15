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
- **M2b — dependency dataflow.** Nodes consume CHILDREN's results (a node's a/b are indices into res,
  not immediates) -> the SPPF DAG. A node is ready only when its children are done; respect deps via
  stratification (topological strata, the cooperative-megakernel pattern) or a ready-flag + spin.
  Entailment: M2a's exactly-once drain + a readiness gate -> correct DAG evaluation.
- **M2c — gcd-window fusion / real carrier.** Each node processes a WINDOW of the EEA/CF trace (the
  suspended-generator carrier); swap int64 for the bignum/Q carrier (jea_swar_* / jea_trace_window).
  Fuse the gcd/Euclid windows per node (pay-per-unfold). Heterogeneous depths handled by the queue
  (deep nodes = more windows = more dequeues; the lock-free queue load-balances naturally).
- **M2d — close the dispatch loop.** The nedge oracle (live_dispatcher) sets work distribution /
  priority over the queue via the zero-copy control buffer (AI-11b) -- live, anytime. The bottleneck/
  f* decision steers which nodes/strata the kernel prioritizes. This is the "spit-take" demo:
  Agda term -> GPU dataflow -> live-scheduled exact evaluation.

## Status
M2a DONE (jea_m2_workqueue.py). M2b/c/d are named bricks; pick up from here. Each is mature-or-nothing
(no stubs). The dispatcher oracle (el-atlas nedge program, ai_ledger.md) is complete and feeds M2d.
