# JEA Evolution — a first-principles ladder to the `jea/` system

This folder is the **recorded developmental trace** of Just-Enough-Agda-on-GPU: ~48
small scripts, each isolating **exactly one concept**, that together build an understanding
of the mature system in [`jea/`](../) from the ground up. They are **frozen historical
snapshots**, not live code — read them in order, run each, watch one idea enter at a time.

The mature system absorbed every spine idea into a handful of modules
(`jea_carrier`, `jea_resident`, `jea_engine`, `jea_navigator`, …). These scripts are where
each of those ideas was **first built in isolation** and proven on its own.

> **Why keep frozen snapshots with their `NEXT:` notes intact?** Because the `NEXT:` at the
> end of rung *N* is usually *answered by rung N+1*. The forward-pointers are the ladder's
> rungs showing through. (This is the opposite discipline from `jea/` proper, where stale
> `NEXT`s are removed — there the code is live; here the code is a museum exhibit.)

## The shape: a ladder of ladders

The either/or "is this a junk pile to archive, or clutter to ignore?" dissolves: it is
**neither** — it is a curriculum. And the structure is **recursive**:

- **Within a chapter**, a strict monotonic ladder — each rung adds *one pain* and resolves it
  (carrier: limb → swar → mul → mixed → bignum → ℚ; generator: increment 1→5; engine: M2a→M2d).
- **Across chapters**, the chapters *are* the architecture: what a value **is** → how values
  **pack** → how the eval loop **runs** → **escalation & dataflow** → how the schedule is **solved**.

```
I.   ROOTS      what jea is, and how we measure it
II.  CARRIER    what a value IS (suspended generator, graded width, value↔trace dual)
III. GENERATOR  how the eval loop runs on-device (the 5 increments)
IV.  ENGINE     escalation-as-spawn + lock-free dataflow (the M2 milestones)
V.   CONTROL    how the schedule is solved (the coordinate→geometry ladder)
VI.  INTEGRATE  an Agda term, evaluated end-to-end, MODE chosen by the oracle
99.  SIDE-TRAILS valid explorations that are off the main spine (kept, marked)
```

## How to run

```bash
python jea/evolution/02_carrier/jea_swar.py        # pure-Python rungs: no deps
python jea/evolution/03_generator/jea_generator_kernel.py   # GPU rungs: need cupy + a CUDA device
```
Each rung prints its witnesses and a final `PASS`/`FAIL`. Rungs that build on the foundation
begin with a small **bootstrap** that puts `jea/` (for `jea_core`, `jea_limb_gpu`, …) and the
sibling chapters on `sys.path`. Three control rungs (`live_cost`, `megakernel`, `telemetry`)
additionally reach the el-atlas tools under [`scratch/el-atlas`](../../scratch/el-atlas).
Standalone rungs (half the ladder) have no bootstrap — they are deliberately pristine.

## The ordered curriculum

Legend for **role**: `spine` = a distinct teaching rung · `scaffold` = measurement/diagnostic ·
`dead-end` = an honest failed branch (the discipline visibly working).

### I — Roots
| # | rung | file | the one concept | absorbed by `jea/` |
|---|------|------|-----------------|--------------------|
| 1 | M1 | `01_roots/jea_gpu.py` | F₂ semiring inside-fold over a GPU-resident interned SPPF, branchless combine | `jea_sppf` `jea_zsppf` `jea_eval` |
| 2 | — | `01_roots/jea_roofline.py` | counter-free bottleneck diagnosis by ablation — *measure, don't prophesy* (scaffold) | informs `jea_navigator` |
| 3 | — | `01_roots/jea_ackermann_spec.py` | the universal spawn-loop (pop/reduce/spawn/resolve): value=recursion=escalation, host oracle | `jea_engine_pool` |
| 4 | — | `01_roots/jea_ackermann_gpu.py` | that spawn-loop ON-DEVICE — per-thread stack replaces host recursion (non-primitive-recursive on silicon) | `jea_engine_pool` `jea_resident` |
| 5 | U7 | `01_roots/jea_intern.py` | device-side parallel dedup (hash-cons by height): tree → canonical SPPF DAG | `jea_mega` `jea_zsppf` |

