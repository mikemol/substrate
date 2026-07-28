------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.V4Transitive
--
-- Transitivity of V₄ acting on itself: for any t₁ t₂ : V₄ there
-- exists g with g · t₁ ≡ t₂. The group element doing the work is
-- t₂ · t₁ (since V₄ is self-inverse, t₁⁻¹ = t₁).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.V4Transitive where
open import Substrate.Groups.V4.Axioms.EpsilonRight using (ε-right)
open import Substrate.Groups.V4.Axioms.Assoc using (·-assoc)
open import Substrate.Groups.V4.Operations using (_·_)
open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ)

open import Substrate.Foundation.Product using (_,_; ∃)
open import Substrate.Foundation.Eq using (_≡_)
import Substrate.Groups.V4.Operations as V4

V4-transitive : (t₁ t₂ : V₄) → ∃ λ g → g · t₁ ≡ t₂
V4-transitive e t₂ = t₂ , ε-right t₂
V4-transitive α t₂ = (t₂ · α) , aux
  where
    aux : (t₂ · α) · α ≡ t₂
    aux rewrite ·-assoc t₂ α α = ε-right t₂
V4-transitive β t₂ = (t₂ · β) , aux
  where
    aux : (t₂ · β) · β ≡ t₂
    aux rewrite ·-assoc t₂ β β = ε-right t₂
V4-transitive γ t₂ = (t₂ · γ) , aux
  where
    aux : (t₂ · γ) · γ ≡ t₂
    aux rewrite ·-assoc t₂ γ γ = ε-right t₂
