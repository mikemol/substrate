------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.F2Parity.NatparityCanonical
--
-- Defines: ℕ/parity-Canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient.F2Parity; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.F2Parity.NatparityCanonical where

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
open import Substrate.Algebra.Quotient.F2Parity.CanonicalParity
open import Substrate.Algebra.Quotient.F2Parity.CanonicalParityIdem
open import Substrate.Algebra.Quotient.F2Parity.CanonicalParityRespects
open import Substrate.Algebra.Quotient.F2Parity.ApproxCanonical
open import Substrate.Algebra.Quotient.F2Parity.NatparityQuotient



ℕ/parity-Canonical : Canonical ℕ/parity-Quotient
ℕ/parity-Canonical = record
  { canonical            = canonical-parity
  ; canonical-idempotent = canonical-parity-idem
  ; canonical-respects-≈ = λ {m} {n} eq → canonical-parity-respects {m} {n} eq
  ; ≈-canonical          = ≈ₚ-canonical
  }

------------------------------------------------------------------------
-- 5. Capstone for QU6.
--
-- ℕ / ≈ₚ ≅ F₂ as a Quotient +F Canonical instance. The canonical
-- form picks the 2-element {0, 1} ⊂ ℕ as class representatives,
-- matching the 3+1 parity universal at the ℕ-level.
------------------------------------------------------------------------
