------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Canonical.ReducedBuild
--
-- Defines: reduced-build
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.Canonical; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Canonical.ReducedBuild where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Reduce
open import Substrate.Algebra.Q.Reduction.AbsInt
open import Substrate.Algebra.Q.Reduction.Private
open import Substrate.Algebra.Q.Properties.Abs
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.GCD.GcdN
open import Substrate.Algebra.Z.Coprime.CofactorCoprime
open import Substrate.Algebra.Z.Coprime.Private
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst



------------------------------------------------------------------------
-- 1. reduce produces a reduced fraction (cofactor coprimality, lifted to ℚ).
--    Worker over reduce-build's witnesses (so it reduces transparently).
------------------------------------------------------------------------

reduced-build :
  (sgn : ℤ) (na d : ℕ)
  (dl : gcd-ℕ na (suc d) ∣ na) (dr : gcd-ℕ na (suc d) ∣ suc d) →
  gcd-ℕ (abs-ℤ (num (reduce-build sgn dl dr))) (denominator (reduce-build sgn dl dr)) ≡ 1
reduced-build sgn na d (divides qn eqn) (divides (suc qd′) eqd) =
  subst (λ x → gcd-ℕ x (suc qd′) ≡ 1) (sym (abs-sign-of sgn qn))
        (cofactor-coprime na d qn (suc qd′) eqn eqd)
reduced-build sgn na d (divides qn eqn) (divides zero ())
