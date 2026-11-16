------------------------------------------------------------------------
-- Substrate.WitnessTower.SimplicialBoundary.DelAt
--
-- Defines: delAt
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.SimplicialBoundary; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SimplicialBoundary.DelAt where

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



------------------------------------------------------------------------
-- 1. The i-th face map: delete the vertex at position i (total; an
--    out-of-range position deletes nothing).
------------------------------------------------------------------------

delAt : ℕ → List A → List A
delAt _       []       = []
delAt zero    (_ ∷ xs) = xs
delAt (suc n) (x ∷ xs) = x ∷ delAt n xs
