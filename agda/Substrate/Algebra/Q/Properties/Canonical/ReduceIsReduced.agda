------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Canonical.ReduceIsReduced
--
-- Defines: reduce-is-reduced
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.Canonical; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Canonical.ReduceIsReduced where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Reduce
open import Substrate.Algebra.Q.Reduction.AbsInt
open import Substrate.Algebra.Q.Reduction.IsReduced
open import Substrate.Algebra.Q.Reduction.Private
open import Substrate.Algebra.Q.Properties.Abs
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.GCD.GcdN
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft
open import Substrate.Algebra.Nat.GCD.GcdDividesRight
open import Substrate.Algebra.Z.Coprime.CofactorCoprime
open import Substrate.Algebra.Z.Coprime.Private
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Q.Properties.Canonical.ReducedBuild



reduce-is-reduced : (q : ℚ) → is-reduced (reduce q)
reduce-is-reduced q =
  reduced-build (num q) (abs-ℤ (num q)) (den-1 q)
    (gcd-divides-left  (abs-ℤ (num q)) (denominator q))
    (gcd-divides-right (abs-ℤ (num q)) (denominator q))
