------------------------------------------------------------------------
-- Substrate.Geometry.PG.Type
--
-- The projective space type PG(n, F₂) = (F₂^(n+1) \ {𝟎}) / F₂*.
--
-- In F₂, the projective equivalence (v ~ λv for λ ∈ F₂*) is trivial
-- (only λ = 𝟙 works), so PG n is literally the nonzero subset of
-- F₂^(n+1). Cardinality = 2^(n+1) − 1.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.PG.Type where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Product using (Σ)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (¬_)

open import Substrate.Algebra.F2.Vector

PG : ℕ → Set
PG n = Σ (Vector (suc n)) (λ v → ¬ (v ≡ 𝟎ⱽ))
