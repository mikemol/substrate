------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.PlusMonoRLe
--
-- Defines: +-monoʳ-≤
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.PlusMonoRLe where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus



------------------------------------------------------------------------
-- Monotonicity: right-summand and left-factor preserve ≤.
------------------------------------------------------------------------

+-monoʳ-≤ : (k : ℕ) {m n : ℕ} → m ≤ n → k ℕ+ m ≤ k ℕ+ n
+-monoʳ-≤ zero    p = p
+-monoʳ-≤ (suc k) p = s≤s (+-monoʳ-≤ k p)
