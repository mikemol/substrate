------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.GcdN
--
-- gcd-ℕ : ℕ → ℕ → ℕ. Extracts the gcd value from compute-trace.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.GcdN where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (proj₁)
open import Substrate.Algebra.Nat.GCD.ComputeTrace using (compute-trace)

gcd-ℕ : ℕ → ℕ → ℕ
gcd-ℕ a b = proj₁ (compute-trace a b)
