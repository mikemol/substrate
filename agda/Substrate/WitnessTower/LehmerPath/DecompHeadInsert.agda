------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerPath.DecompHeadInsert
--
-- Defines: decomp-head-insert
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerPath; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerPath.DecompHeadInsert where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Enumerate.InsertAt
open import Substrate.WitnessTower.Enumerate.Perm
open import Substrate.WitnessTower.Decompose
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 5. (Ⓣ₁b) The path is UNIQUE: decompose un-does insert-at. The head
--    recovers the choice (refl); the tail recovers the smaller permutation,
--    read straight off `decomp-correct` through `insert-at-inj`.
------------------------------------------------------------------------

decomp-head-insert : ∀ {n} (p : Fin (suc n)) (σ : Perm n) →
                     decomp-head (insert-at p σ) ≡ p
decomp-head-insert p σ = refl
