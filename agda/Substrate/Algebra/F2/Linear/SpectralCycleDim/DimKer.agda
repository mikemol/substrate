------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.DimKer
--
-- Defines: dim-ker-Φσ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.DimKer where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.KernelSpan
open import Substrate.Algebra.F2.Linear.Augmentation
open import Substrate.Algebra.F2.Linear.SpectralCycle
open import Substrate.Algebra.F2.Linear.Universal
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.KernelDimCong
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.EqA



-- THE GOAL: dim ker Φ_p(σ_p) = p − 1 (= n), the literal-shift presentation.
dim-ker-Φσ : ∀ {n} → KernelDim (Φσ {n}) n
dim-ker-Φσ {n} = KernelDim-cong Φσ≡A (aug-dim n)
