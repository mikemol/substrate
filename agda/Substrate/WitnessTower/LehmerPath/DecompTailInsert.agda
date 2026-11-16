------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerPath.DecompTailInsert
--
-- Defines: decomp-tail-insert
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerPath; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerPath.DecompTailInsert where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product
open import Substrate.WitnessTower.Enumerate.InsertAt
open import Substrate.WitnessTower.Enumerate.Perm
open import Substrate.WitnessTower.IsPermutation
open import Substrate.WitnessTower.Decompose
open import Substrate.WitnessTower.DuplicateFree
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym



decomp-tail-insert : ∀ {n} (p : Fin (suc n)) (σ : Perm n)
                     (perm : IsPerm (insert-at p σ)) →
                     decomp-tail (insert-at p σ) perm ≡ σ
decomp-tail-insert p σ perm =
  sym (proj₂ (insert-at-inj (decomp-correct (insert-at p σ) perm)))
