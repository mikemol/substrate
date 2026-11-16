---
name: feedback_navigator_not_answer
description: "don't find THE optimal solution (a stored scalar/config); build the NAVIGATOR that recomputes the optimum from the evidence of the moment, with every surface parameter discovered+measured at runtime so it adapts to new hardware/conditions — the optimum is a live-solve OUTPUT, never stored"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

The GOAL is never "find the optimal solution" (a stored number, config, or tuned constant). It is to build the
SYSTEM that finds the optimal solution under the EVIDENCE OF THE MOMENT, and re-solves when the evidence or the
hardware changes. The optimum is a live-solve OUTPUT, not an artifact you compute once and keep. If you catch
yourself "locating the optimum" / "tuning the best K/g/threshold", you have reverted to the static-answer reflex.

Two properties the navigator must have, both by construction:
1. ADAPTS TO CONDITIONS: it re-reads the live evidence (telemetry package) and re-solves per window/event. The
   answer tracks state -- it is never a cached scalar (TOCTOU; [[feedback_reread_meters_toctou]]).
2. ADAPTS TO HARDWARE: every parameter of the cost surface (launch cost, occupancy, edge bounds & efficiencies,
   memory/PCIe bandwidth, thermal trips) is DISCOVERED (topology probe) + MEASURED (micro-ablation) AT RUNTIME on
   whatever box it runs on -- NOT hardcoded. On new hardware the same code yields a different operating point
   with zero edits. A hardcoded constant or a frozen "best config" is the bug.

This is the substrate ethos made operational: recompute-from-residue, never store the answer. It is the same
correction as structural-not-scalar ([[feedback_structural_not_scalar]]: the bound is a live Kron-solve, not a
number), re-read-meters, and never-discard-residue, applied to the OPTIMIZER itself. The engine is one point in
a parameter polytope (the knob surfaces); the navigator = argmin over the joint surface given the current
discovered+measured surfaces and the live evidence package, re-solved continually.

**How to apply:**
- When asked to optimize, build/extend the NAVIGATOR (evidence -> operating point), not a stored optimum. Deliver
  the re-solving function, parameterized by discovered+measured surface params + the live package.
- Never hardcode a surface constant or a winning config. Read it from discovery/ablation at runtime; if you can't
  yet measure it, leave the surface PLUGGABLE and flag it -- don't fabricate or freeze it.
- Validate by SHOWING re-solve: feed two evidence states -> operating point moves; feed two hardware param sets ->
  operating point moves, same code. That is the proof it's a navigator, not an answer.
- The optimum need not be found "permanently" or perfectly; it must be found FRESH from the evidence each time.
