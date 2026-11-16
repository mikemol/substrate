------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.PlusMonoLe
--
-- Defines: +-mono-≤
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.PlusMonoLe where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Order.LeTrans
open import Substrate.Foundation.Nat.Properties.Order.PlusMonoRLe
open import Substrate.Foundation.Nat.Properties.Order.PlusMonoLLe



+-mono-≤ : {m n p q : ℕ} → m ≤ n → p ≤ q → m ℕ+ p ≤ n ℕ+ q
+-mono-≤ {n = n} {p = p} mn pq = ≤-trans (+-monoˡ-≤ p mn) (+-monoʳ-≤ n pq)
