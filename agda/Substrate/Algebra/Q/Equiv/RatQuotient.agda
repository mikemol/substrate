------------------------------------------------------------------------
-- Substrate.Algebra.Q.Equiv.RatQuotient
--
-- Defines: ℚ-Quotient
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Equiv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Equiv.RatQuotient where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Mul
open import Substrate.Algebra.Z.Properties.MulFull
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Algebra.Q.Equiv.ApproxRat
open import Substrate.Algebra.Q.Equiv.ApproxRatRefl
open import Substrate.Algebra.Q.Equiv.ApproxRatSym
open import Substrate.Algebra.Q.Equiv.ApproxRatTrans



------------------------------------------------------------------------
-- 3. ℚ as a Quotient (reusing Algebra.Quotient).
------------------------------------------------------------------------

ℚ-Quotient : Quotient ℚ _≈ℚ_
ℚ-Quotient = record
  { ≈-refl  = ≈ℚ-refl
  ; ≈-sym   = λ {a} {b}     → ≈ℚ-sym   {a} {b}
  ; ≈-trans = λ {a} {b} {c} → ≈ℚ-trans {a} {b} {c}
  }
