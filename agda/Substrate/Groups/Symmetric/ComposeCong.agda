------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.ComposeCong
--
-- Composition respects _≈_.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.ComposeCong (A : Set) where

open import Substrate.Foundation.Eq using (cong-trans)
open import Substrate.Groups.Symmetric.Permutation A
open import Substrate.Groups.Symmetric.Eq A using (_≈_)
open import Substrate.Groups.Symmetric.Permutation.Compose A using (_·_)

·-cong :
  {σ₁ σ₂ τ₁ τ₂ : Permutation} →
  σ₁ ≈ σ₂ → τ₁ ≈ τ₂ → (σ₁ · τ₁) ≈ (σ₂ · τ₂)
·-cong {σ₁} {σ₂} {τ₁} {τ₂} σ₁≈σ₂ τ₁≈τ₂ x =
  cong-trans (apply σ₁) (τ₁≈τ₂ x)
             (σ₁≈σ₂ (apply τ₂ x))
