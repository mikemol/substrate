{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.CFMatrixBridge.Properties — the bridge theorems:
-- conv-go's one-step update IS right-mult by M(a) (BRIDGE 1), and one CF step
-- NEGATES the matrix determinant BY the repo's own det-flip (BRIDGE 2, ◆T3=(−1)ⁿ).
-- Split from CFMatrixBridge per def/proof separation (R.Trace.Properties /
-- Nat.Properties.Add imports live here).
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.CFMatrixBridge.Properties where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.R.Trace.Properties using (det4; det-flip)
open import Substrate.Algebra.R.Trace.CFMatrixBridge
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2

-- the matrix's determinant IS the substrate's det4 (definitional).
det-is-det4 : (p₁ q₁ p₀ q₀ : ℕ)
            → detM (state p₁ q₁ p₀ q₀) ≡ det4 p₁ q₁ p₀ q₀
det-is-det4 p₁ q₁ p₀ q₀ = refl

------------------------------------------------------------------------
-- BRIDGE 1 (the matrix identity): conv-go's one-step update IS right-mult by M(a).
------------------------------------------------------------------------
conv-step-is-matmul :
  (a p₁ q₁ p₀ q₀ : ℕ) →
  state (a * p₁ ℕ+ p₀) (a * q₁ ℕ+ q₀) p₁ q₁ ≡ (state p₁ q₁ p₀ q₀) · (M a)
conv-step-is-matmul a p₁ q₁ p₀ q₀ =
  cong₄ mat
    (cong (a * p₁ ℕ+_) (sym (+ℕ-identityʳ p₀)))
    (sym (trans (cong (_ℕ+ zero) (+ℕ-identityʳ p₁)) (+ℕ-identityʳ p₁)))
    (cong (a * q₁ ℕ+_) (sym (+ℕ-identityʳ q₀)))
    (sym (trans (cong (_ℕ+ zero) (+ℕ-identityʳ q₁)) (+ℕ-identityʳ q₁)))
  where
    cong₄ : {A B C E R : Set} (f : A → B → C → E → R)
            {x₁ x₂ : A}{y₁ y₂ : B}{z₁ z₂ : C}{w₁ w₂ : E}
          → x₁ ≡ x₂ → y₁ ≡ y₂ → z₁ ≡ z₂ → w₁ ≡ w₂
          → f x₁ y₁ z₁ w₁ ≡ f x₂ y₂ z₂ w₂
    cong₄ f refl refl refl refl = refl

seed-is-identity : state (suc zero) zero zero (suc zero) ≡ I
seed-is-identity = refl

------------------------------------------------------------------------
-- BRIDGE 2 (the landing): one CF step NEGATES the matrix determinant, BY det-flip.
------------------------------------------------------------------------
matrix-det-flip :
  (a p₁ q₁ p₀ q₀ : ℕ) →
  detM (state (a * p₁ ℕ+ p₀) (a * q₁ ℕ+ q₀) p₁ q₁)
  ≡ -ℤ (detM (state p₁ q₁ p₀ q₀))
matrix-det-flip a p₁ q₁ p₀ q₀ =
  trans (det-is-det4 (a * p₁ ℕ+ p₀) (a * q₁ ℕ+ q₀) p₁ q₁)
        (trans (det-flip a p₁ q₁ p₀ q₀)
               (cong -ℤ_ (sym (det-is-det4 p₁ q₁ p₀ q₀))))
