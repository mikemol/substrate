------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.RotateCrumb.ActDot
--
-- Defines: act-∙ᶜ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Pipeline.Examples.RotateCrumb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples.RotateCrumb.ActDot where

open import Substrate.Pipeline.Brick
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Operations
open import Substrate.Foundation.Eq
open import Substrate.Pipeline.Examples.RotateCrumb.Crumb
open import Substrate.Pipeline.Examples.RotateCrumb.V4Xor


act-∙ᶜ : (g h : V₄) (c : Crumb) → v4-xor c (g ·₄ h) ≡ v4-xor (v4-xor c h) g
act-∙ᶜ e e = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ e α = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ e β = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ e γ = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ α e = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ α α = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ α β = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ α γ = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ β e = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ β α = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ β β = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ β γ = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ γ e = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ γ α = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ γ β = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
act-∙ᶜ γ γ = λ { c₀ → refl ; c₁ → refl ; c₂ → refl ; c₃ → refl }
