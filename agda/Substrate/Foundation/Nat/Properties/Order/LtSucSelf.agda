------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.LtSucSelf
--
-- Defines: <-suc-self
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.LtSucSelf where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Order.LeRefl



<-suc-self : (n : ℕ) → n < suc n
<-suc-self n = ≤-refl (suc n)
