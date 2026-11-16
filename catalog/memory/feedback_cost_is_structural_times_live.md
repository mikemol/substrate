---
name: feedback_cost_is_structural_times_live
description: "a decision's COST is never a hardcoded scalar (a stale proxy) nor a naive median (a TOCTOU efficiency×state blind-multiply) — it is structural_bound(discovered) × efficiency(measured, STATE-STAMPED) × live_state(POLLED at point-of-use), argmin RE-SOLVED per run; the GPU-JEA (jea_cost/jea_navigator/jea_edge_states) + membudget/buildtime are the in-repo instances"
metadata:
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

When a decision hinges on a COST (which engine, which schedule, which strategy), do NOT reach for a
hardcoded scalar or a hand-fed ms table — that is the exact anti-pattern the substrate's cost machinery
exists to KILL. The user redirected me TWICE (2026-07-18) when I proposed a static crossover for the
catalog engine: "look at how jea rides the roofline" then "how per-item costs get calculated and
DYNAMICALLY UPDATED."

**The law (structural-not-scalar, from `jea_edge_states.py`):** every dynamic cost factors as
`achieved = structural_bound × efficiency × live_state`, each layer sourced + re-read at its own cadence:
- **structural_bound** — DISCOVERED from the topology / the item's structure (the ceiling; per-item derived,
  e.g. bytes/nodes). `jea_cost` derives launch_count/W/S/P from the op-graph + `discover()`.
- **efficiency** — MEASURED by a saturating micro-ablation (achieved/structural < 1); the intrinsic rate,
  semi-stable. Persisted analog: `membudget._record_time` → `buildtime` MEDIAN-of-last-K (Ⓟ.proof-cost-ledger).
- **live_state** — POLLED per-window at POINT-OF-USE (contention/thermal/link); volatile, re-read, never baked.

Then the decision is an **argmin over the MEASURED surface, RE-SOLVED each call** ("no stored optimum",
`jea_navigator.navigate`), with the noise floor MEASURED too (not a hardcoded threshold, Δ-A6b) —
"adapts to hardware/conditions for free."

**Why:** a static constant is a stale PROXY of a live measurement (construct-dont-classify #5 — read the
live structure, don't re-derive a proxy). A naive median-of-last-K is worse: it blends efficiency×live_state,
and reusing it later composes two world-states — the **TOCTOU blind-multiply** [[reread-meters-toctou]]
forbids. The fix is to SEPARATE the layers: efficiency state-stamped (÷ the state it was read under), live_state
polled fresh at use. This DISSOLVES a "measurements are confounded by CPU contention" objection — you don't wait
for an idle box, you POLL the contention (live_state) and let it move the operating point.

**How to apply:** before hardcoding any cost/threshold/crossover, factor it: what is the STRUCTURAL bound
(from the item / a discover()), the EFFICIENCY (measured, state-stamped, median-of-K), the LIVE_STATE
(polled at dispatch)? Compute the decision as an argmin re-solved from those; record the measurement back
(self-calibrating). The tell = "let me use ~0.X s per item", "median of the last few runs", "the crossover
is N", "I'll benchmark it once". Relates to [[reread-meters-toctou]], [[read-structure-dont-rebuild]],
[[feedback_measure_instrument_before_theorize]], [[single-source-truth]].
