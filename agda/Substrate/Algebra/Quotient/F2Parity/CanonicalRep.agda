------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.F2Parity.CanonicalRep
--
-- Defines: canonical-rep
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient.F2Parity; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.F2Parity.CanonicalRep where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.Quotient.F2Parity.Preamble



------------------------------------------------------------------------
-- 2. Canonical representative.
--
-- Factor through F₂: `canonical-rep` maps each F₂ element to the
-- chosen ℕ representative (𝟘 ↦ 0, 𝟙 ↦ 1). The full canonical-form
-- function on ℕ is the composite `canonical-rep ∘ parity`.
-- Splitting via a helper keeps Agda's reduction transparent in the
-- idempotence and respect proofs below.
------------------------------------------------------------------------

canonical-rep : F₂ → ℕ
canonical-rep 𝟘 = 0
canonical-rep 𝟙 = 1
