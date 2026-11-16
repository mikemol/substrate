------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.F2Parity.NatparityQuotient
--
-- Defines: ℕ/parity-Quotient
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient.F2Parity; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.F2Parity.NatparityQuotient where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.Quotient.F2Parity.Private
open import Substrate.Algebra.Quotient.F2Parity.Preamble
open import Substrate.Algebra.Quotient.F2Parity.Approx



------------------------------------------------------------------------
-- 4. Quotient +F Canonical instance.
------------------------------------------------------------------------

ℕ/parity-Quotient : Quotient ℕ _≈ₚ_
ℕ/parity-Quotient = record
  { ≈-refl  = λ _ → refl
  ; ≈-sym   = sym
  ; ≈-trans = trans
  }
