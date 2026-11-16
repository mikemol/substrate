---
name: feedback_structural_not_scalar
description: "a hardware/perf \"structural bound\" is NOT a scalar — it is a discovered conductance TOPOLOGY solved by Kron, whose binding edge shifts with live state; never scalarize the cost model, and read the WAL/git not stale docstrings"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

When modeling hardware/perf cost, "structural_bound" is **not a scalar you multiply an ephemeral scalar by.**
It is the DISCOVERED CONDUCTANCE GRAPH (topology_breakers.discover) solved by Kron node-elimination; the
bottleneck is a THEOREM of KCL, emergent from the topology, not a number. Each dynamic EDGE is a
(structural bound, live state) PAIR, and the BINDING edge SHIFTS with live state (PCIe -> iMC -> thermal).
So you CANNOT pre-collapse to a scalar -- which edge binds is itself state-dependent; the answer (bottleneck
id, dispatch f*, g_eff) is the OUTPUT of a live Kron-solve re-run each window, never a precomputed number.

The kernel-perf/hardware-discover arc's major lesson (WAL-confirmed): **every scalar/static assumption was
invalid** and got replaced by a structural/relational one -- G_OR/G_AND-as-ops -> reductions of the nodal
solve; min-as-operator -> the geodesic (minimum-dissipation) settle; "clock cancels in the ratio" -> FALSIFIED
(TWO clock domains; the cross-domain ridge clock_core/clock_mem does NOT cancel; same-domain cancellation is a
narrow special case, not a license to scalarize); "chassis BINDS" -> retracted (state-dependent); psys/EDAC ->
firmware-unpopulated. I re-committed the scalarization twice (2026-06-15) -- cost = struct[scalar] x
ephem[scalar], "same-domain cancels" -- a category error.

ROOT of the relapse: I (and a research agent) read the tool DOCSTRINGS/COMMENTS, which are STALE -- they
assert the pre-falsification scalar story and were never corrected in place (kernel_cost_model.py = the literal
source; cost_cotype.py single-clock-cancels; residual_decompose.py; jea_perf_engine.py; aspm_link.py). The
durable truth is in the WAL: ai_ledger.md + the git commit MESSAGES (which RETRACT/FALSIFY), not the comments.

**How to apply:**
1. A perf/cost "bound" is a SOLVE over a discovered graph, never a scalar. Wire the live machinery
   (discover -> typed GraphElement registry -> live edge-state poll -> kron_reduction.g_eff, re-solved per
   window); read the bottleneck/winner OFF the solve under current state. Don't fit or multiply scalars.
2. When auditing/reading old code, **read the WAL (ai_ledger + git log bodies), not the docstrings** -- comments
   go stale and orphan falsified claims (twin of [[feedback_silo_sprawl_orphans_fixes]]). git-log for
   retract/falsified/corrected first.
3. Same-domain cancellation, peak constants, "the bottleneck is X" -- all are narrow/state-dependent; never
   generalize a scalar shortcut. Extends [[feedback_governing_law_before_special_case]] and
   [[feedback_validate_outputs_not_inputs]]: solve the network, don't collapse it to a number.
