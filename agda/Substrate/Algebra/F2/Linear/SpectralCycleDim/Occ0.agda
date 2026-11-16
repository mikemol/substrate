------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ0
--
-- Defines: occ-0
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ0 where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Le2
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.SLesInjective
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Properties
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Negation.Dec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.Vector
open import Substrate.Foundation.Fin.Iterate
open import Substrate.Algebra.Nat.CyclicSuc
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ0Hit



occ-0 : ∀ {n} (j : Fin (suc n)) → occ (suc n) (zero {n}) j ≡ 𝟙
occ-0 {n} j = occ-0-hit (suc n) j (toℕ-bound j) (≤-refl (suc n))
