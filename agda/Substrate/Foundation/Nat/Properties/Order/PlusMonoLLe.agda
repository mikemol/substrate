------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.PlusMonoLLe
--
-- Defines: +-monoˡ-≤
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.PlusMonoLLe where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Order.NLemPlusn



+-monoˡ-≤ : (k : ℕ) {m n : ℕ} → m ≤ n → m ℕ+ k ≤ n ℕ+ k
+-monoˡ-≤ k z≤n     = n≤m+n _ k
+-monoˡ-≤ k (s≤s p) = s≤s (+-monoˡ-≤ k p)
