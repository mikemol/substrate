------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.GcdDividesRight
--
-- gcd-divides-right : ∀ a b → gcd-ℕ a b ∣ b.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.GcdDividesRight where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (proj₂)
open import Substrate.Algebra.Nat.Divides using (_∣_)
open import Substrate.Algebra.Nat.GCD.ComputeTrace using (compute-trace)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.TraceDivides using (trace-divides-right)

gcd-divides-right : ∀ a b → gcd-ℕ a b ∣ b
gcd-divides-right a b = trace-divides-right (proj₂ (compute-trace a b))
