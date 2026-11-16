------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.OccShift
--
-- Defines: occ-shift
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.OccShift where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.PlusSelfInverse
open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Fin.Iterate
open import Substrate.Algebra.Nat.CyclicSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Neq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.PlusCancelR
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.OccTele



-- shift-invariance: occ(p)(cyclic-suc k) ≡ occ(p) k  (boundary cancels via σ_p^p=id).
occ-shift : ∀ {n} (k j : Fin (suc n)) →
            occ (suc n) (cyclic-suc k) j ≡ occ (suc n) k j
occ-shift {n} k j =
  +-cancelʳ _ _ (lookup (basis k) j)
    (trans (occ-tele (suc n) k j)
           (cong (λ z → occ (suc n) k j +F lookup (basis z) j) (cyclic-suc-HasOrderPerm k)))
