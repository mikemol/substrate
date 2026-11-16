------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCycleDim.Term0Hit
--
-- Defines: term0-hit
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Linear.SpectralCycleDim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCycleDim.Term0Hit where

open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Properties
open import Substrate.Foundation.Vec
open import Substrate.Algebra.F2.F2
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
open import Substrate.Foundation.Eq.Neq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.F2.Linear.SpectralCycleDim.Iter0ToNat



term0-hit : ∀ {n} (i : ℕ) (j : Fin (suc n)) → i < suc n → toℕ j ≡ i →
            lookup (basis (σ-iterate i (cyclic-suc) (zero {n}))) j ≡ 𝟙
term0-hit i j i<sn eq =
  trans (cong (λ a → lookup (basis a) j)
              (toℕ-injective (trans (σ-iter0-toℕ i i<sn) (sym eq))))
        (basis-lookup-same j)
