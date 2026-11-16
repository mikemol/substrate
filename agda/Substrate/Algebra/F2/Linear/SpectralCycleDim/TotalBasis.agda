------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.TotalBasis
--
-- Defines: total-basis
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.TotalBasis where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.Augmentation
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Total



total-basis : ∀ {n} (k : Fin n) → total (basis k) ≡ 𝟙
total-basis {suc n} zero    = trans (cong (𝟙 +F_) (total-𝟎 {n})) (+-identityʳ 𝟙)
total-basis {suc n} (suc k) = total-basis k
