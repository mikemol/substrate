------------------------------------------------------------------------
-- Substrate.Category.RuleAction.V4Compose
--
-- _∘V_ : V₄ → V₄ → V₄. Composition table (mirrors
-- eliza/rule_action.py:_V4_COMPOSE). XOR on the two underlying Z/2
-- indices.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction.V4Compose where

open import Substrate.Category.RuleAction.V4 using (V₄; e; α; β; γ)

_∘V_ : V₄ → V₄ → V₄
e ∘V x = x
α ∘V e = α
α ∘V α = e
α ∘V β = γ
α ∘V γ = β
β ∘V e = β
β ∘V α = γ
β ∘V β = e
β ∘V γ = α
γ ∘V e = γ
γ ∘V α = β
γ ∘V β = α
γ ∘V γ = e
