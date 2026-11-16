------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.LtSucR
--
-- Defines: <-suc-r
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.LtSucR where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Order.LeSucR



<-suc-r : ∀ {m n} → m < n → m < suc n
<-suc-r = ≤-suc-r
