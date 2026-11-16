------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.EqA
--
-- Defines: Φσ≡A
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.EqA where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.Augmentation
open import Substrate.Algebra.F2.Linear.SpectralCycle
open import Substrate.Algebra.F2.Linear.Universal
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.AOnBasis
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.OnBasis



-- Φ_p(σ_p) = A as operators (agree on basis ⟹ everywhere).
Φσ≡A : ∀ {n} (v : Vector (suc n)) → apply (Φσ {n}) v ≡ apply (A {suc n}) v
Φσ≡A {n} = linear-extensionality (Φσ {n}) (A {suc n}) (λ k → trans (Φσ-on-basis k) (sym (A-on-basis k)))
