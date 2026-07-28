------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.ADividesLcm
--
-- a-divides-lcm : ∀ a b → a ∣ lcm-ℕ a b. Direct from m∣m*n.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.ADividesLcm where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Algebra.Nat.Divides.Mul using (m∣m*n)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_)
open import Substrate.Algebra.Nat.GCD.LcmN using (lcm-ℕ)

a-divides-lcm : ∀ a b → a ∣ lcm-ℕ a b
a-divides-lcm a b = m∣m*n b
