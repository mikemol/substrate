------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.Op
--
-- Defines: σ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.Op where

open import Substrate.Foundation.Product
import Substrate.Foundation.Product as FP   -- for the ⟡def-eq projection witnesses
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQConfluence.Proj1
open import Substrate.FUSep.FUSepQConfluence.Proj2
open import Substrate.FUSep.FUSepQConfluence.Iso
open import Substrate.FUSep.FUSepQConfluence.RIdx
open import Substrate.FUSep.FUSepQConfluence.PIdx



------------------------------------------------------------------------
-- THE BRAIDING σ : (RIdx ⊗ PIdx) ≅ (PIdx ⊗ RIdx) — the swap, a WedgeIso. This IS
-- confluence: presenting the two indexes reduce-then-peel OR peel-then-reduce are
-- related by a coherent ISO (round-trips to identity). The diamond, categorically.
------------------------------------------------------------------------
σ : Iso (RIdx × PIdx) (PIdx × RIdx)
σ = record
  { fwd     = λ p → proj₂ p , proj₁ p       -- (r , p) ↦ (p , r)
  ; bwd     = λ p → proj₂ p , proj₁ p
  ; bwd∘fwd = λ _ → refl
  ; fwd∘bwd = λ _ → refl
  }
