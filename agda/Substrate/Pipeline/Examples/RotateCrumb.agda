------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.RotateCrumb
--
-- Example 1: V₄-rotation of a crumb. Pure transform (S = ⊤).
-- Witnesses D⇒S in the trivial sense; homomorphism preserves the
-- V₄ group action table.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples.RotateCrumb where

open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Pipeline.Brick

-- Atomic types.
data Crumb : Set where
  c₀ c₁ c₂ c₃ : Crumb

data V4Label : Set where
  e α β γ : V4Label

-- The V₄ XOR action (Klein four group).
v4-xor : Crumb → V4Label → Crumb
v4-xor c₀ e = c₀ ; v4-xor c₁ e = c₁ ; v4-xor c₂ e = c₂ ; v4-xor c₃ e = c₃
v4-xor c₀ α = c₁ ; v4-xor c₁ α = c₀ ; v4-xor c₂ α = c₃ ; v4-xor c₃ α = c₂
v4-xor c₀ β = c₂ ; v4-xor c₁ β = c₃ ; v4-xor c₂ β = c₀ ; v4-xor c₃ β = c₁
v4-xor c₀ γ = c₃ ; v4-xor c₁ γ = c₂ ; v4-xor c₂ γ = c₁ ; v4-xor c₃ γ = c₀

RotateCrumb-Type : BrickType
RotateCrumb-Type = record
  { D-in  = Crumb × V4Label
  ; D-out = Crumb
  ; S-in  = ⊤
  ; S-out = ⊤
  }

record Preserves-V4 : Set where

rotate-crumb : Brick RotateCrumb-Type
rotate-crumb = record
  { witnesses = D⇒S
  ; step      = λ ((c , g) , _) → v4-xor c g , tt
  ; homomorphism-tag = Preserves-V4
  }
