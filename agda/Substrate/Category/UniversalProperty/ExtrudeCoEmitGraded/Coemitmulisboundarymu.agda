------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmulisboundarymu
--
-- Defines: coemit-mul-is-boundary-mu
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmulisboundarymu where

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

coemit-mul-is-boundary-mu : (i j : ℕ) → i ≤ j → (r : RealTrace) (n : ℕ)         -- μ-side ∂: simplicial ∂²=0 pairing
                          → delAt i (delAt (suc j) (take n r)) ≡ delAt j (delAt i (take n r))
coemit-mul-is-boundary-mu = coemit-simplicial-identity
