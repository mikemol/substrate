------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.OccKTo0
--
-- Defines: occ-k-to-0
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.OccKTo0 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Properties
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.Vector
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
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.OccShiftIter
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.IterK0



-- so occ(p) k ≡ occ(p) 0 for every k.
occ-k-to-0 : ∀ {n} (k j : Fin (suc n)) → occ (suc n) k j ≡ occ (suc n) (zero {n}) j
occ-k-to-0 {n} k j =
  trans (cong (λ z → occ (suc n) z j) (sym (σ-iter-k0 k))) (occ-shift-iter (toℕ k) j)
