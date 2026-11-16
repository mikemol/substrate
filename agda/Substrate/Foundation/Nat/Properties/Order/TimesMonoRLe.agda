------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.TimesMonoRLe
--
-- Defines: *-monoʳ-≤
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.TimesMonoRLe where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Order.PlusMonoLe



*-monoʳ-≤ : (n : ℕ) {r b : ℕ} → r ≤ b → n * r ≤ n * b
*-monoʳ-≤ zero    p = z≤n
*-monoʳ-≤ (suc n) p = +-mono-≤ p (*-monoʳ-≤ n p)
