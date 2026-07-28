------------------------------------------------------------------------
-- Substrate.Algebra.Q.Reduction
--
-- Q4 of the constructive ℚ arc per [scratch/q_arc_plan.md].
--
-- Reduction predicate for ℚ. A rational p/q is REDUCED iff
-- gcd(|p|, q) = 1 (numerator and denominator are coprime).
--
-- Uses substrate-native Substrate.Algebra.Nat.GCD.gcd-ℕ.
--
-- UPDATE: the full reduction function `reduce : ℚ → ℚ` is LANDED in
-- Substrate.Algebra.Q.Reduce (with soundness q ≈ℚ reduce q in
-- Q.Properties.Reduce). It needs NO new ℤ÷ℕ division — the cofactors num/gcd
-- and den/gcd are the witness quotients already kept by gcd-divides-left/right
-- ("we never discard residue"). The earlier "deferred — needs NonZero ℤ÷ℕ"
-- framing was a forgotten residue, not a missing algorithm.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Reduction where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.Z using (ℤ; +_; -suc_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; denominator)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)

------------------------------------------------------------------------
-- 1. Absolute value of ℤ.
--
-- Maps + n to n and -suc n to suc n. Always non-negative.
------------------------------------------------------------------------

open import Substrate.Algebra.Q using (0ℚ; 1ℚ; -1ℚ)
abs-ℤ : ℤ → ℕ
abs-ℤ (+ n)    = n
abs-ℤ (-suc n) = suc n

------------------------------------------------------------------------
-- 2. gcd at the ℚ layer.
--
-- gcd-of-ℚ q = gcd(|num q|, denominator q). The denominator is
-- always ≥ 1 by construction (suc den-1).
------------------------------------------------------------------------

gcd-of-ℚ : ℚ → ℕ
gcd-of-ℚ q = gcd-ℕ (abs-ℤ (num q)) (denominator q)

------------------------------------------------------------------------
-- 3. Reduced predicate.
--
-- A ℚ is reduced iff its gcd is 1 (numerator and denominator
-- are coprime).
------------------------------------------------------------------------

is-reduced : ℚ → Set
is-reduced q = gcd-of-ℚ q ≡ 1

------------------------------------------------------------------------
-- 4. Worked examples: ℚ values that are trivially reduced.
--
-- 0/1 has gcd(0, 1) = 1 (any number divides 0; gcd with 1 is 1).
-- ±1/1 similarly.
------------------------------------------------------------------------


private
  -- gcd-ℕ at small closed inputs computes; the Q4-deferred oracles now
  -- discharge by refl (gcd(0,1) = gcd(1,1) = 1).
  _ : is-reduced 0ℚ
  _ = refl
  _ : is-reduced 1ℚ
  _ = refl
  _ : is-reduced -1ℚ
  _ = refl

------------------------------------------------------------------------
-- 5. Capstone for Q4.
--
-- Reduction predicate + gcd-of-ℚ landed. The full `reduce : ℚ → ℚ` is in
-- Substrate.Algebra.Q.Reduce (NO ℤ-by-ℕ division — the cofactors are the kept
-- gcd-divisibility witnesses); reduced-form uniqueness (the Canonical instance)
-- is in Q.Properties.Canonical. Q5 (Arithmetic) operates on UNREDUCED ℚ; apply
-- reduce for canonical-form comparison.
------------------------------------------------------------------------
