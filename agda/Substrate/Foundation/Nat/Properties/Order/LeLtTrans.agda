------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.LeLtTrans
--
-- Defines: ≤-<-trans
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.LeLtTrans where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Properties.Order.LeTrans



≤-<-trans : ∀ {m n p} → m ≤ n → n < p → m < p
≤-<-trans m≤n n<p = ≤-trans (s≤s m≤n) n<p
