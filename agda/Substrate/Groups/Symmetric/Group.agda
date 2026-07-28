------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.Group
--
-- The symmetric group as a SetoidGroup.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.Group (A : Set) where

open import Substrate.Algebra.SetoidGroup using (SetoidGroup)
open import Substrate.Groups.Symmetric.Permutation A
open import Substrate.Groups.Symmetric.Eq A using (_≈_)
open import Substrate.Groups.Symmetric.EqRefl A using (≈-refl)
open import Substrate.Groups.Symmetric.EqSym A using (≈-sym)
open import Substrate.Groups.Symmetric.EqTrans A using (≈-trans)
open import Substrate.Groups.Symmetric.Permutation.Compose A using (_·_)
open import Substrate.Groups.Symmetric.Identity A using (ε)
open import Substrate.Groups.Symmetric.Permutation.Inverse A using (_⁻¹)
open import Substrate.Groups.Symmetric.Assoc A using (·-assoc)
open import Substrate.Groups.Symmetric.EpsilonLeft A using (ε-left)
open import Substrate.Groups.Symmetric.EpsilonRight A using (ε-right)
open import Substrate.Groups.Symmetric.InvLeft A using (inv-left)
open import Substrate.Groups.Symmetric.InvRight A using (inv-right)
open import Substrate.Groups.Symmetric.ComposeCong A using (·-cong)
open import Substrate.Groups.Symmetric.InverseCong A using (⁻¹-cong)

Symmetric-Group : SetoidGroup Permutation _≈_
Symmetric-Group = record
  { _∙_       = _·_
  ; ε         = ε
  ; _⁻¹       = _⁻¹
  ; ≈-refl    = ≈-refl
  ; ≈-sym     = λ {σ} {τ} → ≈-sym {σ} {τ}
  ; ≈-trans   = λ {σ} {τ} {ρ} → ≈-trans {σ} {τ} {ρ}
  ; ∙-assoc   = ·-assoc
  ; ε-left    = ε-left
  ; ε-right   = ε-right
  ; inv-left  = inv-left
  ; inv-right = inv-right
  ; ∙-cong    = λ {σ₁} {σ₂} {τ₁} {τ₂} → ·-cong {σ₁} {σ₂} {τ₁} {τ₂}
  ; ⁻¹-cong   = λ {σ} {τ} → ⁻¹-cong {σ} {τ}
  }
