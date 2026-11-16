------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.OnBasis
--
-- Defines: Φσ-on-basis
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.OnBasis where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.Augmentation
open import Substrate.Algebra.F2.Linear.Cyclotomic
open import Substrate.Algebra.F2.Linear.SpectralCycle
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.OrbitCount
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Conn4
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.OnesLookup



-- Φ_p(σ_p)(basis k) ≡ ones (each coordinate is the orbit tally = 𝟙).
Φσ-on-basis : ∀ {n} (k : Fin (suc n)) → apply (Φσ {n}) (basis k) ≡ ones
Φσ-on-basis {n} k =
  ≡-from-lookup _ _ (λ j → trans (trans (orbit-count (suc n) k j) (conn4 k j))
                                 (sym (ones-lookup j)))
