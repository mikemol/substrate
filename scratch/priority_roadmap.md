# Priority roadmap (2026-06-04)

Ordering principle: **leverage** = how many downstream paths an item opens
(load-bearing reach × multipath-enabling), filled **top-down** from the realized
peak. Items within a tier are largely *independent* → fill in parallel.
Backing data: the realizability surface + transitive reach (`audit_import_reach`,
`realizability_surface`) and the SPPF/atlas findings.

## Tier 0 — keystone bridges (highest leverage: land on the center, unify silos)

Each is a `≃`/`WedgeIso` 2-cycle; building it *labels a node* and connects
already-heavily-used objects, so the paths it opens are many.

- **P1. Morphism-carrier bridge** — `Character` / `FieldBond` as instances of
  `FreeOverBasis.η` (the center's unit). Unifies Pontryagin duality + field
  towers + free constructions *through the center* — the most-connected concept
  in the repo. Highest multipath; feasible (a real iso). **Start here.**
- **P2. V₄ atlas** — `≃` 2-cycles among V₄'s 6 presentations (reach 132).
  Connects S4 / Coxeter / F₂² / sites across the group-theory silo. Feasible;
  rich existing material to wire.

## Tier 1 — coverage extension (leverage: one action realizes many)

- **P3. rank-4 × rank-4 wedge-walk** — cross-multiply peak types (`CrossMul`),
  match residues to rank-3 types → covers them (lifts the surface). One walk
  realizes multiple rank-3 objects. Harder (heterogeneous wedge applied).
- **P4. cheap rank-4 atlases** — `F₂≅Bool`, `Word≅List`, `Dec≅(A⊎¬A)`. Trivial
  `≃`s; low individual leverage but they raise the repo's bridge-count from 3
  and exercise the pattern. Parallel with P1/P2.

## Tier 2 — fill the realizability floor (leverage: unblocks arcs built on them)

The rank-1 holes have ~zero *current* reach (nothing depends on a hole), so
their leverage is *potential* — realize the ones an arc is waiting on.

- **P5. term-algebra generic** — collapse `CascadeGen/ConjGen/LensGen/DFTGen…`
  (one motif, many copies) into one generic, as `Coxeter.Cyclic` did for `Zₙ`.
  Multipath: every copy site simplifies.
- **P6. wire the unmeasured operations** — `UniversalEnvelopingAlgebra`,
  `TwoCategory`, `LinearAlgebra`, `Semiring` ops are declared, never called
  (manifest-not-measured). Give each one consumer to realize it.
- **P7. discharge obligation surfaces** — `SubstrateTopos`/`*-stated`,
  `SheafAdjointPair`, the `*Obligation`/`*Theorem` records. ASPIRATIONAL and
  possibly out-of-scope (the topos may be a deliberate stated target, not to be
  proved); lowest priority, per-arc judgement.

## Tier 3 — cleanup (near-zero leverage, cheap, parallel — drain anytime)

- **P8. delete the 7 dead types** (`Fibration`, `LensFunctoriality`, … ) — pure
  subtraction, certified dead by every reaction-kind.
- **P9. drain the import-shape ratchet** — rename the genuine collisions
  (`Axis`, `Section`, `Line`) to `Name⟦shape⟧`; lower `BASELINE` from 90.
- **P10. split false nodes** — the same `Axis`/`Section`/`Step` collisions at
  the declaration (already shape-tagged; renaming is the deeper fix).

## How to fill (multipath)

Tier 0 has THREE independent high-leverage items (P1, P2, P4) → run in parallel.
P1 first by leverage (lands on the center). Tier 3 is cheap and independent of
everything → drain alongside any tier. Don't serialize what's independent;
serialize only where a later item needs an earlier one (P3 wants the atlas
pattern from P1/P2; P7 wants P5/P6 to know what's real).
