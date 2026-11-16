------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitboundarypairs
--
-- Defines: coemit-boundary-pairs
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitboundarypairs where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.WitnessTower.SimplicialBoundary.DelAt
open import Substrate.WitnessTower.SimplicialBoundary.Len
open import Substrate.WitnessTower.SimplicialBoundary.Private
open import Substrate.WitnessTower.SimplicialBoundary.Simplicial
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitsimplicialidentity
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- the ∂²=0 core (F₂/simplicial pairing): any two nested faces commute (delAt i ∘ delAt (suc j) = delAt j ∘ delAt i),
-- so in ∂∘∂ each 2-face appears twice and cancels over F₂ — reusing the literal simplicial identity (332).
coemit-boundary-pairs : (i j : ℕ) → i ≤ j → (r : RealTrace) (n : ℕ)
                      → delAt i (delAt (suc j) (take n r)) ≡ delAt j (delAt i (take n r))
coemit-boundary-pairs = coemit-simplicial-identity
