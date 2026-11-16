------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Canonical.Op
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.Canonical; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Canonical.Op where

open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Equiv
open import Substrate.Algebra.Q.Reduce
open import Substrate.Algebra.Q.Reduction.Op3
open import Substrate.Algebra.Q.Reduction.Private
open import Substrate.Algebra.Q.Properties.Reduce.ApproxReduce
open import Substrate.Algebra.Q.Properties.Reduce.Op3
open import Substrate.Algebra.Q.Properties.Reduce.Private
open import Substrate.Algebra.Nat.GCD.CFInvariance.Private
open import Substrate.Algebra.Z.Coprime.Private
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Q.Properties.Canonical.Private
open import Substrate.Algebra.Q.Properties.Canonical.ReduceRespectsApprox


_ : reduce (mkℚ (+ 2) 3) ≡ reduce (mkℚ (+ 1) 1)
_ = reduce-respects-≈ {mkℚ (+ 2) 3} {mkℚ (+ 1) 1} refl
