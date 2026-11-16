------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.ApplyPowLBasis
--
-- Defines: apply-powL-basis
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.ApplyPowLBasis where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
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



------------------------------------------------------------------------
-- conn2: σ_p^i sends basis k to the orbit position basis(σ-iterate i cyc k).
-- Induction on i, reusing the exposed cyclic-Linear-basis (conn1).
------------------------------------------------------------------------

apply-powL-basis :
  ∀ {n} (i : ℕ) (k : Fin (suc n)) →
  apply (powL i (σ {n})) (basis k) ≡ basis (σ-iterate i (cyclic-suc {n}) k)
apply-powL-basis zero    k = refl
apply-powL-basis (suc i) k =
  trans (cong (apply (σ)) (apply-powL-basis i k))
        (cyclic-Linear-basis (σ-iterate i (cyclic-suc) k))
