------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.BDividesLcm
--
-- b-divides-lcm : ∀ a b → b ∣ lcm-ℕ a b. Direct from n∣m*n.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.BDividesLcm where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Algebra.Nat.Divides using (_∣_; n∣m*n)
open import Substrate.Algebra.Nat.GCD.LcmN using (lcm-ℕ)

b-divides-lcm : ∀ a b → b ∣ lcm-ℕ a b
b-divides-lcm a b = n∣m*n a
