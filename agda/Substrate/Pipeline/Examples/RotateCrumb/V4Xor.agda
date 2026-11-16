------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.RotateCrumb.V4Xor
--
-- Defines: v4-xor
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Pipeline.Examples.RotateCrumb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples.RotateCrumb.V4Xor where

open import Substrate.Pipeline.Brick
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Eq
open import Substrate.Pipeline.Examples.RotateCrumb.Crumb



-- The Klein four-group acting on crumbs by its regular action (= F₂²-XOR),
-- over the CANONICAL V₄ (Groups.V4) — not a local carrier.
v4-xor : Crumb → V₄ → Crumb
v4-xor c₀ e = c₀ ; v4-xor c₁ e = c₁ ; v4-xor c₂ e = c₂ ; v4-xor c₃ e = c₃
v4-xor c₀ α = c₁ ; v4-xor c₁ α = c₀ ; v4-xor c₂ α = c₃ ; v4-xor c₃ α = c₂
v4-xor c₀ β = c₂ ; v4-xor c₁ β = c₃ ; v4-xor c₂ β = c₀ ; v4-xor c₃ β = c₁
v4-xor c₀ γ = c₃ ; v4-xor c₁ γ = c₂ ; v4-xor c₂ γ = c₁ ; v4-xor c₃ γ = c₀
