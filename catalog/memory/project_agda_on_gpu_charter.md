---
name: project_agda_on_gpu_charter
description: "Design charter (acceptance criteria) for foundational Agda-on-GPU — the term-algebra → GPU evaluator. The PRIMARY goal now (over condensing the substrate). On-GPU traces, faithful (no truncation/hidden quotient), bandwidth-hoarding/compute-spending engineering."
metadata: 
  node_type: memory
  type: project
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

The PRIMARY goal (user, 2026-06-13, supersedes the condense-the-substrate angle): a
**foundational Agda-on-GPU** evaluator — the term-algebra → GPU "Just Enough Agda" /
mini-MAlonzo — "working well enough to cause spit-takes." Everything is term algebras +
folds; a fold into a GPU carrier is the evaluator. Lives in the repo-root .venv
([[reference_python_venv]]: cupy-cuda13x, sympy, numpy).

**ACCEPTANCE CRITERIA (the user will be looking for these):**
1. **Calculation almost entirely on-GPU.** Traces stay device-resident; the trace DAG IS
   the memo table (shared subterms = computed once). No host round-trips.
2. **Recompute from residues-on-hand, don't copy across a memory boundary.** Compute is
   cheaper than bandwidth: when a value is far (HBM / another SM) but its residue is near
   (SM / registers), RECOMPUTE it. This is [[feedback_never_discard_residue]] and literally
   [[project_substrate_real_arc]] ("reason about ℝ via the trace, never hold the value") —
   the EEATrace residue lives on-GPU; values are forced near compute, never materialized
   and moved.
3. **No regexy funny business** — a real evaluator over the term AST (folds like
   `inside`/`foldUPTerm`), never text munging.
4. **No hidden quotienting / truncation** — exact carriers, no float. ℚ keeps (num,den) +
   reduction is the EXPLICIT wedge/EEA, never silent reduce-and-drop. Overflow is DETECTED
   and ESCALATED (fixed-width → multi-limb), never wrapped.
5. **Geometric model of computer+GPU; spend compute, hoard bandwidth.** Working set in
   SM/registers; only immediately-relevant data near compute; recompute-vs-fetch is a
   first-class scheduling primitive (decide per-edge: value-size×distance vs
   residue-size×recompute-cost). Exploit cache/locality; minimize crossings.

**ARCHITECTURE:** trace = device-resident SoA DAG (`tag[]` + child-index arrays),
interned (shared subterm = one node = memoization = SPPF/Register packing); fold =
bottom-up, SM-local (residues stream into shared mem, internal values recomputed in-SM,
only results spill); carriers exact, escalate-don't-truncate.

**SEQUENCING (foundational fork = exact-arithmetic representation):**
- M1: F₂ / small-finite carrier (exactness free) → prove the DATAFLOW (resident trace,
  SM-local fold, zero host copies, zero truncation, DAG-memoized) — the spit-take.
- M2: ℤ/ℚ via fixed-width lanes + overflow→multi-limb escalation; recompute-from-residue
  earns its keep (recompute a reduction from the EEA trace in-SM vs fetch a materialized ℚ).

