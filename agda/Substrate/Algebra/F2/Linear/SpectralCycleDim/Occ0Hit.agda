------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ0Hit
--
-- Defines: occ-0-hit
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ0Hit where

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
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Term0Hit
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Term0Miss
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Occ0Miss



-- j visited (exactly once) by step m (toℕ j < m ≤ p).
occ-0-hit : ∀ {n} (m : ℕ) (j : Fin (suc n)) → toℕ j < m → m ≤ suc n → occ m (zero {n}) j ≡ 𝟙
occ-0-hit (suc m) j tj<sm sm≤sn with suc (toℕ j) ≤? m
... | yes tj<m =
  trans (cong₂ _+F_ (occ-0-hit m j tj<m (≤-suc-r (s≤s-injective sm≤sn)))
                   (term0-miss m j sm≤sn
                     (λ tj≡m → <-irrefl m (subst (λ x → suc x ≤ m) tj≡m tj<m))))
        (+-identityʳ 𝟙)
... | no ¬tj<m =
  cong₂ _+F_ (occ-0-miss m j (subst (λ x → suc m ≤ suc x) (sym (≤-tight (toℕ j) m tj<sm ¬tj<m)) (≤-refl (suc m))))
            (term0-hit m j sm≤sn (≤-tight (toℕ j) m tj<sm ¬tj<m))
