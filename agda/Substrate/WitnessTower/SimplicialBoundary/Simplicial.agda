------------------------------------------------------------------------
-- Substrate.WitnessTower.SimplicialBoundary.Simplicial
--
-- Defines: simplicial
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SimplicialBoundary; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SimplicialBoundary.Simplicial where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.Not
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Bool.Properties.XorComm
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans
open import Substrate.WitnessTower.SimplicialBoundary.Private
open import Substrate.WitnessTower.SimplicialBoundary.DelAt



------------------------------------------------------------------------
-- 2. THE SIMPLICIAL IDENTITY (the keystone): for i ≤ j, deleting the later
--    vertex first (at suc j) then the earlier (at i) equals deleting the
--    earlier first (at i) then the later (now shifted down to j).
------------------------------------------------------------------------

simplicial : (i j : ℕ) → i ≤ j → (xs : List A) →
             delAt i (delAt (suc j) xs) ≡ delAt j (delAt i xs)
simplicial i       j       _       []       = refl
simplicial zero    j       _       (x ∷ xs) = refl
simplicial (suc i) (suc j) (s≤s p) (x ∷ xs) = cong (x ∷_) (simplicial i j p xs)
