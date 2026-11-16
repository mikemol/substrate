------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.OccShiftIter
--
-- Defines: occ-shift-iter
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.OccShiftIter where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Fin.Iterate
open import Substrate.Algebra.Nat.CyclicSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.OccShift



-- iterate the shift from 0: occ(p)(σ-iterate m cyc 0) ≡ occ(p) 0.
occ-shift-iter : ∀ {n} (m : ℕ) (j : Fin (suc n)) →
                 occ (suc n) (σ-iterate m (cyclic-suc) (zero {n})) j ≡ occ (suc n) (zero {n}) j
occ-shift-iter zero    j = refl
occ-shift-iter (suc m) j =
  trans (occ-shift (σ-iterate m (cyclic-suc) zero) j) (occ-shift-iter m j)
