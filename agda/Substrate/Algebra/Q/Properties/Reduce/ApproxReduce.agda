------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Reduce.ApproxReduce
--
-- Defines: ≈-reduce
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.Reduce; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Reduce.ApproxReduce where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Properties.Mul
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Equiv
open import Substrate.Algebra.Q.Reduce
open import Substrate.Algebra.Q.Reduction.AbsInt
open import Substrate.Algebra.Q.Reduction.Op3
open import Substrate.Algebra.Q.Reduction.Private
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft
open import Substrate.Algebra.Nat.GCD.GcdDividesRight
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.Q.Properties.Reduce.ApproxBuild



≈-reduce : (q : ℚ) → q ≈ℚ reduce q
≈-reduce q =
  ≈-build q (gcd-divides-left  (abs-ℤ (num q)) (denominator q))
            (gcd-divides-right (abs-ℤ (num q)) (denominator q))
