------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.KernelDimCong
--
-- Defines: KernelDim-cong
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.KernelDimCong where

open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.KernelSpan
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym



------------------------------------------------------------------------
-- Transport: pointwise-equal operators share their KernelDim. (Generic;
-- the dimension of a kernel depends on the operator only through inKer.)
------------------------------------------------------------------------

KernelDim-cong :
  ∀ {n m} {L L′ : Linear n m} {d} →
  ((v : Vector n) → apply L v ≡ apply L′ v) →
  KernelDim L′ d → KernelDim L d
KernelDim-cong {L = L} {L′} eq KD = record
  { into     = KernelDim.into KD
  ; retract  = KernelDim.retract KD
  ; into-ker = λ x → trans (eq (apply (KernelDim.into KD) x)) (KernelDim.into-ker KD x)
  ; indep    = KernelDim.indep KD
  ; spans    = λ v h → KernelDim.spans KD v (trans (sym (eq v)) h)
  }
