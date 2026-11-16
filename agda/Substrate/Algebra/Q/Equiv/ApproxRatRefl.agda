------------------------------------------------------------------------
-- Substrate.Algebra.Q.Equiv.ApproxRatRefl
--
-- Defines: ≈ℚ-refl
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Equiv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Equiv.ApproxRatRefl where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Mul
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Equiv.ApproxRat
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 2. The setoid laws.
------------------------------------------------------------------------

≈ℚ-refl : (a : ℚ) → a ≈ℚ a
≈ℚ-refl a = refl
