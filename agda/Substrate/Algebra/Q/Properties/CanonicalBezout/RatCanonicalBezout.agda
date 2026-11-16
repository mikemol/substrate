------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.CanonicalBezout.RatCanonicalBezout
--
-- Defines: ℚ-Canonical-bezout
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.CanonicalBezout; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.CanonicalBezout.RatCanonicalBezout where

open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Equiv
open import Substrate.Algebra.Q.Reduce
open import Substrate.Algebra.Q.Reduction.Private
open import Substrate.Algebra.Q.Properties.Reduce.ApproxReduce
open import Substrate.Algebra.Q.Properties.Reduce.Private
open import Substrate.Algebra.Q.Properties.Canonical.Op
open import Substrate.Algebra.Q.Properties.Canonical.Private
open import Substrate.Algebra.Q.Properties.Canonical.ReduceIsReduced
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Q.Properties.CanonicalBezout.ReduceRespectsApproxBezout



ℚ-Canonical-bezout : Canonical ℚ-Quotient
ℚ-Canonical-bezout = record
  { canonical            = reduce
  ; canonical-idempotent = λ a → sym (reduce-respects-≈-bezout (≈-reduce a))
  ; canonical-respects-≈ = reduce-respects-≈-bezout
  ; ≈-canonical          = ≈-reduce
  }