### II — Carrier (what a value *is*)
| # | rung | file | the one concept | absorbed by `jea/` |
|---|------|------|-----------------|--------------------|
| 6 | — | `02_carrier/jea_limb_spec.py` | the carrier is a byte-limb **suspended generator** (pay-for-size, unfold-on-demand), not a frozen u64 | `jea_limb_gpu` `jea_carrier_base` |
| 7 | — | `02_carrier/jea_swar.py` | SWAR add: one full-adder formula descending widths 32→…→1, GF(2) at the floor | `jea_bitkernel` `jea_carrier_base` |
| 8 | — | `02_carrier/jea_swar_mul.py` | single-lane multiply via bit-serial accumulate + lane-spacing (spill-avoidance) | `jea_bitkernel` (`bs_mul`) |
| 9 | — | `02_carrier/jea_swar_mixed.py` | heterogeneous lane widths in one register; mask-driven add | `jea_graded` `jea_carrier` |
| 10 | — | `02_carrier/jea_swar_mixed_mul.py` | mixed-width multiply needs per-width passes — add ≠ mul under heterogeneity | `jea_graded` |
| 11 | — | `02_carrier/jea_swar_bignum.py` | schoolbook convolution + per-lane carry: single-lane mul → multi-limb bignum | `jea_limb_gpu` `jea_bitkernel` |
| 12 | — | `02_carrier/jea_swar_mixed_bignum.py` | mixed-width bignum — the per-group carry-shift is a *structure*, not a bug | `jea_carrier` |
| 13 | — | `02_carrier/jea_swar_q.py` | the payload: a lane-pair carries ℚ=(num,den); ℚ-mul = dual bignum; (num,den) = el-atlas nedge | `jea_graded` (`q_*`) `jea_divstr` |
| 14 | I3 | `02_carrier/jea_bucket_msb.py` | magnitude bucketing (width = MSB+1) + the migration law (mul widens, add +1, reduce ↓, escalate ↑) | `jea_graded` `jea_carrier` |
| 15 | U1 | `02_carrier/jea_carrier_bucketed.py` | the data-driven mixed-width carrier at native dtypes (u8/16/32/64) | `jea_carrier` `jea_graded` |
| 16 | U3 | `02_carrier/jea_carrier_escalate.py` | on-device tier routing u64→u128→byte-limb by migration-law *prediction*; deliver at top, no wrap | `jea_apex` `jea_apex_deliver` |
| 17 | U5 | `02_carrier/jea_limb_div.py` | byte-limb division (restoring-doubling) → ℚ reduce (gcd + canonical) at arbitrary precision | `jea_divstr` |
| 18 | U4 | `02_carrier/jea_carrier_trace.py` | the trace-window lane on GPU (CF via Euclid): canonical by construction, residue-free; dual of the value-window | `jea_trace_window` `jea_carrier` |

### III — Generator (how the eval loop runs) — *the increment ladder*
| # | rung | file | the one concept | absorbed by `jea/` |
|---|------|------|-----------------|--------------------|
| 19 | incr 1 | `03_generator/jea_generator_kernel.py` | the persistent megakernel loop: barriers, cross-block visibility, observe/publish | `jea_generator_unified` |
| 20 | incr 2 | `03_generator/jea_generator_dag128.py` | the 128-bit carrier — *escalate* (detect overflow), never silently truncate | `jea_generator_unified` |
| 21 | incr 3 | `03_generator/jea_generator_fold.py` | the worker's real gcd-window step on resident nodes; the K-closed loop | `jea_generator_unified` `jea_generator_strat` |
| 22 | incr 4 | `03_generator/jea_generator_async.py` | ring-buffer async — remove the per-tick barrier (a Kahn process network) | `jea_engine_pool` |
| 23 | incr 5 | `03_generator/jea_generator_coop.py` | branchless cooperative: no roles, monotonic control, one unified body | `jea_generator_unified` `jea_branchless` |

### IV — Engine (escalation + dataflow) — *the M2 milestones*
| # | rung | file | the one concept | absorbed by `jea/` |
|---|------|------|-----------------|--------------------|
| 24 | M2a | `04_engine/jea_m2_workqueue.py` | a lock-free persistent megakernel drains a work-queue **exactly once** | `jea_engine` `jea_mega` |
| 25 | M2b | `04_engine/jea_m2_dag.py` | data-driven sweep: nodes fire when children ready; fixpoint, no per-stratum relaunch | `jea_engine` |
| 26 | M2c | `04_engine/jea_m2_qcarrier.py` | exact ℚ + fused gcd-window + escalate-don't-truncate poison propagation | `jea_engine` `jea_mega_eval` |
| 27 | M2d | `04_engine/jea_m2_dispatch.py` | the oracle steers value↔trace (eager/lazy) Pareto **live** via zero-copy control | `jea_mega_eval` `jea_navigator` |
| 28 | U6 | `04_engine/jea_universal_engine.py` | spawn+scheduler+rewrite fused in ONE kernel — *parallel track*: dynamic rewrite, dual to the fixed-DAG ℚ-fold | `jea_resident` |
| 29 | C3 | `04_engine/jea_engine_tiers.py` | the carrier ladder as **escalation-as-spawn**; tiers predicted by bit-width, placed before computing | `jea_engine_pool` `jea_apex` |
| 30 | C3-apex | `04_engine/jea_engine_apex.py` | intern-during-spawn + predict-place tiers + deliver >u128: Growth × Carrier × Sharing in one reduce-step | `jea_mega` `jea_apex` |
| 31 | Δ-J1-rest | `04_engine/jea_megakernel.py` | persistent kernel reads the operating-point (granularity g) live; the sum is invariant to schedule (combine ⊥ schedule) | `jea_mega_eval` |

