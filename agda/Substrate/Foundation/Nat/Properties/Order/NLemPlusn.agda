------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Order.NLemPlusn
--
-- Defines: n≤m+n
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Order; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Order.NLemPlusn where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Order.LeSucR
open import Substrate.Foundation.Nat.Properties.Order.LeRefl



n≤m+n : (m n : ℕ) → n ≤ m ℕ+ n
n≤m+n zero    n = ≤-refl n
n≤m+n (suc m) n = ≤-suc-r (n≤m+n m n)
