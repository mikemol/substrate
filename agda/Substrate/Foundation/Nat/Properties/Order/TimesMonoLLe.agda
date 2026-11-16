------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.TimesMonoLLe
--
-- Defines: *-monoˡ-≤
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.TimesMonoLLe where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Order.PlusMonoRLe



*-monoˡ-≤ : (n : ℕ) {r b : ℕ} → r ≤ b → r * n ≤ b * n
*-monoˡ-≤ n z≤n      = z≤n
*-monoˡ-≤ n (s≤s p)  = +-monoʳ-≤ n (*-monoˡ-≤ n p)
