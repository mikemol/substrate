------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.MLemPlusn
--
-- Defines: m≤m+n
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.MLemPlusn where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus



------------------------------------------------------------------------
-- Additive order: a summand is ≤ the sum. (The chirality pair.)
------------------------------------------------------------------------

m≤m+n : (m n : ℕ) → m ≤ m ℕ+ n
m≤m+n zero    n = z≤n
m≤m+n (suc m) n = s≤s (m≤m+n m n)