STATUS: **M1 DONE** (`scripts/jea_gpu.py`, runs in the .venv on the RTX 4050). SPPF
`inside`-fold over F₂: device-resident interned-DAG trace, branchless CUDA RawKernel
combine (`(mg&gval)^mo^(mm&(a&b))^(ma&(a^b))`, leaf children→node 0 masked, only the
tail guard conditional), one launch per (contiguous, coalesced) level. Verified: chain
demo folds a 2⁴⁰≈1.1e12-leaf expression as an 82-node DAG vs closed form AND host fold;
wide demo 65M nodes in 8.4 ms (~7.7G nodes/s), 715 MB resident, 0 host copies, kernel
cross-checked vs host fold. **M1.5 DONE** (same file, `_fold_subtree_f2` + `demo_tiled`): SM shared-memory tiling. A
balanced mixed-op tree folded so each block owns a subtree — bottom s levels folded
ENTIRELY in `__shared__` (register-staged read/sync/write, no race; adjacent-pairing
preserved since mixed ⊗/⊕ makes the pairing load-bearing — stride-reduction would be
wrong); only the subtree root spills. Branchless combine; only branch = structural stride
guard. CONTROLLED A/B (`demo_compare`, same 2²²-leaf tree, both GPU, JIT-warmed, min-over-reps):
per-level global ~0.28 ms / ~12.6 MB value-traffic vs bottom-9 shared-tiled ~0.26 ms /
~4.2 MB ⇒ ~1.1× faster, ~66% less value round-tripped (analytic). The TIME win is modest
BY DESIGN — F₂ values are 1 byte so the fold is launch/latency-bound, not bandwidth-bound;
tiling moves 66% less data but it barely shows in time. **MEASUREMENT LESSON: an earlier
"55× faster" was the first-call nvrtc JIT compile caught inside the timer; and "65M@8.4ms
vs 4.2M@1.09ms" were non-comparable workloads. Always warm the JIT and A/B the SAME
workload.** F₂ cannot show a time spit-take ([[feedback_test_the_wall_before_declaring_it]]
sibling: don't trust a headline number without a controlled, warmed comparison). The
recompute/bandwidth WIN converts to TIME only on M2's large carriers (exact ℚ).

**M2 DONE** (same file: `_combine_level_i128`/`_fold_subtree_i128` + `demo_compare_i128` +
`demo_overflow_i128`). Exact ℤ via `unsigned __int128` (16-byte values, lo/hi uint64 lanes,
nvrtc `options=('--device-int128',)`). Branchless combine; overflow DETECTED (add carry-out;
mul division-check) → sticky flag = the escalate signal, never a wrap. Same-tree A/B,
JIT-warmed, VERIFIED EXACT vs Python bignum: 2²²-leaf exact-ℤ ⊕-tree (82-bit result, flag 0)
→ per-level 1.48 ms vs SM-tiled **0.75 ms = 1.98× FASTER**. THESIS CONFIRMED: 16-byte values
are bandwidth-bound, so SM residency converts to TIME — the win F₂'s 1-byte values couldn't
show (~1.1×). Escalate-don't-truncate proven: a ⊗-tree with a 9882-bit exact product sets
the flag = 1 (detected, not wrapped).

**DEVICE-SIDE TRACE BUILDER DONE** (same file: `build_balanced_device` / `btags_device` /
`inside_tiled_device` + `demo_device_build`). The per-block btags layout (was an O(nblk·s)
host Python loop, ~57 ms at 2²²) is now a vectorised cupy reshape+scatter, O(s) device ops;
leaves+tags generated on-device (cp.random/cp.full). Warmed A/B: btags layout ON GPU
0.17 ms vs host Python 57 ms = **333× faster**, device==host verified, device-native exact-ℤ
fold 0.76 ms, root exact vs host bignum. (Again a transient 610 ms was first-call cuRAND
init — warm before timing.)

**M2b/ℚ DONE — the exact-arithmetic ladder is COMPLETE** (same file: `_combine_level_q` +
`inside_perlevel_q` + `demo_q` / `demo_q_overflow`). Exact ℚ as (num:i128, den:i128>0),
32B values; +/× exact rational, then the EXPLICIT reduction gcd(|num|,den) (branchless
fixed-iter Euclidean) — the wedge/EEA, no hidden quotient. Overflow of num/den OR the
intermediate products (incl. add-numerator SUM) DETECTED → escalate flag, never wrapped.
SWP probability carrier (fraction leaves). h=6: root BIT-EXACT vs Python Fraction, flag 0.
h=12: exact value needs 781 bits (>128) → flag 1 (detected). LADDER: F₂ (M1) → ℤ-128 (M2)
→ ℚ (M2b/ℚ), all exact, all escalate-don't-truncate.

**LESSON (checker bug):** the ℚ kernel was correct from the start; my `_host_fold_q`
verifier used `mul=(tg[0]==MUL)` — applied the level's FIRST tag to EVERY pair, so mixed-op
trees got a WRONG ground truth and the correct device result "failed". A green/red verdict
is only as trustworthy as the verifier — localize with micro-tests (h=1 passed, h=2-mixed
failed → the verifier). [[feedback_test_the_wall_before_declaring_it]] sibling.

**tiled-ℚ measured ~0.82x SLOWER than per-level (the prediction "32B ⇒ bandwidth-bound ⇒
tiling wins" did not hold)** — `scripts/jea_roofline.py`, the durable ABLATION instrument.
EPISTEMIC NOTE (the user caught me reasoning by EXCLUDED MIDDLE here — [[feedback_reject_lem_in_substrate]],
[[feedback_negative_findings_in_corpus]]): each mispredict I flipped into a categorical
negation ("NOT compute-bound", "static SASS lied, trust ablation only") that refuted the
prior and narrowed the admissible set — LEM, in the project built to reject it. The honest
intuitionistic reading: the axes COEXIST; no look refuted a prior look; "not BINDING at this
operating point" ≠ "false". value-size, SASS-intensity, latency are COORDINATES of one
multi-axis carrier ([[feedback_wedge_not_projection]]), and every claim is bounded to
(workload, config). Bounded findings (NOT laws):
  * value-size named the BANDWIDTH axis; at this workload/config it was not the binding one.
  * SASS named the COMPUTE axis (the 256-iter nested 128-bit-divide is real, expensive in
    isolation); at this operating point the 5 software-128-bit multiplies + 2 divides added
    ~0 ms — they hid under memory latency. (The `(b!=0)?(a%b):0` ternary is PREDICATED, so
    `a%b` runs every iter — the gcd window is ~20% of runtime, windowing 256→4 ≈ 1.2x.)
  * ablation RANKED the axes at this point: the floor is set by memory latency / launch
    (~402 MB in ~16.6 ms ≈ 24 GB/s of the 4050's ~200 GB/s ⇒ few in-flight requests). Static
    analysis NAMES axes; ablation RANKS them at an operating point — hold both, neither
    refutes the other.
  Tiling slower here = it cut BYTES (not the binding axis at this point) while cutting
  OCCUPANCY (the binding one: latency-bound kernels live on in-flight-request count; the
  reduction tree drops to 22% dynamic thread-util). WHICH axis binds is itself a coordinate
  that shifts with the workload — which is the technical reason the answer is dynamic
  rebalancing (my LEM reasoning-bug was isomorphic to the kernel's static-single-point bug).
  [TODO: re-ablate the M2 ℤ-128 "1.98x tiled" headline under the same harness — it may rank
  differently than first reported; not asserting it's wrong, just unverified by ablation.]

**THE BOTTLENECK IS MULTI-AXIS; the answer is DYNAMIC on-device rebalancing** (user,
2026-06-13). Axes identified by measurement: (1) ALU/compute (gcd; binds only when the loop
is long enough not to hide), (2) memory BANDWIDTH (bytes; the tiling axis; not binding here),
(3) memory LATENCY/MLP = occupancy (THE binding one), (4) LAUNCH/dispatch chain (22 dependent
launches), + (5) thread-UTILIZATION/divergence (the coupling axis). These form a TRADEOFF
SIMPLEX — every static knob moves several at once (tiling: bandwidth↓ but occupancy↓; gcd
window: compute↓ but divergence↑; fuse launches: launch↓ but reg-pressure↑). A static kernel
is ONE fixed point; a heterogeneous DAG (deep-gcd vs trivial nodes; wide vs deep subtrees)
has DIFFERENT optima per sub-batch ⇒ no single point is right. Hence the correct architecture:
data-dependent rebalancing decided ON THE GPU (the deciding residue is device-resident; a host
round-trip costs more than the work) via INDIRECT / PARAMETERIZED LAUNCH dispatched by an
on-device process — CUDA Dynamic Parallelism (CDP2, Ada-supported), device graph launch
(CUDA 12+, tail/sibling launch collapsing the dependent chain), or a PERSISTENT MEGAKERNEL +
on-device work queue (the more tractable first build — one launch + a device-side scheduler
loop, no `-rdc=true`/device-runtime-link wrinkle that CDP imposes under cupy/NVRTC). This is
charter criterion #1 raised from the DATA plane to the CONTROL plane, with #2 (recompute-vs-
fetch) as one per-edge rebalancing decision; it is [[feedback_never_discard_residue]] applied
to the SCHEDULING resources (keep all axes live, rebalance; the dispatcher is a coalgebra over
(compute,bandwidth,latency,launch) unfolding launches from the trace). The user's earlier
"partial-EEA-ladder, pack work into freed slots" is the SPECIAL CASE for the gcd axis.

INSTRUMENT: `scripts/jea_roofline.py` (`--ablate`/`--bench`/`--sass`) — counter-free roofline
by ablation. ncu HW counters are root-gated here (`RmProfilingAdminOnly:1`, sudo needs a
password ⇒ ERR_NVGPUCTRPERM); cupy-under-ncu NVRTC header crash is fixed with `CUDA_PATH=/usr`.
nsys/cuobjdump/--resource-usage/cupyx.benchmark all work unprivileged.

**THE DISPATCHER'S DECISION ENGINE = a NEDGE generator network over exact ℚ** (user,
2026-06-13; `scripts/jea_nedge_model.py`). NOT bespoke scheduling logic — it is the
el-atlas **G-Value Calculus** (the electrical evidence framework, nedge-decomposition §6):
conductance G∈ℚ, G_OR=ΣG (parallel), G_AND=1/Σ(1/G) (series), G_NOT=1/G; the **Wheatstone
bridge** (§8) picks tunables by signed comparison-of-comparisons; readings via pluggable
semiring (tropical (min,+) = the HARD binding breaker / Viterbi corner; conductance (×,+) =
the SOFT margins — keep BOTH, the not-LEM discipline). THE VANTAGE (the unifying structure
the user steered to, [[discipline/feedback_common_substructure_recursively]]): a carrier
value is a **suspended generator** (EEATrace/gcd not-yet-forced); a pass observes a bounded
**window** of K steps; converged nodes EMIT+free their slot, unconverged ones CARRY their
(a,b) residue and CONTINUE — the dual rail IS the generator's split **E⁺=forced value,
E⁻=suspended continuation**. "Escalation" is not a branch/floor/separate-impedance (those
were three views of ONE thing) — it is the residue continuing = the "pack work into freed
slots" refill applied gcd-internally. SELF-SIMILAR: gcd-step/window/(a,b) ≅
node-fold/slot/subtree ≅ level-cascade/pass/pending. FITTED TOPOLOGY (reproduces all 5
ablation points): dependent ALU chain (gcd) is SERIES with memory (the dependency starves
MLP — 256-gcd = 16.46+5.48); independent ALU (mul/ovf) HIDES by ILP = tropical MAX co-issue;
windows in SERIES, each RE-PAYS t_mem iff residue NON-resident (global) but only the cheap
ALU max iff RESIDENT — so recompute-from-residue (charter #2) = choosing which RAIL E⁻
continues on (a G_OR parallel pick, not a branch). Result: residue-on-E⁻ flips the flattened
model's wrong K-pick (global optimum = smallest 1-pass K=3; K=2 catastrophic = 2× memory);
the RESIDENT lever pays only on DEEP/HETEROGENEOUS workloads (few ~185-step adversarial nodes
among shallow) — which IS the dynamic-rebalancing case. Model's next gap: mixed-depth REFILL
dynamics (deep nodes holding lanes) not yet in it. THE CONTROLLER IS A CONTINUOUS ANYTIME
FIXED-POINT ITERATION, not a periodic solve (user, 2026-06-13): the G-calculus equilibrium IS
a least-fixed-point (el-atlas §7.2 pair power-iteration / Perron) reached by RELAXATION, and
since telemetry never stops drifting the controller NEVER halts — one warm-started step per
iteration (warm-started from its own current iterate = the equilibrium estimate = its carried
residue), the current K/rail ALWAYS live in the control buffer (anytime; workers read it with
no barrier, async to the controller). Taking the converged value would be the unbounded-
decision LEM trap; the bounded current iterate IS the answer (Tarski tower walked, never
halted — [[feedback_finite_window_constructive_lem]]). SELF-SIMILAR: the controller is itself
a suspended generator continuously forced (observe a datum, advance one step, carry the
iterate) — same shape as the gcd window and the node fold; the scheduler's brain is the same
object it schedules. SPEC/ORACLE for the device controller: `scripts/jea_nedge_model.py`
(control law + closed-loop tracking sim — K climbs 64→256 on a deep burst, relaxes back, no
oscillation; the ovf-divisions create a cost PLATEAU [max_depth, ~121] where K is a free
variable, so the loop fiddles K only when max_depth>K — a live-control insight static analysis
misses). Deployment = persistent megakernel: worker blocks (windowed fold + refill + telemetry
stream) ∥ a controller block (the continuous relaxation), branchless (the decision is the
equilibrium current, not an if). UNIFICATION (user, "find the common structure recursively"):
worker, controller, AND their comms are ONE primitive — `generator_step : state ↦ (emit,
state′)` = observe a window (of own residue + shared STORE) · step once · publish (into store)
· carry residue. Worker and controller are the SAME primitive with different step_fn; "async
comms" is NOT a third thing, it is COMPOSITION (one generator's publish = another's observe,
via the store); RECURSIVE (a step_fn is itself a generator — worker's gcd-window over Euclid
steps, controller's relaxation over iterates). Proven in the oracle: `worker_step` and
`worker_step_relax` are both `(state,store)→(emit,state′)`, composed via one store, loop tracks
(K 64→256 on deep burst, relaxes back). So the DEVICE BUILD IS ONE THING: a persistent block
running `generator_step` over a global-memory store, instantiated per role (identity step_fn
first to prove persistent-residency + async observe/publish/threadfence, THEN relaxation =
controller, THEN gcd-window = worker). Not three builds. The on-device ℚ controller verified
against this oracle (same exact ℚ ⇒ identical K decisions).
**INCREMENT (1) DONE** (`scripts/jea_generator_kernel.py`, RTX 4050): the persistent-megakernel
skeleton PASSES — 20 blocks on 20 SMs (≤1/SM ⇒ all co-resident, no deadlock), controller↔worker
bidirectional handshake (controller PUBLISHES K, workers OBSERVE; workers PUBLISH telemetry,
controller OBSERVES) via pure `volatile`+`__threadfence()`+one `atomicAdd`, NO grid.sync / NO
cooperative groups; all 19 workers logged an IDENTICAL K trajectory (coherent async cross-block
visibility) that transports an injected telemetry schedule (shallow→deep→shallow) with the
1-tick observe→act lag. Every spin loop has a hard maxspin cap (a logic bug exits + sets err,
never hangs the GPU). step_fn = identity here.
**INCREMENT (2) DONE** (same file, `step_mode=1`): the controller brain — the exact-rational
relaxation — runs ON-DEVICE and its K-trajectory is BIT-IDENTICAL to the oracle
(`jea_nedge_model`). Device K [64,64,64,64,128,256,256,256,128,64,64,64] climbs 64→128→256 on
a deep burst, relaxes back — == oracle, no float, no tolerance. KEY TRICK: the plant-model
totals share a common denominator (25600), so the bridge compare total(A)<total(B) reduces to
an EXACT int64 numerator compare (`numK = passes·(421376 + max(548·K, 66304))`) — exact ℚ via
common denominator, no division. Still one primitive (only step_mode changed); still async,
persistent, maxspin-capped. (Gotcha: CUDA source must be ASCII — em-dash/ℚ/·/× in NVRTC
comments fail; Python strings keep unicode.) **INCREMENT (3) DONE** (`scripts/jea_generator_fold.py`): the FULL evaluator loop on-device.
Workers fold real ℚ nodes in K-windows (Euclid gcd reduction), EMIT converged (N/g,D/g) +
CARRY the unconverged (a,b) residue RESIDENT across windows, PUBLISH measured depth as
telemetry; the controller grows K off it. Closed loop demonstrated: K seeded=4 below the deep
node, controller DISCOVERS it from telemetry and climbs K 4→8→16→32, converging the (F20,F19)
Fibonacci node (18 Euclid steps) in 3 windows vs 5 at fixed K=4. Reductions BIT-EXACT vs Python
gcd, all converged, err=0. (u64 carrier here to focus the windowed-refill MECHANISM; proven
128-bit _QDECL drops in unchanged.) THE LADDER (1)(2)(3) IS COMPLETE — persistent megakernel,
on-device exact-ℚ controller, real fold, all one primitive (step_fn varies).

TWO CORRECTIONS from an external review (both adopted): (a) the protocol is NOT "async" — it is
a per-tick BARRIER (global rendezvous: controller waits all acks, workers wait the tick); what's
proven is inter-block barrier sync WITHOUT cooperative-launch/grid.sync, NOT fully-async
progress (relaxing the per-tick rendezvous = a later increment). (b) RESIDENCY IS A SEMANTIC
REQUIREMENT, measured not assumed: the cyclic comm graph (controller waits workers ∥ workers
wait controller) deadlocks if any participant is descheduled, so `resident_blocks >=
launched_blocks` is now a LOGGED, ASSERTED invariant computed from the COMPILED kernel's
register footprint (jea_generator_fold.residency: 47 regs ⇒ 43 blk/SM ⇒ 860 ≥ 20 launched).
The review's framing: the SCHEDULER ITSELF is now part of the mathematical object (warm-started
relaxation K_{n+1}=F(K_n,telemetry) is a dynamical system, not an argmin; the oracle check is a
trajectory BISIMULATION, not same-final-answer). NEXT COLLAPSE (review point 7): eliminate the
`if(blk==0)` controller/worker branch — make ROLE data (`role=observe_role(); generator_step(
role, store)`), so the kernel contains only generators and the scheduler graph itself is data.
**INCREMENT (4) DONE** (`scripts/jea_generator_async.py`): RING-BUFFER ASYNC removes the
per-tick barrier (user: "ring buffers are what you're looking for"). Per-worker SPSC rings (one
lead thread/block ⇒ single producer+consumer ⇒ NO lock-free hazards, plain head/tail); cross-
block channels are latest-value (K, telem) + one atomic `pending` (benign races — K/telem are
hints, exactness is K-independent). NO tick/ack/grid.sync. THE RING CARRIES RESIDUE: a node not
converging in a K-window is RE-PUSHED to the ring tail = the suspended generator re-enqueued =
carry-residue / pack-into-freed-slots; ring-full = escalate (flag). Generators + bounded FIFO
channels = a KAHN PROCESS NETWORK (observe=pop, publish=push); the old "store" was a capacity-1
ring + a barrier standing in for flow control. Bit-exact vs Python gcd, all converge, residency
asserted. HONEST FINDING (caught the over-claim reflex again): I predicted the free-running
controller would take MANY relax steps per worker window; measured 9 vs ~6 per-worker windows —
decoupled but NOT faster, because its iteration is heavy (rescans all 19 telem slots + a fence,
O(workers)). FIX = a TELEMETRY RING the controller drains incrementally (O(1) amortized) — rings
on the telemetry channel too; THEN it can free-run ahead.
**INCREMENT (5) DONE** (`scripts/jea_generator_coop.py`): BRANCHLESS LOCK-FREE cooperative
generators — the ontological collapse completed. Role-as-data taken to its end: NOT a static
`roles[]` table, NOT a floated controller-token — role DISSOLVED. 20 symmetric blocks, ONE
generator body, no distinguished node. Every generator does BOTH work AND control EVERY cycle,
unconditionally (user: "to maintain branchless, every worker should just do the thing; all async
and monotonic anyway"). No work/control branch, no token/lock (user: "shouldn't be a problem if
idempotent"). WORK = one gcd K-window on a round-robin node slot; the step `if(bb!=0)` is inherent
predication so a converged node is a NO-OP (no skip-branch, no ring). CONTROL = `atomicMax(obsmax,
depth)` (idempotent+commutative) then `relax_q` off it (convergent: fixed point per obsmax, benign
concurrent K-hint writes — K is a hint, exactness K-independent). Bookkeeping branchless via
monotonicity: `atomicSub(pending, nowdone-wasdone)` decrements exactly on the 0→1 transition;
`outN=Na/(aa?aa:1)` unconditional emit (overwritten with Na/g once aa is the gcd). THE INSIGHT
(both user corrections are one): monotonic/idempotent ops compose WITHOUT coordination ⇒ drop the
branch AND the lock together. Verified: 40 regs ⇒ 48/SM residency, bit-exact, all converge,
obsmax=18 (deep Fibonacci discovered), K 4→32 via distributed monotonic control, err=0.
FULL LADDER (1)-(5): persistent → exact-ℚ controller → real fold → ring-async → branchless
lock-free cooperative. **INCREMENT (6) DONE** (`scripts/jea_generator_dag.py`): the STREAMING RECURSIVE FOLD = the
mini-MAlonzo brick, and the apex that UNIFIED the three open "options" (user: "find the common
structure recursively"). The three were not alternatives but the three COORDINATES of a generator
network: 128-bit = the CARRIER (payload), telemetry-ring = a CHANNEL (movement), recursive-fold =
the WIRING (deps) — all three enrichments of the SAME monotonic residue store + one branchless
cooperative generator from (5). Building the recursive fold forced the unification: WIRING became
data in the store (child indices + a monotonic readiness gate `active = ready[L] & ready[R] &
!ready[self]`), which makes the CARRIER a typedef (128-bit _QDECL drops in for scale, where add's
denominator-product overflows u64 = the escalate point) and makes the CHANNEL just BE the store
(the ring became OPTIONAL — NOT needed). KEY: the recursive fold did NOT need the MPMC ring /
work-stealing I'd flagged as its hard part — the monotonic readiness gate handles dynamic
dependency branchlessly + lock-free, SAME as (5)'s cooperation, because monotonic/idempotent
composition needs no coordination. An arbitrary term-algebra DAG (+/x over ℚ leaves) is evaluated
bottom-up by the identical cooperative generators (combine inits its gcd residue on first active
touch, carries it across windows, emits reduced value + flips ready 0->1 which activates its
parent). VERIFIED: 24/24 bit-exact vs Python Fraction across L in {8,16,32,64} x 6 seeds, all
converge, err=0, 40 regs residency. FULL LADDER (1)-(6) COMPLETE: persistent -> exact-ℚ controller
-> real fold -> ring-async -> branchless lock-free cooperative -> streaming DAG (mini-MAlonzo).
**INCREMENT (2) DONE** (`scripts/jea_generator_dag128.py`): 128-bit CARRIER for the streaming DAG
fold — the carrier swap (each ℚ component = u128 as a lo/hi u64 lane pair, nvrtc --device-int128);
SAME generator body / readiness gate / cooperative control, "carrier is a typedef" confirmed.
Escalate-don't-truncate (charter #4): combine products overflow-checked (div/carry tests), sticky
`escalate` flag. VERIFIED: (a) small fold == u64 regime; (b) all-mul of 4 big primes → root
16001216028344223056274833 (84 bits, >2^64 so u64 WOULD WRAP) bit-exact vs Python, escalate=0;
(c) all-mul of 8 primes >2^128 → escalate=1 (DETECTED, not wrapped).
**INCREMENT (3) DONE** (`scripts/jea_generator_telemring.py`) — but FIRST a framing correction:
"telemetry-ring = O(1)-observe optimization" was MOOT (the dedicated-controller scan it would fix
was already removed in (5) by distributed atomicMax(obsmax) = O(1) observe). The ring's GENUINE
value: obsmax is MONOTONIC (only climbs) so K can't relax DOWN; a windowed RING (recent-W samples,
oldest overwritten) gives recent-max so K tracks a TIME-VARYING workload BOTH ways (for the
persistent evaluator, not a one-shot fold). DEMONSTRATED on-device: shifting depth schedule
shallow->DEEP->shallow; ring K = 4->256->64 (climbs AND relaxes), monotonic baseline K = 4->256->256
(stuck high, cannot track down). [Discipline: did NOT build a ring just to check a box for speed it
already had — only the genuine windowing contribution; [[feedback_choice_rigidification_in_substrate]].]
ONLY REMAINING (the spit-take): wire the term-algebra trace from the AGDA side — emit SPPF/foldUPTerm
output as this DAG format (vN/vD/lch/rch/op) via a serializer (no new kernel). Then a term algebra
defined in Agda is evaluated on the GPU by these cooperative generators, exact = the primary goal.

**STRUCTURAL STRICTIFICATION DONE** (`scripts/jea_core.py`, user-requested + a retrospective G9):
through (1)-(6) "one generator primitive, different step_fn" was NARRATIVE — each script
copy-pasted the control law / residency / compile boilerplate. jea_core.py makes it STRICT: the
shared structure lives once (CTRL_CUDA = numK/relax_q control law; Q128_CUDA = u128 lane helpers;
build_kernel = compile through an ASCII GATE; residency = the liveness invariant; relax_q_ref =
the Python bisimulation oracle). All 7 jea_generator_*.py now `import jea_core` and differ ONLY in
their step_fn kernel body — the claim is compiled, not asserted; all stay bit-exact green.
**ASCII GATE** (`jea_core.build_kernel`): the G9 escalation of the em-dash/ℚ/->/=> NVRTC failure
that recurred 4x — refuses non-ASCII device source BEFORE compile with a precise line/col/codepoint
pointer (validated: fires on U+2014). Correct-by-construction (every kernel goes through it).
RETROSPECTIVE (this arc): SUSTAIN = every increment verified bit-exact vs Python before claiming
PASS (held throughout, caught all 3 over-claims). Recurring class findings = over-claim-before-
measure (countermeasure: the ablation instrument [[feedback_test_the_wall_before_declaring_it]])
and git-lapse (0 commits all session, on main — pending the branch/grouping decision).
SCRIPT INVENTORY (scripts/, all green): jea_core (shared), jea_roofline (ablation roofline),
jea_nedge_model (controller oracle), jea_generator_{kernel,fold,async,coop,dag,dag128,telemring}
(the (1)-(6)+128bit+telemring ladder). jea_gpu (M1-M2b, committed). Removed _ncu_q_probe (throwaway).

**PRIMARY CHARTER GOAL CLOSED — the Agda-on-GPU path is end-to-end** (`jea/agda-emit/Emit.agda` +
`scripts/jea_agda_bridge.py`, committed 8046b4c). A ℚ term algebra (lf/add/mul = the SPPF free
term gen/⊕/⊗) is DEFINED IN AGDA; the TYPECHECKER is the bridge (substrate --safe, NO MAlonzo,
NO IO/GHC plumbing): `render term ≡ termStr` and `evalStr term ≡ valStr` proved by refl, so the
serialization + value are machine-vouched faithful. The bridge typechecks Emit.agda (the refls =
the guarantee), reads termStr/valStr, parses the S-expr into the GPU DAG (leaves first, combines
post-order), evaluates it on the cooperative generators (jea_generator_dag.run_g), and asserts
the EXACT reduced GPU root == Agda's value. (2/3+1/2)*(1/4*3/5) → 7/40 on Agda AND on 20 GPU
generators; generality confirmed on a second term → 7/3. THE SPIT-TAKE: a term over the ℚ algebra
written in Agda, folded on 20 cooperative GPU generators, exact rational back, Agda agrees.
GIT: this segment's work committed on main in 4 commits (5538097 diagnostics, 85fef7a jea_core,
6dca4b1 ladder, 8046b4c the Agda bridge); tree clean, all pre-commit gates green.
NEXT (beyond the closed goal): wire the REAL substrate SPPF/ℚ (not the self-contained Emit Term)
through the same bridge; emit DAGs with sharing (intern); scale via the 128-bit run_g path.

**THE MERGE DONE — dynamic AND data-parallel in ONE kernel** (`scripts/jea_generator_unified.py`,
committed c55ac21; user: "the point is the unified architecture, not silo demos"). The cooperative
dynamic architecture (live K control, readiness-gated arbitrary DAG, branchless, lock-free) now
runs DATA-PARALLEL across the full thread grid, on the exact 128-bit carrier with escalate. Change
from jea_generator_dag: drop `if(threadIdx!=0)return`; partition combines across ALL gridDim*blockDim
threads by global tid (round-robin, computed — no own[] array); same predicated readiness-gated
gcd-window step; control monotonic (atomicMax obsmax by active threads, K relaxed once/block).
PERF: ~366 M nodes/s (all-+ 2^18 tree, 5120 threads) vs the 20-lead-thread silo's ~0.66 M = ~555x;
random +/× exact to 2^128 (root 81b exact where u64 WRAPS), >2^128 intermediate ESCALATES (flag,
not wrapped). THE RESIDENCY CLIFF (review pt 8, learned hard): the persistent CYCLIC comm graph
needs ALL launched blocks co-resident or resident blocks spin forever on combines owned by
never-scheduled ones. The ANALYTIC residency (jea_core.residency ⇒ 6/SM) OVERESTIMATES — empirically
DEADLOCKS past ~3/SM: fast to 32 working blocks (0.1ms), HANGS at 64. cupy lacks the CUDA occupancy
API, so launch 1 block/SM (the hardware-guaranteed resident floor) + round-robin all combines —
correct at any N. [Open perf: 1/SM = ~16% occupancy; measured-residency (a concurrency probe) could
push to the true 2-3/SM for more throughput; heavy-gcd workloads run lower than the all-+ 366M.]
SESSION GIT (main, all gates green): 5538097 diagnostics, 85fef7a jea_core, 6dca4b1 ladder,
8046b4c Agda bridge, c55ac21 the unified merge.

**THE DEADLOCK WAS A FLOW-CONTROL FAILURE, fixed by STRATIFYING** (user: "no valid reason for a
deadlock... did we forget to stratify?"). The persistent kernel made threads WAIT on specific nodes
owned by maybe-unscheduled blocks (cyclic wait). Fix (`scripts/jea_generator_strat.py`): process
TOPOLOGICAL STRATA — within a stratum all children are done, so NO cross-block waits, deadlock
impossible, any occupancy (full grid, blocks EXIT), dynamic K re-LAUNCHES across strata. ~847 M
nodes/s, 2^20 all-+ tree, full occupancy, 128-bit exact. REFINED (`scripts/jea_generator_bucket.py`,
committed b9200b1): BUCKETIZE strata->substrata by COMPACTING survivors (K tracks each bucket's
depth, not the deepest node; 3.9x less work, ~36x less time on heterogeneous depth) + ESCALATION
PRIORITY (overflowed node = cracked-open + blocking its parent -> priority bucket for the wider
carrier, before fresh work). Principle: PRIORITIZE BY PROGRESS STATE (escalated > in-progress > fresh).

**THE FRONTIER = ACKERMANN** (user: "the real win is when our universal term-algebra engine handles
Ackermann"). Everything built so far is a STATIC-DAG evaluator (tree known before eval => stratifiable)
= the PRIMITIVE-RECURSIVE case. Ackermann breaks that: call structure is DATA-DEPENDENT + UNBOUNDED
(A(m,n-1)'s VALUE becomes an arg), so the DAG cannot be pre-built/pre-stratified. It forces three
UNBUILT capabilities, which are the convergence of every open thread: (1) DYNAMIC WORK PRODUCTION —
a reduction SPAWNS new sub-terms at runtime; the work queue GROWS during eval (the dynamic-spawning
ring/dataflow the cooperative path circled and the static stratified fix abandoned — bring it back
WITH the flow-control/priority/bucket lessons). (2) TERM REWRITING — pattern-match reduction rules on
constructors (A(0,n)->n+1, ...), not a fixed +/x fold (the actual "universal" part). (3) TRUE
MULTI-LIMB — A(4,2) ~19729 digits => escalate-don't-truncate must DELIVER arbitrary precision, not
just flag. Ackermann = a GPU evaluating a non-primitive-recursive function, exact = the universality
spit-take. STATUS: have the scheduler + carrier + exactness discipline; NOT term-rewriting or dynamic
spawning yet — that is the real new build.

**THE UNIFICATION — escalation IS dynamic work production** (user: "so does escalation... it doesn't
have to be as terrifying as you're thinking"; PROVEN in `scripts/jea_ackermann_spec.py`, committed
c18ddeb). There is NO static-fold-vs-dynamic-rewrite split. ONE loop: pop a node, reduce, it yields a
VALUE or SPAWNS sub-work the parent depends on. The three "spawn" cases are one act (push-to-queue):
recursion (A(m,n) needs A(m,n-1) then A(m-1,that)), escalation (value over width W → spawn width 2W),
ordinary combine (fits → terminal). We ALREADY built every piece: spawn = the escalation priority
push; dependency = the readiness gate; priority = the bucket scheduler. The spec is GPU-shaped
(explicit node array + work queue, NO host recursion — the call stack lives in spawned nodes;
continuation A(m,n)→A(m-1,A(m,n-1)) = tail-rewrite: spawn inner, on resolve rewrite node to A(m-1,v)),
verified exact through A(3,6) (172k steps, 86k nodes = the non-primitive-recursive explosion).
Ackermann is SEQUENTIAL (max-queue 1): it tests UNIVERSALITY not parallelism (parallelism = the 847M
nodes/s scheduler; the universal engine = spawn loop ⊕ parallel scheduler, both built). NEXT (the real
new build, now de-risked): GPU port = this spawn loop on the existing scheduler — dynamic node alloc
(atomic bump) = spawn; value-explosion = escalation/multi-limb spawn (the same push). Multi-limb is
just the escalation rule actually delivering arbitrary precision (A(4,2)=2^65536−3 is where it fires).

**ACKERMANN ON GPU DONE** (`scripts/jea_ackermann_gpu.py`, committed 0f94881): a non-primitive-
recursive function evaluated on silicon, EXACT, batch-parallel. The spawn structure collapses to the
classic ITERATIVE STACK (per-thread stack of m-values + running n) — the stack IS the suspended
continuation (push=spawn, pop=resolve), NO host recursion. 200k independent evals, all == host ref.
Universality on silicon = the spit-take. HONEST perf: 0.1M evals/s (misleading — cases vary ~10^6x
in work; A(3,7)~700k steps vs A(0,5)=1); real costs = warp divergence (mixed cases/warp) + global-mem
stack; ~10^10 spawn-steps/s. Optimizable (shared-mem stack, sort by case); throughput is NOT
Ackermann's point (universality is; throughput is the 847M-nodes/s scheduler).
**MEASURED FINDING — suspended-generators NOT exercised by Ackermann** (corrects the hypothesis "this
is where they pay off"): tractable Ackermann keeps n within u64 (n grows +1/step ⇒ 2^64 needs 2^64
steps = unreachable; value & step-count bounded TOGETHER), so multi-limb never fires. The suspended-
generator / constructive-CF-unfold-on-demand carrier (vs GMP eager limbs) pays off on a DISTINCT axis:
TRACTABLE-step / HUGE-value workloads (factorial, powers, big products) — carry the value's
CONSTRUCTION (compact), unfold digits on demand; that is the genuine next brick.

**CARRIER = BYTE-LIMB (8-bit), not u64** (user: "why operate as coarse as u64 when we could operate
at 8-bit?"; `scripts/jea_limb_spec.py`, committed 89932bb). u64 was a FROZEN GAUGE (a convenient
native word = [[feedback_choice_rigidification_in_substrate]]). The principled carrier for unfold-on-
demand is the BYTE: a value IS its little-endian byte stream, length = significant bytes, unfolded
one limb at a time, escalation = append a byte (fine grain, not 64->128). Proven: (1) pay-for-what-
you-use (small value = 1 limb not 8; charter #5 hoard-bandwidth); (2) unfold-on-demand (low k bytes
of a product of two astronomical numbers = O(k^2), touch only low k limbs, independent of operand
size; GMP ropes the whole thing, we unfold only digits asked for). CORRECTION to my stale intuition
(user): 8-bit is NOT emulated/slow — it PACKS MORE PER REGISTER (4 int8/32-bit word) and is the GPU's
FASTEST int path. VERIFIED on sm_89: `__dp4a` = 4 int8 MAC/instruction, exact. A byte-limb bignum
multiply is a byte CONVOLUTION => maps onto __dp4a / int8 tensor cores. 8-bit wins ALL THREE axes
(bandwidth, unfold granularity, compute/packing); the principled carrier (byte-stream suspended
generator) = the hardware-optimal carrier (int8 SIMD convolution). The limb width is a gauge the
controller could tune; 8-bit is the floor/default. NEXT BRICK redefined: the big-value carrier is a
byte-limb suspended-generator, multiplied via dp4a/int8-tensor convolution, unfolded on demand.

**BYTE-LIMB BIG-VALUE CARRIER ON GPU DONE** (`scripts/jea_limb_gpu.py`, committed fe69034): a value
is a little-endian uint8 limb stream; a*b = the CONVOLUTION of the limb streams, mapped onto __dp4a
(pack a[i..i+3] forward + b[k-i..k-i-3] reversed -> one __dp4a = 4 uint8 MACs of convolution terms),
columns parallel, carry one O(L) pass. VERIFIED exact vs Python: 7^4000 x 11^4000 (1404x1730 ->
3134 limbs) in 0.082 ms; repeated squaring 3^(2^k) on GPU exact through 3^8192 (8192 limbs). 30
GMAC/s on the int8 datapath. The escalation-spawn's wider carrier, realized. HONEST limits: carry is
SERIAL (1 thread, O(L)) -- parallel-prefix carry is the scale-up; 30 GMAC/s is far below dp4a peak
(small/unsaturated/carry-serial) -- correctness + int8-path were the goal, not peak tuning.
CARRIER NOW COMPLETE-ENOUGH (committed 376ede8): PARALLEL carry (vectorized scatter+ripple, every
step a GPU kernel; ~2 rounds for a 3134-limb product, replaced the serial 1-thread O(L) pass —
worst-case all-0xff is O(L) rounds, carry-lookahead scan is the asymptotic fix), byte-limb ADD, and
ESCALATION DELIVERS: a u128-overflowing combine (10^20*10^20=10^40) recomputes on the byte-limb
carrier exact — escalation appends limbs and produces arbitrary precision, NOT just a flag. Verified
exact vs Python (multiply, add, repeated squaring 3^(2^k) through 3^8192).
OPEN: division (for ℚ reduce); auto-route escalation INSIDE the spawn-loop kernel on-device (the
demo shows delivery at host-orchestration level — the carrier IS ready to be the on-device target).
Then the universal engine = spawn loop ⊕ parallel scheduler ⊕ byte-limb unfold-on-demand carrier,
all on-GPU, exact.

**BASE-PARAMETRIC CARRIER — the WIDTH LADDER 8→4→2→1 + GF(2)** (`scripts/jea_carrier_base.py`,
committed b9bda79; study `jea/agda-emit/4bit-WAL.md` rev2). User: 4/2/1-bit are MANDATORY regardless of
perf; the question was the LEAST-COST descent. Answer realized: the dp4a convolution KERNEL IS
UNCHANGED (multiplies byte-valued limbs, base-agnostic); only the host carry takes base B=2^w + a
carry/carryless mode. Descending = changing one parameter w. VERIFIED exact: integer multiply at
w∈{8,4,2,1} all reconstruct to a*b (same value, limb streams 392/784/1567/3134); carryless w=1 ==
clmul (GF(2)[x] poly multiply). AT w=1 CARRYLESS the big-value carrier and the F₂ SUBSTRATE ARE THE
SAME OBJECT (multiply=AND, add=XOR, no carry = the int1 XOR-popcount / binary-tensor path = GF(2)
matmul = the substrate home field: commuting-sphere, 3+1 parity, GL(3,F₂)). Width w + carry/carryless
are controller GAUGES (join K); ONE carrier, never per-width forks. PREMORTEM catch (held): did NOT
chase per-width int4/int1 datapath (no nibble ALU MAC, grounded) — that perf axis is DEFERRED, off
the descent's critical path. The user has a reason aimed past 1-bit; architecture lands at GF(2)
cleanly. (4-bit WAL plan P1'/P2'/P3' done; per-width-datapath = the deferred P4-perf axis.)

**SWAR ADD LADDER — N carriers per register** (`scripts/jea_swar.py`, committed ef51cc0). User
directed: exploit carrier<ALU to process MULTIPLE carriers concurrently per register, walking the
ladder TOP-DOWN (annealing — verify each rung before the next): lane width L=32→16→8→4→2→1, packing
nlanes=32/L = 1,2,4,8,16,32 independent bignums/word. ONE parametric SWAR full-adder handles every
rung (low=(a&notH)+(b&notH)+cin; s=low^(a&H)^(b&H); cout=maj; only the lane MASKS change per L), carry
lane-isolated (no bleed), verified == per-lane reference at EVERY width. At L=1 it degenerates to XOR
sum / AND carry = GF(2) (carryless = keep sum, drop carry) — reached only after the carry-isolation
pain of the wider rungs. Honest state: this is SWAR ADD (where carry-isolation is the challenge);
SWAR MULTIPLY (lane-crossing partial products) is the NEXT pain, separate — the carrier's multiply is
still per-value dp4a, not multi-carrier-packed. cupy-vectorized=GPU; custom kernel mechanical.
WHY (the convergence): smaller carrier ⇒ more carriers/register; the width descent's PURPOSE is to
reach max packing, maximal + carry-free at L=1 GF(2) (32-way bitslice on the boolean/int1 path).
**SWAR MULTIPLY LADDER too** (`scripts/jea_swar_mul.py`, committed 3e66376): N independent products
a_l*b_l per 64-bit register, lane-isolated, walked 32→16→8→4→2→1 (nlanes 1→32), verified exact
(4096 words/rung). Multiply's pain ≠ add's carry-isolation — it's the 2L-bit product SPILLING lanes;
fixed by SPACING each lane to W=2L (partial products stay in-lane, monotone <2^W ⇒ PLAIN-add
accumulation, no cross-lane carry) + per-lane bit-broadcast (log W in-lane shift-ORs) + bit-serial
shift-add. At L=1: R = a AND b = GF(2) scalar multiply (carryless, no spill). BOTH ladders (add: XOR,
mul: AND) bottom out at GF(2) = the substrate home field, max packing, carry-free. Lane-wise scalar
ops; bignum SWAR convolution = chaining per lane (next composition). At the GF(2) floor for both ops;
the user has a reason aimed past 1-bit (the destination).
**SWAR BIGNUM MULTIPLY DONE — carrier is SWAR end-to-end** (`scripts/jea_swar_bignum.py`, committed
0811851; "do the build before the discovery, context flush soon"). N independent BIGNUMS multiplied
concurrently per register, lane-isolated: each lane runs its own schoolbook convolution (lane-wise
bit-serial mul-accumulate, plain add since W has room) + base-2^L carry-propagate (carry stays
in-lane; tail carry fully propagated). VERIFIED exact: integer (L=4 K=4→4 bignums/reg; L=8 K=3→2/reg)
and carryless L=1 = N independent GF(2) clmuls (L=1 K=8,12 → 16 clmuls/reg). BUG caught by per-lane
DUMP not guessing: the doubling broadcast (low bit→full lane via shift-OR 1,2,4,8,16) OVERSHOOTS when
lane width W is NOT a power of 2 (W=24 pushed lane0 bits into lane1) → FIX: W must be pow2 (asserted),
W = pow2 ≥ 2L+ceil(log2 K). SWAR FILES: jea_swar.py (add ladder), jea_swar_mul.py (lane-wise mul
ladder), jea_swar_bignum.py (bignum convolution). The carrier is now SWAR end-to-end (add+multiply),
N carriers in flight, both ops bottoming at GF(2) (add=XOR, mul=AND). cupy-vectorized=GPU; custom
RawKernel mechanical. STATE: standing on GF(2) with multi-carrier add+multiply, max packing, carry-free.
NEXT (post-flush): the user's REASON / destination past 1-bit (chasing the discovery now that the
build is banked); on-device RawKernel for the SWAR carrier; wire SWAR carrier as the escalation
target / into the spawn loop. ALL session work committed on main ( end fe69034→...→0811851), gates green.
**MIXED-WIDTH SWAR** (`scripts/jea_swar_mixed.py`, committed d892ceb): carriers of DIFFERENT
precisions in ONE register — 32+16+8+8=64-bit layout — added concurrently, lane-isolated at the
UNEVEN boundaries. The SWAR full-adder is MASK-DRIVEN ⇒ layout-agnostic: H=top-bit-of-each-lane,
notH=~H; carry can't cross (each lane's low-(w-1) sum <2^w stays in its range). Verified each lane's
sum mod 2^w AND carry-out exact (100k words), no bleed. masks(layout=[(off,wid),...]) builds H/LANE_LO/
VAL for any partition. Pay-for-what-you-use at the LANE level (each carrier at exactly its needed
width) — the controller-as-gauge idea at register granularity. NEXT pain: mixed-width MULTIPLY
(per-lane 2L room + per-lane broadcast/shift, and the broadcast needs power-of-2 lane width — see the
jea_swar_bignum overshoot bug) and bignum carry-CHAINING across mixed lanes (per-lane shift of
carry-out to the next word's lane-low). User is building toward mixed precision packing; destination
past 1-bit still pending. **SWAR-ADD CONCLUDED** (committed f862579): the maximal mixed tiling
32+16+8+4+2+1+1=64 (one lane of EVERY power-of-2 width, incl. two 1-bit GF(2) lanes) all add
concurrently in one register, each lane's sum+carry-out exact, no bleed — same mask-driven adder,
`demo(layout)` works for any tiling. The whole width ladder simultaneously, GF(2) lanes = XOR/AND.

**MIXED-WIDTH SWAR MULTIPLY** (`scripts/jea_swar_mixed_mul.py`, committed 0913bca): operand widths
16/8/4/2/1/1 (=32) in product rooms 2L = 32/16/8/4/2/2 (=64) tiling a 64-bit register — SAME operand
ladder as the add-conclusion but top lane is 16 not 32 (each product room is 2L; product-doubling
halves the top). Each lane's product == a*b exact; two 1-bit lanes = GF(2) AND. KEY ASYMMETRY (user:
"our equivalence of warp divergence"): mixed ADD is ONE mask-driven pass (carry stays in-lane); mixed
MUL needs ONE PASS PER DISTINCT WIDTH — the global shifts (a<<k + bit-broadcast) overshoot a narrow
lane into its wider neighbor, so each width-group is masked off & run uniformly. That per-distinct-
width pass count IS branch/warp divergence re-expressed at register level (homogeneous tiling = 1 pass
= convergent warp; k distinct widths = k passes = k-way divergent). A few SM cycles → usually hidden
by occupancy/latency, exposed when not → a VALID PARETO KNOB: packing density (mix widths tightly) vs
divergence cost (#passes = #distinct widths), same tradeoff as lane-utilization vs divergence in a real
warp. mixed_swar_mul(a,b,layout) groups by (L,W) for the passes.

**MIXED-WIDTH SWAR BIGNUM — per-lane carry-chaining** (`scripts/jea_swar_mixed_bignum.py`, committed
3683548): composition of mixed multiply + bignum carry. Lanes of different precision, each a K-limb
bignum, multiplied in one register, carry-chained PER LANE. The new pain is the carry SHIFT: uniform
bignum carries with one global >>L (all lanes share L); mixed lanes must each shift their high part
down by THEIR OWN L, so a single global shift over/under-shifts. Fix = SAME move as mixed mul: group by
(L,W), shift per group, OR disjoint: carry = OR_g ((c & GRP_HI_g) >> L_g). In-lane because & GRP_HI_g
zeroes non-group bits and >>L_g (<W_g) keeps group g's high bits inside each lane; groups disjoint ⇒
OR clean. Single col[k]+carry add is lane-safe IFF W ≥ 2L+1+ceil(log2 K) (ASSERTED, the overshoot
lesson; note the +1 carry-headroom term beyond jea_swar_bignum's 2L+ceil(log2 K)). Verified each lane's
K-limb product == a*b across 20k words at 3 distinct widths (L4/W16, L2/W8, L1/W8); L=1 group = BINARY
INTEGER with carry (distinct corner from GF(2) carryless clmul). BOTH convolution AND carry-propagate
cost #distinct-widths divergent passes — same Pareto knob. Carrier is SWAR end-to-end at MIXED
precision now. The SWAR carrier arc (add/mul/bignum × uniform/mixed) is COMPLETE; floor = GF(2).

**SWAR ↔ EL-ATLAS WIRED** (pilot `el-atlas/tools/swar-boundary-nedge-pilot.py`
committed 7f9e01b; claim SWB registered in `tools/el-atlas-depsort-v3.py` committed 3b65e06). The
SWAR carrier IS the el-atlas (E+,E-) pair, NOT a quotient: E+ = Σ payload L_i (parallel G_OR fold),
E- = Σ forced expansion (W_i-L_i), mass = ΣW_i = 64 (REGISTER CONSERVED), bias = E+−E-, D =
#distinct-(L,W) = divergent passes (series resistance, G_thru = E+/D). FALLS OUT: operation → crossbar
region by room rule — add (W=L) bias +64 = T(payload); MUL (W=2L) bias 0 = B (the bridge NULL, half the
register is product headroom — multiply SITS AT the el-atlas null); bignum (W>2L) bias <0 = F(headroom).
Validity = SERIES G_AND gate (a leaky lane boundary, e.g. mul room<2L, shorts to 0). The ranked G=E+/D
column IS the live symmetry-breaker weigher the kernel-perf control loop wanted (every add width ties
at 64 = width is a FREE GAUGE; mul 32; bignum descends). Pilot = 6 witnesses PASS. Claim SWB: deps
(pins,two_ops), NO new knob (column not row → existing space-hashes/separation ledgers intact), coeff-
INDEPENDENT (no _COMPLEX_STANCE). VERIFIED: harness EXIT 0, load-bearing assertions hold, ALL 27 prior
claims ZERO verdict-diff across full 663552-config space (no contamination), SWB = P on 221184 (exactly
1/3, the pins≥2 & two_ops regime), V on 442368, F nowhere (structural theorem). How to model a domain in
nedge: supply the (E+,E-) accumulators + two ops (series/parallel) + boundary terminals + range ℛ;
calculus computes LFP equilibrium + mass/bias + confidence. Pilot skeleton = docstring(claim+numbered
witnesses) → ok_X &= check over sample → print "NAME: prop {bool}".

**WHAT IS IN THE LANES = ℚ; ℚ↔TRACE TIED** (`scripts/jea_swar_q.py`, committed ac3fc15). A lane
carries ℚ = (num,den), and that pair IS the el-atlas nedge (E+,E-) carrier via the LIFT THEOREM:
G_OR = fraction-add, G_NOT = swap = reciprocal, G_AND = swap-conjugated-add = series conductance. So
the SWB pilot's E+/E- WAS num/den. A register packs N rationals as adjacent (num,den) lane-pairs;
ℚ-multiply = num·num,den·den = ONE lane-wise bignum pass (N//2 ℚ-products/reg). THE CLOSURE: el-atlas
crossbar on a ℚ-lane is mass=num+den, bias=num−den; reduce(gcd) LOWERS MASS at FIXED VALUE, and the
stripped cofactor g IS the residue the TRACE retains. "Quotient erases the mass the pair keeps"
(el-atlas) ≡ "never discard residue" (substrate) — SAME FACT; reduce = split-idempotent RETRACTION,
lossless because the trace keeps g. Trace = the suspended EEA/CF generator the (num,den) lane WINDOWS;
lane width = how much of the trace is unfolded. Unifies jea-SWAR ↔ el-atlas-nedge ↔ ℚ/EEATrace /
[[feedback_never_discard_residue]] / [[project_split_idempotent_apex]]. 3 witnesses PASS (cupy
ℚ-mul == unreduced (n1n2,d1d2); lift on the pair; reduce mass-drop+retract). N·W≤64 caps reg packing.
OPEN FORK (next): lane = VALUE-window (num,den) [built] vs TRACE-window (CF quotients/EEA shape, recover
(num,den) by the fold) — the deeper "ℝ as process" rep where the lane holds trace digits, not value
limbs. Trace-window = pay-per-unfold, exact-by-shape (SPPF≅EEA canonical key), the suspended-generator
made the carrier. That's the natural next build toward the substrate-ℝ-on-GPU goal.

**TRACE-WINDOW CARRIER BUILT** (`scripts/jea_trace_window.py`, committed 5b491b4). The dual carrier:
lane holds the CF = EEA quotient sequence; (num,den) by the convergent fold. to_cf (value→trace,
Euclid) / from_cf (trace→value, convergents). 5 witnesses PASS: (1) from_cf∘to_cf == reduce, idempotent
(split-idempotent); (2) CANONICAL BY CONSTRUCTION — to_cf(kp,kq)==to_cf(p,q) scale-free ⟹ equal value
⟺ equal CF, NO reduce step (the CF IS the canonical key); (3) pay-per-unfold — convergents alternate-
bracket, error shrinks, last==value; (4) compare-by-prefix — CF lex (sign-alternating) == true order, no
cross-multiply; (5) THE NEW PARETO as an el-atlas Wheatstone bridge — value(arith 1/canon 8) vs
trace(arith 8 Gosper/canon 1 prefix) cross at f*=0.5 (arith fraction) = the bridge NULL, bias flips,
arith-heavy→value, compare-heavy→trace. THE PARETO: value-window = dense arithmetic throughput,
expensive canonical/compare (carries mass); trace-window = free canonical+compare, expensive arithmetic
(Gosper Möbius state machine, NOT a limb op, not SWAR-friendly). Round-trip between reps = reduce. NOTE
for wiring: this Pareto could become an el-atlas claim on existing knobs, but a 'rep' KNOB would be a ROW
(changes SPACE/space-hashes, invalidates frozen separation ledgers) — unlike SWB which was a column; do
NOT casually add a knob. OPEN: SWAR-pack the trace-window's CHEAP path (fixed-k CF prefix per lane →
parallel lex compare + parallel convergent fold; the canonical/compare side IS SWAR-able, only Gosper
arithmetic isn't) — would show the trace-window's throughput arm concretely.

**GPU TOPOLOGY MODELED IN EL-ATLAS** (`el-atlas/tools/gpu-topology-nedge-pilot.py`,
committed 55258b1). The NVIDIA hardware hierarchy IS a series-parallel nedge conductance network:
BANDWIDTH = conductance, LATENCY = resistance = 1/G (G_NOT swap), SERIES links = G_AND (harmonic ⟹
SLOWEST LINK = the bottleneck), PARALLEL resources (SMs, mem channels) = G_OR (sum), ROOFLINE RIDGE =
the Wheatstone bridge NULL between compute & memory branches, OCCUPANCY = series-AND binding constraint
(min over threads/regs/shared/blocks). Numbers QUERIED LIVE (cupy/cudaDeviceProp), RTX 4050 Laptop: 20
SMs, 192 GB/s DRAM (96-bit×8GHz), 24MB L2, 64K regs+100KB shared/SM, ~10.9 TFLOP/s FP32, ridge ≈56.8
FLOP/byte; intermediate L1/L2/PCIe BWs flagged [est] (structure exact for any positive numbers). 5
witnesses PASS: bottleneck=PCIe(16) (path G_AND=14.5, drop it→159); 20 SMs G_OR→10906 GFLOP/s; ridge
bridge-null+bias-flip; G_NOT involution; occupancy reg-bound 67%@64regs / thread-bound 100%@32. COMPOSES
WITH SWB: SWB weighed the ALGORITHM lane geometry, this weighs the HARDWARE; achieved throughput =
G_AND(algorithm conductance, hardware bottleneck) — series composition of the two pilots. This is the
kernel-performance nedge model the SESSION-ORIGIN intent called for ("model the kernel-perf space
properly in nedge, live control loop"). nvidia-smi topo -m is trivial here (1 GPU); the rich topology is
the on-chip hierarchy. LIVE-LOOP HOOK (next): NVML telemetry (clock throttle/util) scales the edge
conductances → nedge LFP re-solves → bottleneck shifts → scheduler rebalances. The static network is
built; the time-varying edges + on-device LFP are the dynamic dispatcher debt below.

**BOTTLENECK SPECTRUM + KERNEL-TYPE KNOB + HET DISPATCH** (el-atlas tools/, committed eccd519 /
5c51e1c / f86f16d). (a) `gpu-bottleneck-spectrum-pilot.py`: the FULL bottleneck ranking = the
continued-fraction/EEA TRACE of the conductance ladder (Cauer ladder impedance IS a CF — same
to_cf/from_cf carrier as jea_trace_window). Topology pilot's single bottleneck = TOP of the trace;
whole sorted ladder w/ Amdahl shares (f_i=(1/G_i)/Σ, speedup-if-removed=1/(1−f_i)) = the ranking.
Host-streaming @I=4: PCIe 90.4% ≫ DRAM 7.5% > L2 1.3% > compute 0.5% > L1 0.3%. Single ridge →
HIERARCHICAL (multi-ceiling) roofline. (b) KERNEL-TYPE KNOB: data residence/access-pattern selects
which rungs are in the loop + moves the ridge: host-stream 681.6 > dram 56.8 > L2 9.5 > L1 2.0 >
compute ∞ FLOP/byte (slower feed ⟹ higher ridge ⟹ cache-resident saturates compute sooner). A
PILOT knob, NOT a depsort SPACE knob (row, invalidates ledgers). (c) HET DISPATCH (CPU+GPU): two
PARALLEL compute branches (G_OR, conductances add), each SERIES-gated by its feed (G_AND):
throughput = G_OR(G_AND(cpu,sysram·I), G_AND(gpu,feed·I)). MAX throughput = split work ∝ each
branch's effective conductance so both finish together = the WHEATSTONE BRIDGE NULL; total = the
parallel sum. Optimum MOVES with kernel-type: host-stream low-I f_gpu=0.20 (CPU gets 80%! CPU 4×
the GPU bc PCIe starves it); device-resident 0.75; compute-bound 0.96. THE KERNEL-PERF NEDGE MODEL
IS NOW COMPLETE: SWB (algorithm lanes) + topology (hw hierarchy) + spectrum (full ranking=CF trace)
+ kernel-type knob + het-dispatch (optimal split=bridge balance) — one G_OR/G_AND/bridge calculus.
Static; the LIVE control loop (NVML edges → LFP re-solve → rebalance) = the dispatcher debt below.

**HOST TOPOLOGY FETCHED AT RUNTIME** (`host_probe.py` + `host-topology-nedge-pilot.py`, committed
934024a). CPU-side mirror of the GPU topology, numbers MEASURED LIVE (sysfs/proc for static facts;
streaming/sgemm/PCIe benchmarks for conductances) — no hardcoded estimates. This box (i7-12650H): 10
cores AVX2, 15.3 GiB, L3 24M, ~150 GFLOP/s sgemm, sysram 1-core ~7.6 → 10-core-saturated ~18-24 GB/s
(MEMORY CONTROLLER caps WELL below 10× → series-over-parallel: cores G_OR but G_AND-capped by the
controller), PCIe ~6 GB/s measured (lower than the 16 guess). Same conductance network as GPU: cache
hierarchy = queried capacity ladder + measured DRAM bottleneck; CPU roofline ridge ~8.7 FLOP/byte;
CAPACITY/BANDWIDTH PARETO (host owns capacity 15GiB / GPU owns bandwidth 192GB/s = the dispatch
rationale). het-dispatch rewired to probe_host() at runtime; counterintuitive result STRONGER with
real numbers (host-streaming low-I: CPU ~3× the GPU bc measured PCIe ~6 starves it harder). MEASUREMENT
HONESTY: dropped the invalid numpy cache-BW sweep (per-call overhead swamps L1/L2 — can't measure cache
BW from Python) and the faked swap-speed proxy; numbers vary ±30% run-to-run (busy machine) but the
STRUCTURAL witnesses (controller-cap, roofline flip, cpu>gpu-when-pcie-bound, argmax=balance) are robust.

**TOPOLOGY BREAKERS AUTO-ENUMERATED AT RUNTIME** (`topology_breakers.py` + `branch-independence-
nedge-pilot.py`, committed d0b6641 / eccd536). The kernel-perf model's symmetry-breakers are a
DISCOVERY ENGINE — nothing hardcoded; runs on ANY machine and rediscovers ITS breakers. Discovery (not
assumption): caches via shared_cpu_list (private vs shared READ, not assumed); heterogeneity via
cpuinfo_max_freq tiers (this box: 3 tiers 4.7×2/4.6×4/3.5×4, finer than manual P/E); NUMA nodes;
powercap budget TREE (package-0 PL0 45W/PL1 115W + psys=chassis aggregate, emitted even with no
exposed limit bc its existence IS the CPU↔dGPU coupling); GPUs via nvidia-smi (dGPU 30/75W enforced +
iGPU). survey(topo,test) auto-flags a measurement's confounds FROM STRUCTURE — catches the 512²-spills-
to-shared-L3 confound before you run it (threshold = discovered largest-private-cache 1280K). KEY
FINDINGS: (a) G_OR (parallel sum) holds iff branches share NO downstream series resource — compute
(private-L2) composes (scaling 0.71, ~linear to P-cores), MEMORY contends (0.30, controller-capped);
the het CPU+GPU sum is the independent kind, n-cores is NOT — corrects the "n-branch for free" claim.
(b) TDP is a NESTED budget tree (power-domain mirror of cache hierarchy): chassis(psys) ⊃ {CPU-package
⊃ P/E/iGPU, dGPU}; CPU↔dGPU couple only at the chassis root, independent within budgets. (c) GPU peak
FLOP overstated — enforced 30W of 75W → derate ~0.40. MEASUREMENT HONESTY: dropped invalid numpy
cache-BW sweep + faked swap proxy; cache BW not Python-measurable (call-overhead). The whole kernel-perf
nedge model (SWB+topology+spectrum+kernel-type+het-dispatch+host+breakers) is now PORTABLE + self-discovering.

**NEDGE ON ITS KIRCHHOFF FOUNDATION + KRON REDUCTION** (`kirchhoff_nedge.py` committed 3299698,
`kron_reduction.py` committed e97083a). User correction (RIGHT, should have been a given): G_OR=sum /
G_AND=harmonic are NOT primitives — they are the parallel/series REDUCTIONS of the Kirchhoff nodal
solve (graph Laplacian, ground sink, inject unit current, G_eff=1/v_src; = stationary point of
dissipated power, KCL = the Noether conserved current). "Sum holds iff no shared downstream series
resource" = the DEFINITION of parallel (same node pair) under KCL, not an empirical discovery. The
shared-resource contention cap = G_AND(k·g, c) is a KCL THEOREM (derived, not measured); Wheatstone:
series-parallel reduction agrees with nodal ONLY when balanced (coupling carries no current = the
bridge null), differs otherwise. THEN (2nd correction, also right): "~all graphs reduce, in the right
order." NODE ELIMINATION (Kron reduction = Schur complement) is the ONE universal reduction; series
(deg-2) / parallel (edge-merge) / Y-Δ (deg-3) / star→clique (deg-k) are its cases. The "irreducible"
bridge dissolves via one Y-Δ. G_eff is ELIMINATION-ORDER-INVARIANT (gauge), but FILL-IN (cost) is
order-DEPENDENT: min-degree order vs hub-first → same G_eff (4.5) but fill 1 vs 29 = the sparse-
Gaussian-elimination ordering problem (min-degree/nested-dissection, optimal NP-hard). RESONANCES:
fill-in = never-discard-residue (eliminated node folds into neighbors); order = gauge on answer / cost
knob on work. ALL witnesses PASS, cross-checked vs nodal solve. The el-atlas G_OR/G_AND algebra IS
Kron reduction over the Kirchhoff Laplacian, restricted to deg≤2.

**AI-2 DONE — het-dispatch model VALIDATED against ground truth** (`het_validate.py`, committed
12663cf). First time the kernel-perf model met a measured OUTCOME (closes the retro's G8 blind spot:
everything had been validated against itself + queried constants, never reality). Real concurrent
CPU+GPU workload (divisible degree-d Horner on 16M float32; GPU host-streamed; threads). Measured each
branch's SOLO rate, PREDICTED f*=r_gpu/(r_cpu+r_gpu) + peak=r_cpu+r_gpu from those, then measured the
combined split-sweep. PASS: composition law holds — low-I (r_cpu 0.3/r_gpu 0.8) predict f*=0.73 peak
1.1, measured f=0.60 peak 1.0 (91% of sum, genuine 1.25× both-beats-GPU); high-I (0.4/10.1) predict
f*=0.96 peak 10.5, measured f=0.90 peak 10.7 (101%). Shortfall below sum = the chassis-coupling breaker
(upper bound), as precommitted. GROUND TRUTH CORRECTED AN OVERCLAIM: low-I was NOT CPU-favored (GPU won
both) — the het pilot's "CPU 3× GPU" used the sgemm rate (~150), but elementwise CPU measures ~0.3
(memory/alloc bound), so GPU wins even host-streamed. OPTIMAL SPLIT IS RATE-DEPENDENT: needs the
specific kernel's MEASURED branch rates, not a peak constant — a live instance of
[[feedback_governing_law_before_special_case]] / "measuring inputs ≠ validating outputs," catchable
ONLY by meeting reality. Methodology: "both-beats-either" gated on branch comparability (principled, not
PASS-chasing; the strict high-I "fail" was the model being RIGHT — f*≈1 means use GPU alone). AI LEDGER:
AI-1 closed (memory), AI-2 CLOSED (this), AI-3 OPEN (collapse 6 pilots → one nodal/Kron engine over
discover()'s Laplacian — shadow-architecture says build the generator not a wrapper), AI-4 OPEN (pin psys
chassis budget via combined-load power → exact het cap). Watched: "measuring inputs ≠ validating outputs"
now has ITS FIRST recurrence-witness (the corrected CPU-favored claim) — promote to its own feedback
memory if it recurs again.

**OPACITY DISSOLVED: kernel rate is structural, "ephemeral" residual is controllable** (`kernel_cost_
model.py` committed 02f9cdb, `residual_decompose.py` committed b6a7c56). User: "needs the measured rate"
is a MODELING FAILURE — if you must RUN it, structural analysis isn't done. rate = structural(op-graph
+ EVAL STRATEGY) × structural(host conductance) × ephemeral(O(1)). The eval strategy is the missed
structure: fused (8 B/elem, I=d/4, scales) vs EAGER (temporary per op, ~20d B/elem, I=0.1 CONSTANT in
d). numpy runs eager → structurally PREDICTS r_cpu's d-independence (0.3@d2≈0.4@d64) WITHOUT running;
my naive I=d/4 used the fused intensity. THEN user: "the ephemeral bits — cause? we can influence them."
Decomposed + MEASURED: eager-FRESH 0.34 vs eager-REUSE(out=) 1.10 GFLOP/s = 3.19× → ~the ENTIRE residual
was fresh-allocation PAGE FAULTS (controllable: buffer reuse/pool; finer axis eager-fresh vs eager-reuse).
Separate ABSOLUTE lever: governor=POWERSAVE, cores 1.5/4.7GHz (32%) → all session absolute numbers clock-
depressed ~3× (CANCELS in residual so all RELATIONS — intensity/f*/composition-law — stay valid; caps
throughput; performance governor = ~3× lever). Reuse OVERSHOOT (residual 1.40>1) = the BW probe is itself
a read-only-sum kernel under-measuring read+write (recursion continues one level). NET: nothing opaque
except OS jitter; the residual is (1) alloc strategy [3.19×] + (2) per-op overhead [fuse] + (3) clock
[~3×] — all influenceable. THIS IS THE jea EVALUATOR COST MODEL: cost structural in (term, fuse/eager,
host); fuse + reuse + performance-governor are the levers. Sharpens AI-3: the unified engine takes
STRUCTURAL kernel descriptors (op-graph + strategy) × host-Laplacian, only the O(1) scalar is runtime.

**STRUCTURAL COTYPE OF THE COST MODEL** (`cost_cotype.py`, committed c1e72ff). User: the cost
REASONING (e.g. "clock cancels in the ratio") should be ENCODED INTO STRUCTURE so the model proves it
and REVEALS broken assumptions — "structural cotype." Built: cost = a typed product of named FACTORS,
each a MONOMIAL in variables (a signature); multiply=add exponents, divide=subtract. residual = rate /
(intensity·measured_BW) where rate = clock·bw_per_clock·intensity·alloc·overhead·jitter and measured_BW
= clock·bw_per_clock·bw_alloc·bw_jitter (the BW probe is ITSELF a kernel). residual signature =
{alloc,overhead,jitter}/{bw_alloc,bw_jitter}. 4 witnesses PASS: (1) CANCELLATION PROVEN — clock/
bw_per_clock/intensity net exponent 0 (the prose theorem is now structural); (2) SUSPECTS ENUMERATED by
construction (exactly the 5 surviving factors, each w/ control knob + falsifiable hyp); (3)
DISCRIMINATION — fresh/reuse differ ONLY in alloc (all else cancels) so measured ratio 0.31≠1 confirms
alloc; overshoot located in bw_alloc⁻¹ (read-only sum probe under-measures read+write); (4) ASSUMPTION-
REVEAL — a WRONG model (BW clock-independent) yields clock exponent 1 → structure FLAGS "residual depends
on governor" (testable+false). PROVE-OR-REVEAL: a failed prediction points at the broken factor, no
opaque residue. Same discipline as [[feedback_registry_as_pi_not_markdown]] + [[feedback_never_discard_
residue]], applied to performance. The opacity-dissolution chain (kernel intensity → residual → cost
cotype) is the methodology capstone for AI-3's engine: every input is a structural factor, not a measured
primitive, and the structure self-falsifies.

**AI-3 DONE — the ONE perf engine** (`jea_perf_engine.py`, committed cf49e06). Six perf pilots
COLLAPSE to one generating operator + N orbit-views (shadow-architecture rule 6: build the generator
not a wrapper). Generator = g_eff/Kron reduction (imported from kron_reduction) over a conductance
graph built from topology_breakers.discover() + cudaDeviceProp. VIEWS (all route through the ONE
solve, 5/5): bottleneck = top of elimination trace (PCIe host / DRAM device); spectrum = the trace
(PCIe 95.9% > DRAM 3.4% > L2 > L1); ridge = compute↔memory bridge null (56.8 FLOP/byte); dispatch =
2-branch parallel solve (f*=0.24). Witness 1: the operator SUBSUMES the folds — chain g_eff == G_AND,
parallel g_eff == G_OR (the spectrum fold + het sum are special cases of the same solve). Inputs
STRUCTURAL (host conductances from discover(), kernel intensity from op-graph+strategy); only clock+
jitter runtime, CANCEL in the ratios. In-build fix: device bottleneck first came out L3 (cache BW
anchored to host-sysram×small → inverted hierarchy); fixed by anchoring caches ABOVE the DRAM floor
(caches faster by construction; cache BW unmeasurable → don't fabricate inverting numbers). AI LEDGER:
AI-1/2/3 CLOSED, AI-4 open (pin psys chassis budget via combined-load power). The kernel-perf nedge
program is now: discover() → Kron-solve engine → views, all structural + self-falsifying (cost_cotype),
governed by Kirchhoff. The OPEN recursion rung: the BW probe is itself a read-only-sum kernel (bw_alloc
term) — a read+write+strategy-matched probe would de-opacify the host conductance numbers themselves.

**SENSITIVITY VIEW + min() EMERGES FROM THE SETTLE** (`perf_sensitivity.py` committed cd47e04,
`geodesic_min.py` committed 19f0aa2). SENSITIVITY (the rigorous bottleneck ranking): dG_eff/dG_i =
(Δv_i/V)² from ONE nodal solve; fractional s_i = edge i's share of DISSIPATED POWER = resistance share
on a chain (= the spectrum view) but defined on ANY graph (ranks bridge/mesh edges; bridge edge → 0 at
the Wheatstone balance = no current). "How much fixing helps" = the literal derivative (== finite-diff,
verified; top edge = max real gain). min() CORRECTION (user, deeper than mine): min is NOT an operator
to pick — the network SETTLES to minimum dissipation (Thomson = Kirchhoff = resistance-metric geodesic);
the settled G_eff IS the truth; min is its READ-OFF in the dominated regime. Witnesses: G_AND→min as
conductances separate (min emerges FOR FREE, none computed); at the ridge min over-predicts 2× (settle=
a/2 = the rounded knee); Thomson confirmed (2000/2000 perturbations raise P → solve IS the energy min);
geodesic = R_eff→bottleneck resistance. SELF-CORRECTION: my "parameterize the semiring, pick p" was too
permissive — the conductance solve (p=1) IS the physics, min (p→∞) its shadow. The min↔G_AND axis =
perfect-overlap↔serial PIPELINING (a structural/controllable choice), not a free semiring. REJECTED the
external "replace min:=G_AND" suggestion's reasoning while noting G_AND IS the no-overlap settle.
[anti-agreement-without-yielding: pushed back on a flattering external validation's wrong fix.]

**AI-6 DONE — engine views validated vs real measured bottlenecks** (`engine_validate.py`, committed
3d81038). The engine's ridge/bottleneck/spectrum views predict the bottleneck an INDEPENDENT
measurement finds, for 3 kernels: (1) streaming sum (I=0.25) → memory (core-scaling saturates 0.21) ==
engine; (2) L2-resident sgemm (I=43) → compute == engine; (3) GPU host-streamed (3.4 vs device 13.5
GFLOP/s, transfer ~PCIe) → PCIe == engine spectrum top. THE FINDING (hunt-opacity applied to the
validation ITSELF): the first ground-truth signal for compute, CORE-SCALING, was CONFOUNDED — a
genuinely compute-bound sgemm scaled only 0.49 then 0.15 because the P/E-heterogeneity+turbo breakers
drag compute scaling toward the memory range (straddles any threshold). Core-scaling isn't a clean
primitive; dissolved with the structural discriminator: working-set (768K) < largest-private-cache
(1280K from discover()) → never touches DRAM → not DRAM-bound → compute (run-invariant). [[feedback_hunt
_opacity_after_green]] biting in real time on my own ground-truth. AI LEDGER: AI-1/2/3/5/6 CLOSED; AI-4
open (psys chassis budget via combined-load power); bw_alloc rung open (BW probe is itself strategy-laden).
The perf engine is now validated against measured reality, not just internal consistency — the whole
kernel-perf nedge program (discover → Kron settle → views, structural + self-falsifying + ground-truthed).

**POWER ARMS EXPERIMENT → "clock cancels" FALSIFIED → `clock` is TWO clocks** (`power_arms.py`
committed d993110, `two_clock_domains.py` committed 5103b20). Power config IS user-accessible: governor/
EPP sysfs are root-only, but `power-profiles-daemon` (what KDE drives) is settable by the active session
via `powerprofilesctl` NO SUDO (confirmed by no-op set). Box was on `power-saver` → that's the 32%-clock
cause all session. Swept the 3 accessible PPD arms (auto-restored power-saver), measured: performance 4.39
GHz/157 GFLOP/s/14.7 GB/s/ridge 10.7; power-saver 1.45/60/10.2/5.9. W1 PASS: absolute lever real (3.0×
clock, 2.6× compute — residual_decompose governor claim ground-truthed). W2 FAIL: ridge NOT invariant
(45% swing) → FALSIFIES my single-`clock` "clock cancels in the ratio" claim. CAUSE: compute scaled 2.60×
but memory only 1.44× — DIFFERENT CLOCK DOMAINS (core vs memory-controller/uncore). CORRECTION: split
`clock`→{clock_core,clock_mem}; ridge=compute/mem ~ clock_core/clock_mem (CROSS-domain → power-dependent),
predicted scale 2.60/1.44=1.80 == measured 1.81 (QUANTITATIVE match to 1%); memory-bound residual stays
SAME-domain → cancels → residual_decompose HOLDS, correctly scoped. SCOPED STATEMENT (refines cost_cotype/
residual_decompose/geodesic_min): same-domain ratios cancel the clock, cross-domain (ridge) scale as
clock_core/clock_mem. The structural-cotype prove-or-reveal delivered: a falsified prediction pointed at
the broken factor (single clock), which split — concrete [[feedback_hunt_opacity_after_green]] on my OWN
cancellation claim. Finer arms (EPP×5, governor×2, no_turbo, per-core caps) root-gated next granularity.
Machine RESTORED to power-saver.

**HW-SURFACE TAXONOMY — opacity = unenumerated surface (CAPSTONE)** (`hw_surfaces.py`, committed
2c07c6c). User assertion "ALL hw detail is inspectable somewhere" — CONFIRMED. 18/18 hardware facts this
session used map to a PRESENT introspection surface (14 user-accessible, 3 root, rest driver/gated);
ZERO irreducibly opaque. Surfaces stratify by privilege: user (sysfs/procfs/DMI-subset/hwmon/PCI/CPUID/
NVML) → user-polkit (powerprofilesctl) → root (full DMI/dmidecode, ACPI tables, MSR APERF-MPERF/RAPL/
uncore-ratio, debugfs) → gated (PMU perf_event_paranoid, ncu). ACID TEST: the two clock domains we found
BY EXPERIMENT (power_arms) were BOTH in sysfs all along — core (cpufreq 4.60 GHz) + uncore/mem-controller
(intel_uncore_frequency 4.00 GHz). A complete discover() reading both predicts ridge-power-dependence A
PRIORI — the experiment was AVOIDABLE; the fact was just unenumerated. STRUCTURAL/EPHEMERAL SPLIT is IN
the surface: clock cur(governor)/max(structural); PCIe current 2.5GT/s(ASPM-idle)/max 16GT/s gen4 — so
"PCIe ~6 GB/s" had an ephemeral link-state component too. THE GRAND UNIFICATION of the whole opacity-
dissolution arc (kernel intensity → residual → cost cotype → min-emergent → two-clocks → THIS): OPACITY =
A SURFACE NOT YET ENUMERATED, never irreducible. discover() can be COMPLETE = systematic surface
enumeration; every fact = structural bound (inspectable) + ephemeral current (inspectable, time-varying);
14/18 buildable WITHOUT root. Machine: HP Victus 15 (i7-12650H + RTX 4050, GPU link gen4-max/gen1-idle).
This is the principled completion target for AI-3's discover() and the substrate-ℝ-on-GPU cost model.

**KERNEL-PERF NEDGE PROGRAM COMPLETE (host-side live controller)** — AI ledger WAL =
`el-atlas/tools/ai_ledger.md` (single source of truth). The session-origin goal
(live, continual, controlling the scheduler) is realized: `live_dispatcher.py` (committed 5d9665d) polls
ephemeral state (governor/clock/thermal/ASPM-link/dGPU-power) → re-solves the integrated conductance
graph (`perf_graph_integrated.py`, AI-10: the 7a-d bricks + DMI composed, ONE Kron op over shared nodes
iMC/package-power/clock/PCIe) → emits current bottleneck + optimal dispatch f*, anytime. Decision is a
live function of state (f* rises as link ramps; compute_BW falls with temp; bottleneck identity shifts
PCIe→iMC→thermal). Full stack: discover()→Kron settle→views, structural (no measured primitives except
O(1) clock/jitter), self-falsifying (cost_cotype), ground-truthed (engine_validate/het_validate/power_arms),
and now LIVE. CLOSED: AI-1..11,13,bw_alloc,AI-4(hw-limit). OPEN (named, in ai_ledger.md): AI-11b (on-device
actuator = THIS jea debt: persistent megakernel acting on the loop's decisions), AI-12 (chassis-cap test).
New disciplines this arc: [[feedback_firmware_unpopulated_surface]] (3rd gate-type), [[feedback_hunt_opacity
_after_green]], [[feedback_validate_outputs_not_inputs]], [[feedback_governing_law_before_special_case]].

NEXT (jea debts): the on-device dynamic dispatcher (persistent megakernel + device work queue
first; CDP2 / device-graph-launch second) — the real architecture; multi-limb past 128-bit
(flag-triggered); RE-ABLATE the ℤ-128 tiling claim; general device-side INTERNING (parallel
dedup) for IRREGULAR traces — the open case the cohomological substrate reduction needs.

**jea_m2_* CLEAN RE-REALIZATION + AI-11b CLOSED (the on-device actuator)** (2026-06-14, scripts/
jea_m2_{workqueue,dag,qcarrier,dispatch}.py, committed): a clean, self-contained, witness-per-script
reference build of the dataflow core — M2a lock-free work-queue drain (200k nodes exactly-once); M2b
data-driven SPPF-DAG sweep (60k, deadlock-free via atomicCAS claim + children-done ready-gate); M2c the
exact ℚ carrier (num,den) reduced by an on-device fused gcd-window with escalate-don't-truncate (54k
exact + 10 escalated == the unrepresentable set EXACTLY, poison-propagated, --device-int128); M2d closes
AI-11b — the el-atlas nedge oracle steers the resident kernel LIVE via the AI-11b zero-copy mapped-control
channel (resident kernel spin-waits for the zero-copy GO, then runs the pushed schedule). HONEST SCOPE
(I initially over-framed this as "closing the primary goal"; corrected): this does NOT supersede the more
advanced jea_generator_* ladder or the already-closed Agda bridge (jea_agda_bridge, 8046b4c). The
GENUINELY NEW piece is M2d's live value-window↔trace-window (eager/lazy reduction) Pareto knob — distinct
from the existing controller, which steers only K (the gcd-window size). Measured (40k DAG): eager 147604
gcd-ops / 0 non-canonical vs lazy 5429 gcd-ops (27× less) / 33887 non-canonical; both exact; oracle's
MODE choice flips across the bridge-null f*=C*=4.20. WAL: scripts/jea_m2_ledger.md. INTEGRATION FOLLOW-ON
(the real next step): add this eager/lazy reduction-mode knob to jea_generator_dag/strat/bucket's
controller and drive a jea_agda_bridge-emitted DAG through it — fuse the new knob with the closed path.

**INTEGRATION DONE — the eager/lazy knob fused into the production Agda path** (2026-06-15, scripts/
jea_generator_dag_mode.py + jea_agda_dispatch.py, committed): M2d's value-window↔trace-window reduction-
mode knob now lives in the PRODUCTION cooperative-generator evaluator (jea_generator_dag), not just the
synthetic reference build. jea_generator_dag_mode = jea_generator_dag + a MODE control slot read live
alongside K (eager: windowed gcd to b==0, canonical; lazy: skip gcd, emit unreduced), made MATURE with
__int128 combine + overflow detection → reduce-when-the-lane-forces → escalate (poison-propagated), so
lazy is not a silent-overflow stub. The nedge oracle (M2d resistance-sum/argmin) picks MODE from gcd-work
+ non-canonical-COMBINE count + workload C, flipping across the bridge-null f*. jea_agda_dispatch reuses
the closed bridge's Agda machinery UNTOUCHED (typecheck=refl vouchers, parse, to_dag) and evaluates the
Emit.agda term (2/3+1/2)*(1/4*3/5)=7/40 through the MODE-aware evaluator: EAGER and LAZY both == Agda's
refl-vouched value, oracle picks EAGER for the canonicality-demanding workload. So the controller now
steers K AND the value↔trace reduction mode, on the real Agda-on-GPU path. SUBTLETY found: build_dag
leaves can be non-canonical (2/2 etc.) and only combines are reduced, so the honest non-canonical measure
is over COMBINES, not leaves. Carrier boundary: u64 fits L<=128; L>=256 overflows → escalates (the
existing 128-bit carrier jea_generator_dag128 is the next width). NEXT: same MODE knob into the
high-throughput stratified paths (jea_generator_strat/bucket).
UNIFICATION ARC COMPLETE -- BOTH APEXES (2026-06-15, WAL jea/jea_unification_ledger.md -- the substantive JEA
evaluator was promoted from scripts/ to its own jea/ project folder 2026-06-16, audited clean). After the
strictify+DBE+retrospective pass named two attractors, all 8 U-bricks landed: APEX-2 (the bucketed-lattice
Q carrier) = U1 packed mixed-width (jea_carrier_bucketed, 2.46x denser) + U2 MODE in the stratified path
(jea_generator_strat_mode) + U3 on-device escalation routing u64->u128->byte-limb (jea_carrier_escalate,
delivers to 1354b) + U4 trace-window dual = the discarded gcd residue (jea_carrier_trace, canonical+compare-
by-prefix on GPU, free) + U5 byte-limb division -> reduce at arbitrary precision (jea_limb_div). APEX-1
(the universal engine) = U6 fuse spawn⊕scheduler⊕rewrite in one deadlock-free kernel (jea_universal_engine,
~2 Gnode/s, dynamic pool) + U7 device interning TREE->SPPF (jea_intern, 27594x collapse) + U8 real shared
SPPF from Agda evaluated exact (jea/agda-emit/EmitDAG.agda + jea_agda_dag.py, refl-vouched). pack/escalate/
reduce/trace are all MIGRATIONS on one lattice; spawn/schedule/rewrite are one kernel. ZERO unification
bricks remain; only 2 debts (U9 nedge-model refill, U10 re-ablate Z-128 tiling). Two witness-leniency
catches en route (U2 "lazy exact" masked escalation; I3 W2 pow-2-rounding) both fixed -- a witness that
folds its failure mode into the pass set isn't a witness ([[feedback_validate_outputs_not_inputs]]).

OVERFLOW PREDICTED, NOT JUST DETECTED (user, 2026-06-15): escalation is now gated by a cheap operand-
bit-width test BEFORE the multiply -- a k-bit times an m-bit value is < 2^(k+m), so the product provably
fits the u64 lane iff the widths sum within it (mul: <=64; add: each product <=63 + dl*dr<=64). Safe ->
native u64 (no __int128); else -> the wide __int128 exact-detect/reduce-when-forced/escalate path. This
IS the SWAR W>=2L lane-spacing rule (jea_swar_mul) applied DYNAMICALLY: SWAR statically reserves 2L room
knowing operands are <=L bits; the evaluator bit-tests data-dependent operands at runtime. Same invariant
(product-fits-lane <=> operand-bits <= half-lane), static vs dynamic. "Know before you spend" -- predict
(__clzll) beats detect (compute-wide-then-check). Verified bit-identical results + escalation unchanged.
MAGNITUDE-BUCKETING — lane width = MSB+1 (user, 2026-06-15, scripts/jea_bucket_msb.py): the predictor's
conclusion = bucket each value by its bit-width into a SWAR lane (rounded to the pow-2 ladder
{1,2,4,8,16,32,64}). Buckets are DYNAMIC via the MIGRATION LAW: mul adds operand widths (migrate UP), add
~max+1, gcd-reduce shrinks (migrate DOWN), escalate = width past the top bucket (migrate to next carrier).
This UNIFIES four built pieces: jea_swar_mixed (mixed-width lanes in one register = the STATIC packing;
bucketing is its data-driven form), jea_generator_bucket (the scheduler, same bucket machinery keyed on
MAGNITUDE not depth), the overflow predictor, and the eager/lazy MODE knob = literally bucket-OCCUPANCY
control (eager/reduce keeps values in narrow buckets, lazy/defer lets them drift wide + escalate sooner).
Reduction=downward migration, escalation=upward. VERIFIED on real GPU per-node values (L=128): migration
law SOUND both modes (predicted bucket >= actual = no-silent-overflow as bucketing); reduction migrates
down (eager 882 lane-bits vs lazy 1341); lazy drifts wider (max bucket 64 vs eager 32); SWAR-pack 17x
denser than flat lane-per-component. Caught: pred->actual gap is dominated by pow-2 ROUNDING, not
reduction -- the honest "reduction migrates down" measure is direct eager-vs-lazy total lane-bits. NEXT:
pack the cooperative evaluator's lanes by magnitude bucket (SWAR-dense narrow values), re-bucket on each
migration -- the data-driven mixed-width carrier.
