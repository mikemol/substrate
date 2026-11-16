---
name: feedback_noise_floor_is_flat_region
description: "a CHOICE that sits at the noise floor is the signal to stop adjudicating the 1-path (which discrete option wins) and decompose the options into their common parameterized structure (n-path) — the tie is a FLAT REGION of the shared cost surface, not noise to denoise"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

When you are choosing between discrete alternatives (strategies, schedules, configs) and the winner sits at
the MEASUREMENT NOISE FLOOR, do NOT pour effort into denoising the measurement to crown a winner. The tie is
the SIGNAL that the 1-path question ("which discrete option wins?") is the wrong one. Apply "find the common
structure, recursively" as an **n-path**: decompose the alternatives into the common PARAMETERIZED STRUCTURE
they are corners of, and the choice dissolves.

The tie is not noise -- it is a **flat region of the shared cost surface**. The alternatives are nearby points,
and the axis that distinguishes them is flat in that regime. Denoising can't (and shouldn't) crown a winner on
a flat surface; there is no winner to find, and that's fine -- the live solve picks any operating point there.

Worked instance (jea schedule, D4): I treated coop/strat/pool as 3 discrete strategies and tried to adjudicate
dominance; the coop/strat tie on WIDE workloads flickered run-to-run and I kept bumping replication (median-5,
median-9) to stabilize a verdict. Wrong. The n-path: coop/strat/pool are CORNERS of (launch-granularity g∈[1,S],
dynamism d) over ONE persistent-kernel+work-queue engine -- coop=(g=1,static), strat=(g=S,static), pool=(g=1,
spawn). cost surface total_time(g) = g·t_launch + work/(occupancy(g)·rate). The wide-workload tie is STRUCTURAL:
the whole launch span is (S-1)·t_launch, negligible for small S, so the surface is FLAT in g -> coop≈strat by
construction. Deep-narrow (large S) makes g·t_launch steep -> g*=1 (coop) a real ~4x minimum. The "choice"
collapses to a parameter g* the solve reads off the surface; no discrete adjudication, no denoising a tie.

**Refinement (n-path is NOT binary discrete-vs-surface -- it is the CONVEXITY of cost c in the parameter θ).**
Once you decompose a "knob" into (continuous θ, named corners, cost surface c(θ,workload)), classify by c-in-θ:
- BANG-BANG (c linear in θ): the optimum is ALWAYS a corner. The discrete "which preset wins" view is FAITHFUL
  -- the named presets ARE the operating points (e.g. eager/lazy, value/trace: linear cost -> corner optimum).
- INTERIOR (c convex in θ): the optimum is BETWEEN corners. The discrete 2/3-corner audit UNDERSAMPLES -- a
  HYBRID (intermediate K window, coarse bucketing, hybrid launch-granularity drain-k-strata/launch) can beat
  EVERY named preset. That is a missed OPTIMUM, distinct from a missed CONSOLIDATION (a dominance audit only
  finds the latter). jea_knob_surfaces.py: mode/repr proven bang-bang; K/layout/schedule-g interior-candidate.
And PROPAGATE: when ONE axis decomposes to a surface, apply the same decomposition to its SIBLING axes
proactively -- don't wait for each to throw a noise-floor tie (the schedule tie forced it; the siblings needed
it too but were silent). The engine is one point in the joint parameter polytope; the solve navigates it.

**How to apply:**
1. Choice + noise-floor tie => STOP denoising. Ask: what common parameterized structure are these options corners
   of? Decompose to the parameter axes (the n-path); the named options are corners.
2. Re-read the tie as geometry: it is a flat region of the shared cost surface. A flat axis means that parameter
   doesn't matter in that regime -- not that your meter is bad. (Distinguish from a real noisy margin only AFTER
   you've checked whether the structural surface is flat there: total_time(g) flat in g for small S is analytic.)
3. The winner becomes an operating POINT the live solve picks on the surface, not a label you keep/collapse. The
   consolidation/dominance question ("is option X removable?") dissolves into "X is a corner of the parameter
   space; the solve navigates it." Refines "find the common structure recursively" ([[feedback_structural_not_scalar]],
   [[feedback_reread_meters_toctou]]): the tie tells you the 1-path axis is flat, so drop to the n-path.
