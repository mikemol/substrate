------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Canonical.ReduceRespectsApprox
--
-- Defines: reduce-respects-≈
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.Canonical; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Canonical.ReduceRespectsApprox where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Product
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Equiv
open import Substrate.Algebra.Q.Reduce
open import Substrate.Algebra.Q.Reduction.AbsInt
open import Substrate.Algebra.Q.Reduction.IsReduced
open import Substrate.Algebra.Q.Reduction.Private
open import Substrate.Algebra.Q.Properties.Reduce.ApproxReduce
open import Substrate.Algebra.Q.Properties.Reduce.Private
open import Substrate.Algebra.Q.Properties.Uniqueness
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft
open import Substrate.Algebra.Nat.GCD.GcdDividesRight
open import Substrate.Algebra.Nat.GCD.GcdTrace
open import Substrate.Algebra.Nat.GCD.CFInvariance.Private
open import Substrate.Algebra.Nat.GCD.CFInvariance.ShapeValueInvariance
open import Substrate.Algebra.Nat.GCD.CFInjective.CfInjective
open import Substrate.Algebra.Z.Coprime.Private
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Q.Properties.Canonical.ReduceIsReduced
open import Substrate.Algebra.Q.Properties.Canonical.ReducedApproxEq



------------------------------------------------------------------------
-- 3. The capstone obligation + the instance.
------------------------------------------------------------------------

reduce-respects-≈ : {a b : ℚ} → a ≈ℚ b → reduce a ≡ reduce b
reduce-respects-≈ {a} {b} hab =
  reduced-≈⇒≡ (reduce a) (reduce b) (reduce-is-reduced a) (reduce-is-reduced b)
    (≈ℚ-trans {reduce a} {a} {reduce b}
       (≈ℚ-sym {a} {reduce a} (≈-reduce a))
       (≈ℚ-trans {a} {b} {reduce b} hab (≈-reduce b)))
