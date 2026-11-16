------------------------------------------------------------------------
-- Substrate.Algebra.Q.Reduction.Op3
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Reduction; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Reduction.Op3 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Nat.GCD.GcdN
open import Substrate.Algebra.Q.OneRat
open import Substrate.Algebra.Q.OneRat2
open import Substrate.Algebra.Q.ZeroRat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.Q.Reduction.Private
open import Substrate.Algebra.Q.Reduction.GcdOfRat
open import Substrate.Algebra.Q.Reduction.IsReduced
open import Substrate.Algebra.Q.Reduction.Op
open import Substrate.Algebra.Q.Reduction.Op2


_ : is-reduced -1ℚ
_ = refl

------------------------------------------------------------------------
-- 5. Capstone for Q4.
--
-- Reduction predicate + gcd-of-ℚ landed. The full `reduce : ℚ → ℚ` is in
-- Substrate.Algebra.Q.Reduce (NO ℤ-by-ℕ division — the cofactors are the kept
-- gcd-divisibility witnesses); reduced-form uniqueness (the Canonical instance)
-- is in Q.Properties.Canonical. Q5 (Arithmetic) operates on UNREDUCED ℚ; apply
-- reduce for canonical-form comparison.
------------------------------------------------------------------------
