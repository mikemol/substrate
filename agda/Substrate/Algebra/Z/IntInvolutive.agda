------------------------------------------------------------------------
-- Substrate.Algebra.Z.IntInvolutive
--
-- Defines: -ℤ-involutive
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.IntInvolutive where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 5. Double negation: -ℤ (-ℤ z) ≡ z.
------------------------------------------------------------------------

-ℤ-involutive : (z : ℤ) → -ℤ (-ℤ z) ≡ z
-ℤ-involutive (+ zero)  = refl
-ℤ-involutive (+ suc _) = refl
-ℤ-involutive (-suc _)  = refl

------------------------------------------------------------------------
-- 6. Capstone for Q1.
--
-- Substrate-native ℤ with negation ℕ+ decidable equality ℕ+ double-
-- negation involution. Q2 builds ℚ on top.
------------------------------------------------------------------------
