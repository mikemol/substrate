------------------------------------------------------------------------
-- Substrate.Algebra.Q.Reduction.IsReduced
--
-- Defines: is-reduced
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Reduction; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Reduction.IsReduced where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Nat.GCD.GcdN
open import Substrate.Algebra.Q.OneRat
open import Substrate.Algebra.Q.OneRat2
open import Substrate.Algebra.Q.ZeroRat
open import Substrate.Foundation.Eq
open import Substrate.Algebra.Q.Reduction.GcdOfRat



------------------------------------------------------------------------
-- 3. Reduced predicate.
--
-- A ℚ is reduced iff its gcd is 1 (numerator and denominator
-- are coprime).
------------------------------------------------------------------------

is-reduced : ℚ → Set
is-reduced q = gcd-of-ℚ q ≡ 1
