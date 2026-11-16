------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Canonical.RatCanonical
--
-- Defines: ℚ-Canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.Canonical; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Canonical.RatCanonical where

open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Equiv
open import Substrate.Algebra.Q.Reduce
open import Substrate.Algebra.Q.Reduction.Private
open import Substrate.Algebra.Q.Properties.Reduce.ApproxReduce
open import Substrate.Algebra.Q.Properties.Reduce.Private
open import Substrate.Algebra.Nat.GCD.CFInvariance.Private
open import Substrate.Algebra.Z.Coprime.Private
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Q.Properties.Canonical.ReduceRespectsApprox



ℚ-Canonical : Canonical ℚ-Quotient
ℚ-Canonical = record
  { canonical            = reduce
  ; canonical-idempotent = λ a → sym (reduce-respects-≈ (≈-reduce a))
  ; canonical-respects-≈ = reduce-respects-≈
  ; ≈-canonical          = ≈-reduce
  }
