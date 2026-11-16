------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.F2Parity.CanonicalParityRespects
--
-- Defines: canonical-parity-respects
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient.F2Parity; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.F2Parity.CanonicalParityRespects where

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
open import Substrate.Algebra.Quotient.F2Parity.CanonicalRep
open import Substrate.Algebra.Quotient.F2Parity.CanonicalParity
open import Substrate.Algebra.Quotient.F2Parity.ParityCanonicalRep


canonical-parity-respects :
  {m n : ℕ} → m ≈ₚ n → canonical-parity m ≡ canonical-parity n
canonical-parity-respects eq = cong canonical-rep eq

-- parity n ≡ parity (canonical-parity n) by sym of
-- parity-canonical-rep.