### V — Control (how the schedule is solved) — *the coordinate→geometry ladder*
| # | rung | file | the one concept | absorbed by `jea/` |
|---|------|------|-----------------|--------------------|
| 32 | Δ-A4 | `05_control/jea_telemetry.py` | host reads meters → a TOCTOU-free epoch-coherent package (double-buffer swap) | `jea_navigator` |
| 33 | Δ-J1 | `05_control/jea_actuator.py` | a persistent on-device kernel consumes the resident package live, no relaunch | `jea_apex` `jea_carrier_solve` |
| 34 | — | `05_control/jea_nedge_model.py` | the control law: one loop, two roles (worker/controller), K-schedule via the bridge, exact ℚ | `jea_cost` `jea_carrier_solve` |
| 35 | U9 | `05_control/jea_nedge_refill.py` | distribution-aware refill: K tracks each bucket's depth, not max-depth-only | `jea_cost` |
| 36 | — | `05_control/jea_consolidation_pilot.py` | knob audit: a genuine knob (winner *flips*) vs a dominated collapse | seeds the surfaces |
| 37 | n-path | `05_control/jea_knob_surfaces.py` | every knob = corners of a continuous-parameter **surface** (n-path, not binary) | `jea_navigator` |
| 38 | — | `05_control/jea_layout_surface.py` | the layout optimum is a partition topology + region, **measured** not baked | `jea_navigator` |
| 39 | D4 | `05_control/jea_schedule_surface.py` | the schedule is a (granularity g, dynamism) surface; coop/strat/pool are its corners | `jea_cost` `jea_navigator` |
| 40 | Δ-J3 | `05_control/jea_apex_gsurface.py` | the apex active-lane axis, measured to an interior\|corner\|flat verdict | `jea_navigator` |
| 41 | Δ-J6 | `05_control/jea_interior_surfaces.py` | K/layout surfaces measured to a **definite** verdict, reactive to the live kernel | `jea_navigator` |
| 42 | D1/D2 | `05_control/jea_live_cost.py` | the schedule cost READ OFF the live Kron-solve; binding-edge from sensitivity, not a magic ternary | `jea_cost` `jea_onegraph` |
| 43 | D1 | `05_control/jea_fit_plant.py` | **dead-end (the discipline working):** tried to fit plant constants; output-side ground-truth *refused* the fit | not absorbed — the falsification *is* the lesson |

### VI — Integrate
| # | rung | file | the one concept | absorbed by `jea/` |
|---|------|------|-----------------|--------------------|
| 44 | — | `06_integrate/jea_agda_dispatch.py` | an Agda-emitted term, evaluated on the production cooperative GPU evaluator, MODE chosen by the oracle — the loop closed | `jea_agda_apex` `jea_agda_bridge` `jea_agda_dag` |

### 99 — Side-trails (off the main spine — valid, kept, marked)
| rung | file | what it explored | why off-spine |
|------|------|------------------|---------------|
| incr 3 (honest) | `99_side_trails/jea_generator_telemring.py` | a telemetry-ring windowing observation for time-varying workload | the O(1)-observe it sought is already in increment 5 (dead-end) |
| — | `99_side_trails/jea_generator_bucket.py` | bucketized substrata + escalation-priority scheduling | a runtime *policy* layered on increment 5, not a generator increment (scaffold) |
| — | `99_side_trails/jea_generator_dag_mode.py` | the eager/lazy MODE knob ported into the cooperative evaluator | a controller axis (like K), absorbed as a mode — redundant |
| U2 | `99_side_trails/jea_generator_strat_mode.py` | the same MODE knob in the stratified high-throughput path | same controller axis, absorbed — redundant |

## The honest dead-ends are part of the curriculum

`jea_fit_plant` (rung 43) and `jea_generator_telemring` are kept *because* they failed:
the first shows output-side ground-truth refusing to bless a constant-fit (the
"validate outputs, not inputs" discipline catching an error in the act); the second shows an
optimization that a later rung made unnecessary. A ladder that hides its dead-ends teaches
that the final shape was obvious. It wasn't.
