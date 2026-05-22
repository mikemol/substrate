------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.GcdDividesLeft
--
-- gcd-divides-left : ∀ a b → gcd-ℕ a b ∣ a.
-- Direct projection: take the trace's second projection, apply
-- trace-divides-left.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.GcdDividesLeft where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (proj₂)
open import Substrate.Algebra.Nat.Divides using (_∣_)
open import Substrate.Algebra.Nat.GCD.ComputeTrace using (compute-trace)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.TraceDivides using (trace-divides-left)

gcd-divides-left : ∀ a b → gcd-ℕ a b ∣ a
gcd-divides-left a b = trace-divides-left (proj₂ (compute-trace a b))
