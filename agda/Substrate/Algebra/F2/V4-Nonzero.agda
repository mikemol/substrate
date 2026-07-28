------------------------------------------------------------------------
-- Substrate.Algebra.F2.V4-Nonzero
--
-- N-2 of the M-12 DBE plan. The 3 nonzero vectors of F₂² as a
-- structural type, identified by their Fin 3 position with a coords
-- map to Vector 2.
--
-- Structural meaning: V₄'s 3 non-identity elements live here as the
-- F₂² \ {𝟎} subset. The choice of identification is fixed once and
-- documented as a convention (per [[feedback_ordering_is_chirality_choice]]):
--
--   v4nz-α = (𝟙, 𝟘)     ← first axis, α-pair = {D,C}|{S,W}
--   v4nz-β = (𝟘, 𝟙)     ← second axis, β-pair = {D,S}|{C,W}
--   v4nz-γ = (𝟙, 𝟙)     ← α + β, γ-pair = {D,W}|{C,S}
--
-- The relation `vec-α +ⱽ vec-β ≡ vec-γ` captures the V₄ group
-- structure on the nonzero F₂² elements (V₄ ≅ F₂² as additive group).
--
-- Mirrors the Fano (M-9) / Hamming (M-7) pattern: `Fin k` for the
-- positional axis + a coords dispatcher into `Vector m`. Pattern-
-- matching on a Fin 3 inhabitant is cleaner than carrying a Σ-type
-- proof component (Angle B in the M-12 plan).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.V4-Nonzero where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₂)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector

------------------------------------------------------------------------
-- The positional type.
------------------------------------------------------------------------

V4-Nonzero : Set
V4-Nonzero = Fin 3

------------------------------------------------------------------------
-- The 3 nonzero F₂² vectors.
------------------------------------------------------------------------

vec-α vec-β vec-γ : Vector 2
vec-α = 𝟙 ∷ 𝟘 ∷ []
vec-β = 𝟘 ∷ 𝟙 ∷ []
vec-γ = 𝟙 ∷ 𝟙 ∷ []

------------------------------------------------------------------------
-- Convenience names for the 3 positions.
------------------------------------------------------------------------

v4nz-α v4nz-β v4nz-γ : V4-Nonzero
v4nz-α = zero
v4nz-β = suc zero
v4nz-γ = suc (suc zero)

------------------------------------------------------------------------
-- The coordinates dispatcher.
--
-- Maps each Fin 3 position to its nonzero F₂² vector. The ₂
-- catch-all is forced by Fin 3's structure: the only remaining
-- inhabitant after `zero` and `suc zero` is `suc (suc zero)`.
------------------------------------------------------------------------

coords : V4-Nonzero → Vector 2
coords zero                = vec-α
coords (suc zero)          = vec-β
coords ₂       = vec-γ

------------------------------------------------------------------------
-- The defining F₂-linear relation: α + β = γ.
--
-- This captures V₄ ≅ F₂² as an additive group: the three nonzero
-- elements are closed under XOR up to the V₄ multiplication table.
-- Closes by `refl` since `+ⱽ` is componentwise F₂ addition.
------------------------------------------------------------------------

α+β≡γ : coords v4nz-α +ⱽ coords v4nz-β ≡ coords v4nz-γ
α+β≡γ = refl

α+γ≡β : coords v4nz-α +ⱽ coords v4nz-γ ≡ coords v4nz-β
α+γ≡β = refl

β+γ≡α : coords v4nz-β +ⱽ coords v4nz-γ ≡ coords v4nz-α
β+γ≡α = refl

------------------------------------------------------------------------
-- Self-cancellation: each nonzero element XOR'd with itself is 𝟎ⱽ.
--
-- The V₄ self-inverse property in additive (F₂-linear) form.
------------------------------------------------------------------------

α+α≡𝟎 : coords v4nz-α +ⱽ coords v4nz-α ≡ 𝟎ⱽ
α+α≡𝟎 = refl

β+β≡𝟎 : coords v4nz-β +ⱽ coords v4nz-β ≡ 𝟎ⱽ
β+β≡𝟎 = refl

γ+γ≡𝟎 : coords v4nz-γ +ⱽ coords v4nz-γ ≡ 𝟎ⱽ
γ+γ≡𝟎 = refl
