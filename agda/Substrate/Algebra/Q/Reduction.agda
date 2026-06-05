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
open import Substrate.Algebra.Nat.GCD using (gcd-ℕ)

------------------------------------------------------------------------
-- 1. Absolute value of ℤ.
--
-- Maps + n to n and -suc n to suc n. Always non-negative.
------------------------------------------------------------------------

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

open import Substrate.Algebra.Q using (0ℚ; 1ℚ; -1ℚ)

-- These can be discharged once gcd-ℕ's behaviour at small inputs
-- is verified. The actual proofs would unfold gcd-ℕ; deferred to
-- a follow-up slice that exercises Substrate.Algebra.Nat.GCD's
-- compute-trace at small inputs.

------------------------------------------------------------------------
-- 5. Capstone for Q4.
--
-- Reduction predicate + gcd-of-ℚ landed. The full reduce :
-- ℚ → ℚ function (mapping any ℚ to its reduced form) requires
-- ℤ-by-ℕ division with NonZero handling and lives in a follow-up
-- slice. Q5 (Arithmetic) can operate on UNREDUCED ℚ values; users
-- needing canonical-form comparisons would apply reduce after
-- arithmetic.
------------------------------------------------------------------------
