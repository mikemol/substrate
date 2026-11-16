------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.LeRefl
--
-- Defines: ≤-refl
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.LeRefl where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.F2.F2



≤-refl : (n : ℕ) → n ≤ n
≤-refl zero    = z≤n
≤-refl (suc n) = s≤s (≤-refl n)
