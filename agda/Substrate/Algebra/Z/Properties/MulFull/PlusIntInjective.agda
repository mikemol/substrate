------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.PlusIntInjective
--
-- Defines: +ℤ-injective
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.PlusIntInjective where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 6. Cancellation by a positive factor, and a factor-swap helper —
--    the algebra cross-multiplication transitivity needs (for ℚ's _≈ℚ_).
------------------------------------------------------------------------

+ℤ-injective  : {j k : ℕ} → (+ j) ≡ (+ k) → j ≡ k
+ℤ-injective refl = refl
