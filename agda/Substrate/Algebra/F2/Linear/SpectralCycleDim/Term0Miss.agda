------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.Term0Miss
--
-- Defines: term0-miss
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.Term0Miss where

open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Foundation.Fin.Iterate
open import Substrate.Algebra.Nat.CyclicSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Neq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Iter0ToNat


term0-miss : ∀ {n} (i : ℕ) (j : Fin (suc n)) → i < suc n → toℕ j ≢ i →
             lookup (basis (σ-iterate i (cyclic-suc) (zero {n}))) j ≡ 𝟘
term0-miss i j i<sn neq =
  basis-lookup-other (σ-iterate i (cyclic-suc) zero) j
    (λ e → neq (sym (trans (sym (σ-iter0-toℕ i i<sn)) (cong toℕ e))))
