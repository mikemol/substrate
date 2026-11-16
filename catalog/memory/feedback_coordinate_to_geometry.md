---
name: feedback_coordinate_to_geometry
description: "the project's recurring invariant (shadow-engineered) — every repair replaces a COLLAPSED SCALAR COORDINATE with the GEOMETRY it was summarizing (the F0..F8 ladder); climb under the strictification STOP rule (expand iff the witnesses depend on distinctions the coordinate erases), and refuse to over-climb a faithful coordinate"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

Shadow-engineering the whole arc (carrier, scheduler, layout, oracle/control) recovers ONE invariant object
under all the repairs: **none of them was "better constants" -- each replaced a collapsed COORDINATE with the
GEOMETRY it was summarizing.** The ladder of faces:

  F0 scalar parameter (a fitted coeff / argmin over one coordinate)
  F1 measured SURFACE (cost : object -> ℝ, measured not fitted)            [structural-not-scalar / navigator-not-answer]
  F2 near-optimal REGION (a tie => the coordinate erased a connected patch) [noise-floor-is-a-flat-region]
  F3 SETTLEMENT (equilibrium: every local flip is worse; first variation = 0; each part "earns its keep")
  F4 the HYPERCUBE / combinatorial space the coordinate was a projection of (e.g. partitions = {0,1}^rungs)
  F5 WEIGHTED graph (each edge a measured (gain, overhead) state)
  F6 DYNAMIC graph (the weights move with machine state s: thermal, clock, occupancy, link)               [reread-meters-TOCTOU]
  F7 graph + live STATE solved by Kron/Kirchhoff (the binding constraint EMERGES from the solve, isn't pre-known)
  F8 reactive CONTROL MANIFOLD (the winner is a moving attractor; the navigator tracks it live)

**NO STOP RULE (corrected by the user -- a "climb only if witnesses demand / stop at F0" rule is ITSELF a frozen
judgement).** "Stop here, this coordinate is faithful" asserts the distinction WON'T appear -- which you CANNOT
PROVE (a changed kernel / hardware / mix may make a currently-linear cost non-linear). Freezing an unprovable
"won't" is the exact costly demechanization the arc removes. So: ALWAYS build at the SUBSUMING face (the live
solve over the geometry -- surface / settlement / graph / Kron-solved network). The "faithful coordinate" is the
DEGENERATE OUTPUT of that live solve (a corner / a flat region / a trivial graph), computed LIVE + REACTIVE --
never a baked stop. If conditions later create the distinction, the SAME solve captures it; nothing was frozen.
- The "bloat / over-climb" worry dissolves: build the subsuming solve to DEGENERATE CHEAPLY -- its cost scales
  with the geometry actually PRESENT (pay-for-what-you-use: trivial graph -> trivial solve, flat surface ->
  immediate argmin). You never pay for absent geometry, so there is nothing to "save" by pre-judging it absent.
- STRICTIFICATION reconciled: "smallest face that carries the distinctions" is the OUTPUT of the live solve (it
  returns the minimal structure for the PRESENT distinctions), NOT an offline face-choice. Build maximal, output
  minimal, judge the face NEVER.
- mode/repr were MISLABELED "F0 terminal/baked": they are already a LIVE surface-solve (evaluate the cost model,
  argmin) whose output is currently a corner because the surface is currently linear -- the corner is an OUTPUT,
  not a verdict. The fix is to never CALL them terminal; keep re-solving live.
- judgement-is-demechanization applied honestly: the collapse's benefit (skip a cheap degenerate solve) is ~0;
  its cost (a frozen UNPROVABLE "won't" + lost reactivity) is real => NEVER collapse. Can't prove it won't =>
  don't bake it won't.

This SUBSUMES the five charter memories ([[feedback_structural_not_scalar]], [[feedback_navigator_not_answer]],
[[feedback_noise_floor_is_flat_region]], [[feedback_reread_meters_toctou]], [[feedback_judgement_is_demechanization]])
as facets/rungs of one law.

**How to apply:**
- A scalar measure/decision (fitted constant, argmin over one coordinate) is NEVER the object. Build the
  SUBSUMING live solve over the geometry; let it OUTPUT the minimal structure for the present distinctions. Do
  NOT ask "are the witnesses faithful here, can I stop?" -- you can't prove "won't", so don't bake a stop.
- A run-to-run unstable argmin = the surface is really a region (the live solve returns the region). A "which is
  the bottleneck" that shifts with state = solve the network live (the binding constraint is an OUTPUT).
- The repair is NEVER "tune the constant" and NEVER "judge it faithful and stop". It is "solve the geometry live;
  the corner/region/graph is whatever the solve outputs now." Build the solve to DEGENERATE CHEAPLY (pay only for
  geometry present). (Face-position is a momentary OUTPUT, not a chosen stop: scheduling currently outputs ~surface/
  region, K-window ~surface(monotone-on-gw), layout F3 settlement(+F5 graph as it grows), carrier ~migration
  topology, oracle/navigator the Kron-solved network; mode/repr currently output a corner because their surface
  is currently linear -- re-solved live, NOT terminal, NOT baked. Any of these moves if conditions change.)
