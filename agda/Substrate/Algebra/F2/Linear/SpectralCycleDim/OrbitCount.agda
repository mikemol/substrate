------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.OrbitCount
--
-- Defines: orbit-count
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.OrbitCount where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.Cyclotomic
open import Substrate.Algebra.F2.Linear.SpectralCycle
open import Substrate.Foundation.Fin.Iterate
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
open import Substrate.Algebra.Nat.CyclicSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.ApplyPowLBasis
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ



orbit-count :
  ∀ {n} (m : ℕ) (k j : Fin (suc n)) →
  lookup (apply (geomSumL (σ {n}) m) (basis k)) j ≡ occ m k j
orbit-count zero    k j = lookup-𝟎 j
orbit-count (suc m) k j =
  trans (lookup-+ⱽ (apply (geomSumL (σ) m) (basis k)) (apply (powL m (σ)) (basis k)) j)
        (cong₂ _+F_ (orbit-count m k j)
                   (cong (λ w → lookup w j) (apply-powL-basis m k)))
