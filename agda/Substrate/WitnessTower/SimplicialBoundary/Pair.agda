------------------------------------------------------------------------
-- Substrate.WitnessTower.SimplicialBoundary.Pair
--
-- Defines: ∂∂-pair
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SimplicialBoundary; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SimplicialBoundary.Pair where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Not
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Bool.Properties.XorComm
open import Substrate.Foundation.Product
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans
open import Substrate.WitnessTower.SimplicialBoundary.Private
open import Substrate.WitnessTower.SimplicialBoundary.DelAt
open import Substrate.WitnessTower.SimplicialBoundary.Simplicial
open import Substrate.WitnessTower.SimplicialBoundary.Osign
open import Substrate.WitnessTower.SimplicialBoundary.OppSign



-- THE KERNEL: for i ≤ j the (suc j, i) and (i, j) routes of ∂∘∂ land on the SAME
-- codim-2 face with OPPOSITE sign — the canceling pair. (`simplicial` + signs.)
∂∂-pair : (i j : ℕ) → i ≤ j → (xs : List A) →
          (delAt i (delAt (suc j) xs) ≡ delAt j (delAt i xs))
        × ((osign (suc j)) xor (osign i) ≡ not ((osign i) xor (osign j)))
∂∂-pair i j i≤j xs = simplicial i j i≤j xs , ∂∂-opp-sign i j
