------------------------------------------------------------------------
-- Substrate.Algebra.Q.Reduction.GcdOfRat
--
-- Defines: gcd-of-ℚ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Reduction; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Reduction.GcdOfRat where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Nat.GCD.GcdN
open import Substrate.Algebra.Q.OneRat
open import Substrate.Algebra.Q.OneRat2
open import Substrate.Algebra.Q.ZeroRat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.Q.Reduction.AbsInt



------------------------------------------------------------------------
-- 2. gcd at the ℚ layer.
--
-- gcd-of-ℚ q = gcd(|num q|, denominator q). The denominator is
-- always ≥ 1 by construction (suc den-1).
------------------------------------------------------------------------

gcd-of-ℚ : ℚ → ℕ
gcd-of-ℚ q = gcd-ℕ (abs-ℤ (num q)) (denominator q)
