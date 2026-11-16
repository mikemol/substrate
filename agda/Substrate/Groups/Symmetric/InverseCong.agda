------------------------------------------------------------------------
-- Substrate.Groups.Symmetric.InverseCong
--
-- Inversion respects _≈_.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Symmetric.InverseCong (A : Set) where

open import Substrate.Groups.Symmetric.Permutation A
open import Substrate.Groups.Symmetric.Eq A using (_≈_)
open import Substrate.Groups.Symmetric.Permutation.Inverse A using (_⁻¹)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.SymTrans

⁻¹-cong :
  {σ τ : Permutation} → σ ≈ τ → (σ ⁻¹) ≈ (τ ⁻¹)
⁻¹-cong {σ} {τ} σ≈τ x =
  let step : apply τ (invₐ σ x) ≡ x
      step = sym-trans (σ≈τ (invₐ σ x)) (inv-r σ x)
  in sym-trans (inv-l τ (invₐ σ x)) (cong (invₐ τ) step)
