------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Sub.MonusLeSelf
--
-- Defines: ∸-≤-self
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Sub; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Sub.MonusLeSelf where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Order.LeRefl
open import Substrate.Foundation.Nat.Properties.Order.LeSucR



------------------------------------------------------------------------
-- ∸-≤-self : truncated subtraction can only reduce.
------------------------------------------------------------------------

∸-≤-self : (m k : ℕ) → m ∸ k ≤ m
∸-≤-self m       zero    = ≤-refl m
∸-≤-self zero    (suc _) = z≤n
∸-≤-self (suc m) (suc k) = ≤-suc-r (∸-≤-self m k)
