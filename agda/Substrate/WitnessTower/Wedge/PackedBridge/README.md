# `PackedBridge` — the binary cell as the F₂ⁿ SHADOW of the witness tower

```
Substrate.WitnessTower.Wedge.PackedBridge

THE INSTANCE (brick 1's goal): the capacity-2 (binary) graded carrier maps
to the witness tower's graded step, via the unified morphism layer
(Algebra.Wedge.Graded.Morphism).

The capacity-2 cell's content is a BINARY distinction (the detector's F₂
outcome / the two seats / the ℤ/2 swap). A sequence of such cell-choices is
`Vec (Fin 2) n` — the binary graded carrier `vec-graded (Fin 2)`. The witness
tower's step is `tower-graded` (recon = `insert-at`, digit `Fin (suc n)`). The
map `packed→witness` is a `GradedDivStrMorphism`: each binary digit picks a
witness insertion `slot`, and `decode` folds `insert-at` — so the cell IS a
component of the witness inductive step, with `respects-recon` holding by REFL.

Group actions: the cell's ℤ/2 (the seat-swap `fin2-swap`, = the detector's
F₂ flip) maps to the witness tower's S₂ slot-swap at grade 1 (`slot {1}` is
the identity, so the binary swap IS the grade-1 slot transposition). The F₂
generator extends to the V₄ = F₂² that debuts at the 3→4 seam
(WitnessTower.KleinCensus.v4-present-at-seam) — the binary cell is the V₄/F₂ⁿ
shadow of the witness tower.

Inherited readout / gluing: `decode` reads a binary digit-sequence as a
permutation; the witness tower's proven Lehmer bijection
(WitnessTower.Sn.enumerate / Decompose) is the gluing, ALWAYS unobstructed
(H¹ = 0) — the dual of the contextuality obstruction
(Algebra.Wedge.Contextuality, H¹ ≠ 0).

Zero postulates, --safe --without-K.
```
