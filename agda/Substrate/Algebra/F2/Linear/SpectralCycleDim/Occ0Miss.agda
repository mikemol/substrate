------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ0Miss
--
-- Defines: occ-0-miss
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ0Miss where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.SLesInjective
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Properties
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal
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
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Term0Miss



-- j not yet visited in the first m steps (m ≤ toℕ j).
occ-0-miss : ∀ {n} (m : ℕ) (j : Fin (suc n)) → suc m ≤ suc (toℕ j) → occ m (zero {n}) j ≡ 𝟘
occ-0-miss zero       j _      = refl
occ-0-miss {n} (suc m) j sm≤tj =
  cong₂ _+F_ (occ-0-miss m j (≤-suc-r (s≤s-injective sm≤tj)))
            (term0-miss m j (≤-<-trans (<→≤ (s≤s-injective sm≤tj)) (toℕ-bound j))
              (λ tj≡m → <-irrefl m (subst (suc m ≤_) tj≡m (s≤s-injective sm≤tj))))
