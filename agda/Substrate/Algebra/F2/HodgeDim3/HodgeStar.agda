------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.HodgeStar  (Ⓗ — the n=3 rung of the Hodge ★ generator)
--
-- The Hodge ★ at n=3, k=1 (the cross-product grade): Λ¹(F₂³) ≅ Λ²(F₂³). Built by
-- the SAME generator as HodgeDim4's ★ (Λ²(F₂⁴) ≅ Λ²(F₂⁴)) — namely
-- `basis-permutation-Linear` induced by the 2-blade COMPLEMENT involution on the
-- basis indices — so the two rungs collapse onto one construction rather than
-- two parallel formalizations ([[feedback_expose_generator_not_orbit]],
-- [[feedback_collapse_either_or_before_building]]). The L5 GenericHodgeStar's own
-- header names this as the deferred "cross product on ℝ³" instance; this is its
-- discrete F₂ realization.
--
-- At n=3 the complement is the coordinate REVERSAL on the 3 basis blades. With
-- Λ² ordered (e₁∧e₂, e₁∧e₃, e₂∧e₃) and e_i ↦ the blade NOT involving i:
--   e₁ ↦ e₂∧e₃ (idx 2),  e₂ ↦ e₁∧e₃ (idx 1),  e₃ ↦ e₁∧e₂ (idx 0)
-- i.e. 0↦2, 1↦1, 2↦0. The specific pairing is a basis-order gauge choice (one of
-- the S₃ relabelings, [[feedback_choice_rigidification_in_substrate]]); ★² = id
-- holds for ANY complement involution, so the gauge is not load-bearing for the
-- involution. Unlike HodgeDim4's self-dual middle grade (k = n−k = 2), here
-- k=1 ≠ n−k=2 — the source/target grades differ, but both are dim C(3,k)=3.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.HodgeStar where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Involution using (basis-permutation-involution)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Linear using (basis-permutation-Linear)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)

------------------------------------------------------------------------
-- The 2-blade complement at n=3: e_i ↦ the basis 2-blade NOT involving i.
-- (0↦2, 1↦1, 2↦0 = reversal; an involution.)
------------------------------------------------------------------------

complement-3 : Fin 3 → Fin 3
complement-3 ₀ = ₂
complement-3 ₁ = ₁
complement-3 ₂ = ₀

complement-3-involution : (i : Fin 3) → complement-3 (complement-3 i) ≡ i
complement-3-involution ₀ = refl
complement-3-involution ₁ = refl
complement-3-involution ₂ = refl

------------------------------------------------------------------------
-- Hodge ★ : Λ¹(F₂³) ≅ Λ²(F₂³) as the basis-permutation Linear of complement-3
-- — the SAME construction as HodgeDim4.hodge-star (at n=4).
------------------------------------------------------------------------

hodge-star-3 : Linear 3 3
hodge-star-3 = basis-permutation-Linear complement-3

-- ★² = id on basis blades (one-line application of the universal combinator).
hodge-involution-basis-3 :
  (i : Fin 3) → apply hodge-star-3 (apply hodge-star-3 (basis i)) ≡ basis i
hodge-involution-basis-3 =
  basis-permutation-involution complement-3 complement-3-involution

-- ★² = id on all vectors (linear-extensionality from the basis case).
hodge-involution-3 :
  (v : Vector 3) → apply hodge-star-3 (apply hodge-star-3 v) ≡ v
hodge-involution-3 =
  linear-extensionality (hodge-star-3 ∘L hodge-star-3) id-L hodge-involution-basis-3
