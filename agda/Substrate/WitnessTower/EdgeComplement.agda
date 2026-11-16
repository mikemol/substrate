------------------------------------------------------------------------
-- Substrate.WitnessTower.EdgeComplement
--
-- Defines: ★-edge-is-edge
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.EdgeComplement where

open import Substrate.Foundation.Nat.Nat
-- ⚑ `[]` MUST BE IMPORTED, NOT LEFT TO SHADOW. Omitting it makes `[]` a pattern
-- VARIABLE that shadows `Vec.[]`, so the vector pattern never terminates and every
-- `refl` fails against an unreduced `zipWith … []`. Agda warns
-- (`PatternShadowsConstructor`) but the error it produces points at the refl.
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Algebra.F2.F2
open import Substrate.WitnessTower.FaceSet using (Face; ★)
open import Substrate.Category.UniversalProperty.ExtrudeSKIKFaces using (weight; is-kface)
open import Substrate.Foundation.Eq


------------------------------------------------------------------------
-- ★ SENDS AN EDGE OF Δ³ TO AN EDGE — the self-paired dimension.
--
-- ⚑ THIS IS THE LINK THAT MAKES "V₄ INHABITS THE TOWER" A TERM. The pieces
-- were all present and pointed at each other only in header prose:
--   * `FaceSet.★ S = universe n +ⱽ S`, the wedge RESIDUE, with
--     `wedge-recon : S +ⱽ ★ S ≡ universe n` and `★-involution` proved;
--   * `Cocycles.V4Signature.Pairing.Type` — the three matchings as a datum,
--     bijective to V₄∖{e} (`Pairing↔V4-Nonzero`, both round-trips);
--   * `Algebra.F2.HodgeDim4.Bivector` — `complement : Fin 6 → Fin 6` on the
--     six edges, whose header tabulates exactly three fixed-point-free pairs.
-- Nothing typed the FIRST of those as landing back on edges, so nothing
-- connected the tower's ★ to the matchings at all.
--
-- ⚑ AND Δ³ IS WHERE IT CAN HOLD, FOR A COUNTING REASON. `WitnessTower.Hodge`
-- records the obstruction: the grade-LABEL involution `k ↦ n−k` is clean, but
-- the cell counts are not label-symmetric — Δ³ has 6 edges and 4 faces, so
-- Λ¹ and Λ² are not in bijection and ★ cannot pair an edge with a triangle.
-- What ★ DOES do at n=3 is send a weight-2 face to a weight-2 face: 4 vertices
-- minus 2 chosen leaves 2. Λ¹ is SELF-PAIRED, which is the honest statement,
-- and it is the one the matchings need.
--
-- ⚑ THE DIAGONALIZATION, AT THE CELLS. Choosing an edge out of four vertices
-- forces its complement — 4 = 2 + 2, no second choice — so the matching is
-- produced by the choice rather than consulted. `Axes.EdgePairing.edge-v₄`
-- is the same fact one layer up, in V₄; this is it in F₂ face-space.
--
-- Proved by exhausting the four bits: a `Face 3` is `b₀ ∷ b₁ ∷ b₂ ∷ b₃ ∷ []`,
-- and weight-2 constrains which of the sixteen patterns can occur. Only the
-- six weight-2 cases have a hypothesis to consume; the rest are refuted by the
-- absurd pattern on `is-kface 1`.
------------------------------------------------------------------------

★-edge-is-edge : (f : Face 3) → is-kface 1 f → is-kface 1 (★ f)
-- weight 2: the six edges. Each maps to its complementary edge, weight 2.
★-edge-is-edge (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) _ = refl
★-edge-is-edge (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []) _ = refl
★-edge-is-edge (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []) _ = refl
★-edge-is-edge (𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []) _ = refl
★-edge-is-edge (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []) _ = refl
★-edge-is-edge (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []) _ = refl
-- every other pattern has weight ≠ 2, so `is-kface 1` is uninhabited there.
★-edge-is-edge (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) ()
★-edge-is-edge (𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) ()
★-edge-is-edge (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []) ()
★-edge-is-edge (𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []) ()
★-edge-is-edge (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []) ()
★-edge-is-edge (𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []) ()
★-edge-is-edge (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []) ()
★-edge-is-edge (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ []) ()
★-edge-is-edge (𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []) ()
★-edge-is-edge (𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []) ()
