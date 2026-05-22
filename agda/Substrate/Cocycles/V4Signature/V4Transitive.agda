------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.V4Transitive
--
-- Transitivity of V₄ acting on itself: for any t₁ t₂ : V₄ there
-- exists g with g · t₁ ≡ t₂. The group element doing the work is
-- t₂ · t₁ (since V₄ is self-inverse, t₁⁻¹ = t₁).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.V4Transitive where

open import Substrate.Foundation.Product using (_,_; ∃)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)

V4-transitive : (t₁ t₂ : V₄) → ∃ λ g → g V4.· t₁ ≡ t₂
V4-transitive e t₂ = t₂ , V4.ε-right t₂
V4-transitive α t₂ = (t₂ V4.· α) , aux
  where
    aux : (t₂ V4.· α) V4.· α ≡ t₂
    aux rewrite V4.·-assoc t₂ α α = V4.ε-right t₂
V4-transitive β t₂ = (t₂ V4.· β) , aux
  where
    aux : (t₂ V4.· β) V4.· β ≡ t₂
    aux rewrite V4.·-assoc t₂ β β = V4.ε-right t₂
V4-transitive γ t₂ = (t₂ V4.· γ) , aux
  where
    aux : (t₂ V4.· γ) V4.· γ ≡ t₂
    aux rewrite V4.·-assoc t₂ γ γ = V4.ε-right t₂
