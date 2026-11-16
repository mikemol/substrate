------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.LtIrrefl
--
-- Defines: <-irrefl
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.LtIrrefl where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Empty.Bot



<-irrefl : (n : ℕ) → suc n ≤ n → ⊥
<-irrefl (suc n) (s≤s p) = <-irrefl n p
