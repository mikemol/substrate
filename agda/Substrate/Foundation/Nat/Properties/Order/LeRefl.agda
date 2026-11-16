------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.LeRefl
--
-- Defines: ≤-refl
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.LeRefl where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat



≤-refl : (n : ℕ) → n ≤ n
≤-refl zero    = z≤n
≤-refl (suc n) = s≤s (≤-refl n)
