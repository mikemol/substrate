------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.LeSucR
--
-- Defines: ≤-suc-r
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.LeSucR where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat



≤-suc-r : ∀ {m n} → m ≤ n → m ≤ suc n
≤-suc-r z≤n       = z≤n
≤-suc-r (s≤s p)   = s≤s (≤-suc-r p)
