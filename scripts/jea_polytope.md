# JEA as a closed n-cell — the strictified architecture (faces = knobs, incidences = bridge-nulls, apex = the limit engine)

Shadow-engineer + strictifier applied to the ~25 silo scripts: they are not 25 things, they are projections
of FACES of one polyhedral object (a cone / n-cell). Recover the invariant (the faces that survived repeated
reinvention), replace narrative with mechanically-checkable axes, compute INCIDENCE. This IS the substrate's
Cone methodology ([[project_cone_subsumes_equalizer_pullback]], the 3+1 cone) one order up, and it IS the
knobs model: the knobs are the coordinate axes (1-faces); the bridge-nulls are the equalizers (where faces
meet); the unified engine is the LIMIT (apex) of the cone whose legs are the faces.

## Faces (the independent structural axes) -- the strictified generators

```
F0 Evaluation   node -> reduce -> residue -> done            the irreducible base 0-cell (every face enriches it)
F1 Carrier      u64 | u128 | byte-limb | trace               how values are represented (predicted by magnitude)
F2 Schedule     stratified | persistent-coop | work-queue    how reduction work is visited
F3 Growth       fixed-DAG | spawn | rewrite | escalation     whether evaluation CREATES new work
F4 Control      K-adapt | telemetry | oracle | dispatch      how scheduling params evolve (a morphism, see below)
F5 Sharing      intern | hash-cons | CSE | memoize           whether structurally-equal nodes collapse
F6 Representation value-window | trace-window                 dual reps of the rational
F7 Resource     occupancy | residency | launch-count | packing   the hardware geometry
F8 Cost         structural factor-signatures | bridge-nulls   the METRIC over all faces (cost is a typed object)
```

KNOBS-MODEL RECONCILIATION: the consolidation audit's genuine knobs {carrier, schedule, mode, K, layout,
repr} = faces {F1, F2, F4(mode=when-to-reduce / F6), F4(K), F7(layout), F6}. The audit COVERED F1,F2,F4,F6,F7
but treated **Growth (F3), Sharing (F5), Cost (F8) as NOT first-class knobs** -- that incompleteness is the
gap the polytope exposes (and why the audit's earlier conclusions were partial).

## Incidence lattice (the strictifier's "compute incidence" -- each meet is a NAMED construct = an equalizer)

```
F1 Carrier  ∩ F3 Growth        = ESCALATION         (overflow creates work -> spawn a wider carrier)   [U3]
F1 Carrier  ∩ F6 Representation= VALUE<->TRACE        (the bridge-null / equalizer; f*=0.5)              [U4]
F1 Carrier  ∩ F7 Resource      = BUCKET-PACKING       (lane width = magnitude; the layout knob)          [U1]
F2 Schedule ∩ F7 Resource      = RESIDENCY/OCCUPANCY  (can the HW keep the graph alive; launch<->occ Pareto) [coop/strat]
F2 Schedule ∩ F3 Growth        = WORK-QUEUE GROWTH    (dynamic schedule needed to spawn; the pool)        [U6]
F3 Growth   ∩ F5 Sharing       = INTERNING            (spawned nodes collapse onto existing; curvature = the 3131x/27594x blowup) [U7]
F4 Control  ∩ F8 Cost          = ORACLE               (telemetry -> schedule, minimizing cost; a morphism, not an evaluator) [M2d]
F4 Control  ∩ F2 Schedule      = K-ADAPTATION          (control steers the schedule window; refill-aware)  [U9]
F8 Cost     ∩ (all)            = the structural cost model (a morphism preserving factor structure; bridge nulls = equalizers) [cost_cotype]
```

A meet that does NOT appear = the faces are independent (no incidence). The realized meets above are the
commuting squares of the cone; an UN-realized meet = an open square = an orphaned fix.

## The missing apex (the one unfinished vertex)

Orphaned fixes 1-3 are NOT three bugs -- they are the TRIPLE MEET seen from three projections:

```
F3 Growth  ∩  F1 Carrier  ∩  F5 Sharing  =  "spawn work, AT THE RIGHT CARRIER, WITHOUT EXPLODING SHARING"
   escalation-delivers (Growth∩Carrier) + interning (Growth∩Sharing) + predict-place routing (Carrier-placement)
```

Why they co-occur: dynamic work production (Growth) WITHOUT delivery + interning + routing EXPLODES -- the
engine generates work faster than it canonicalizes structure. The pool engine (jea_engine_pool) is exactly
this open vertex: it spawns (Growth) but neither delivers a wider carrier, nor interns, nor predict-routes.
This is the highest-leverage consolidation move: ONE brick closing the Growth×Carrier×Sharing vertex, not
three separate re-propagations.

## Closure criterion (what "unified" actually means)

The unified engine = the LIMIT of the cone with legs F0..F8. It is CLOSED (a closed n-cell) iff:
  (1) every face is a genuine degree of freedom (a real knob, not a false one) -- the AUDIT does this;
  (2) every incidence square COMMUTES (every face-meet is realized as its named construct) -- the ORPHANED
      FIXES are the open squares; C5's regression runner asserts all of them = the limit's universal property,
      mechanized.
Today the "unified engine" is ONE FACE of the polytope (the F0-F1-F2 combine+schedule corner), not the apex.
The orphaned fixes point at the missing incidences needed to close the shape.

## Revised C-arc (driven by the geometry, not the file list)

- **C3-apex (NEW, highest leverage):** close the Growth×Carrier×Sharing vertex in the pool engine -- spawn
  routes to the predicted carrier tier (predict-place, F1∩F3), delivers byte-limb (escalation-delivers,
  F1∩F3 top element), and interns spawned nodes (F3∩F5). Fixes 1-3 as ONE vertex. Supersedes "re-propagate
  3 fixes separately."
- **C4:** Control∩Cost as a stage -- the oracle (morphism telemetry->schedule) + the STRUCTURAL cost model
  (F8, cost_cotype factor-signatures; NOT hand-fed ms) wired in. Closes the Control/Cost squares.
- **C5:** the regression runner = the universal-property check: every prior witness AND every incidence
  (orphaned fix) passes via the ONE engine. Only then is the n-cell closed and "unified" honest.
- Residency-assert (F2∩F7) and three-state-witness fold into C4/C5 as square-closures.

LESSON (why the silos): each script explored ONE face; the repo kept "rediscovering the same thing" because
the faces are projections of one object. The unified engine isn't the center yet -- it's one face. Close the
incidences (esp. the missing vertex) to reach the apex. Ground every face/meet on the CURRENT code +
structure, never remembered history ([[feedback_silo_sprawl_orphans_fixes]]).
