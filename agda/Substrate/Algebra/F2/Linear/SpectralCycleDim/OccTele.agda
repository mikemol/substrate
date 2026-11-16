------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.OccTele
--
-- Defines: occ-tele
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.OccTele where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusComm
open import Substrate.Algebra.F2.PlusF
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
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.PlusSwapMid
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.IterCyc



-- telescoping: Σ_{i<m} T(suc i) +F T 0 ≡ Σ_{i<m} T i +F T m  (T i = lookup(basis(σⁱk)) j).
occ-tele : ∀ {n} (m : ℕ) (k j : Fin (suc n)) →
           (occ m (cyclic-suc k) j +F lookup (basis k) j)
             ≡ (occ m k j +F lookup (basis (σ-iterate m (cyclic-suc) k)) j)
occ-tele zero    k j = refl
occ-tele (suc m) k j =
  trans (cong (λ z → (occ m (cyclic-suc k) j +F lookup (basis z) j) +F lookup (basis k) j)
              (σ-iter-cyc m k))
  (trans (+-swap-mid (occ m (cyclic-suc k) j)
                     (lookup (basis (σ-iterate (suc m) (cyclic-suc) k)) j)
                     (lookup (basis k) j))
         (cong (_+F lookup (basis (σ-iterate (suc m) (cyclic-suc) k)) j) (occ-tele m k j)))
