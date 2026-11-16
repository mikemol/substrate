------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.AOnBasis
--
-- Defines: A-on-basis
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.AOnBasis where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.Augmentation
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.TotalBasis



A-on-basis : ∀ {n} (k : Fin (suc n)) → apply (A {suc n}) (basis k) ≡ ones
A-on-basis k = trans (cong (_*ₛ ones) (total-basis k)) (*ₛ-identityˡ ones)
