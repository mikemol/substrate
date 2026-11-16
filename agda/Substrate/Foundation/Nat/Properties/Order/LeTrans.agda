------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.LeTrans
--
-- Defines: ≤-trans
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.LeTrans where

open import Substrate.Foundation.Nat.Le



------------------------------------------------------------------------
-- ≤-trans / ≤-<-trans : transitivity of ≤ (and the mixed variant).
------------------------------------------------------------------------

≤-trans : ∀ {m n p} → m ≤ n → n ≤ p → m ≤ p
≤-trans z≤n        _         = z≤n
≤-trans (s≤s m≤n)  (s≤s n≤p) = s≤s (≤-trans m≤n n≤p)
