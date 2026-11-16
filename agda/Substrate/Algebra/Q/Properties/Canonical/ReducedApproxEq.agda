------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Canonical.ReducedApproxEq
--
-- Defines: reduced-≈⇒≡
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.Canonical; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Canonical.ReducedApproxEq where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Product
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Equiv
open import Substrate.Algebra.Q.Reduction.AbsInt
open import Substrate.Algebra.Q.Reduction.IsReduced
open import Substrate.Algebra.Q.Reduction.Private
open import Substrate.Algebra.Q.Properties.Uniqueness
open import Substrate.Algebra.Nat.GCD.GcdTrace
open import Substrate.Algebra.Nat.GCD.CFInvariance.Private
open import Substrate.Algebra.Nat.GCD.CFInvariance.ShapeValueInvariance
open import Substrate.Algebra.Nat.GCD.CFInjective.CfInjective
open import Substrate.Foundation.Eq
open import Substrate.Algebra.Polynomial.Graded.Mod



------------------------------------------------------------------------
-- 2. Two REDUCED, ≈ℚ-equal ℚ are propositionally equal (shape uniqueness).
------------------------------------------------------------------------

-- Route 1 (CF shape): the components come from cf-injective on the two coprime
-- traces, compared DIRECTLY (KEYSTONE #1 value-invariance feeds KEYSTONE #2).
reduced-≈⇒≡ : (p q : ℚ) → is-reduced p → is-reduced q → p ≈ℚ q → p ≡ q
reduced-≈⇒≡ p q rp rq pq = uniq-from-mag-den p q (proj₁ inj) (proj₂ inj) pq
  where
    inj : (abs-ℤ (num p) ≡ abs-ℤ (num q)) × (denominator p ≡ denominator q)
    inj = cf-injective
            (coprime-trace (abs-ℤ (num p)) (denominator p) rp)
            (coprime-trace (abs-ℤ (num q)) (denominator q) rq)
            (shape-value-invariance
              (coprime-trace (abs-ℤ (num p)) (denominator p) rp)
              (coprime-trace (abs-ℤ (num q)) (denominator q) rq)
              (s≤s z≤n) (s≤s z≤n) (mag-cross-of-≈ p q pq))
