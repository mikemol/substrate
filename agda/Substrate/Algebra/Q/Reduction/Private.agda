------------------------------------------------------------------------
-- Substrate.Algebra.Q.Reduction.Private
--
-- Defines: Private
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Reduction; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Reduction.Private where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Nat.GCD.GcdN
open import Substrate.Algebra.Q.OneRat
open import Substrate.Algebra.Q.OneRat2
open import Substrate.Algebra.Q.ZeroRat
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 4. Worked examples: ℚ values that are trivially reduced.
--
-- 0/1 has gcd(0, 1) = 1 (any number divides 0; gcd with 1 is 1).
-- ±1/1 similarly.
------------------------------------------------------------------------


-- gcd-ℕ at small closed inputs computes; the Q4-deferred oracles now
-- discharge by refl (gcd(0,1) = gcd(1,1) = 1).
