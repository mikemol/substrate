------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.CanonicalBezout.ReduceRespectsApproxBezout
--
-- Defines: reduce-respects-≈-bezout
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.CanonicalBezout; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.CanonicalBezout.ReduceRespectsApproxBezout where

open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Cancel
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
open import Substrate.Algebra.Q.Properties.Canonical.Op
open import Substrate.Algebra.Q.Properties.Canonical.Private
open import Substrate.Algebra.Q.Properties.Canonical.ReduceIsReduced
open import Substrate.Algebra.Nat.Divides.Antisym
open import Substrate.Algebra.Nat.Divides.Mul
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Z.Euclid
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Q.Properties.CanonicalBezout.ReducedApproxEqBezout



------------------------------------------------------------------------
-- The capstone obligation + instance, via the Bézout route. Same reduce,
-- same reduce-is-reduced, same ≈ℚ spine as the shape route.
------------------------------------------------------------------------

reduce-respects-≈-bezout : {a b : ℚ} → a ≈ℚ b → reduce a ≡ reduce b
reduce-respects-≈-bezout {a} {b} hab =
  reduced-≈⇒≡-bezout (reduce a) (reduce b) (reduce-is-reduced a) (reduce-is-reduced b)
    (≈ℚ-trans {reduce a} {a} {reduce b}
       (≈ℚ-sym {a} {reduce a} (≈-reduce a))
       (≈ℚ-trans {a} {b} {reduce b} hab (≈-reduce b)))
