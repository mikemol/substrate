------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.RotateCrumb
--
-- Example 1: V₄-rotation of a crumb. Pure transform (S = ⊤).
-- Witnesses D⇒S in the trivial sense.
--
-- ⟡Ⓒ.v4 (2026-07-05): the rotation label is now the substrate's CANONICAL
-- Klein four-group V₄ (Groups.V4), not a local `data V4Label` reinvention,
-- and the crumb rotation is a WITNESSED group action — `crumb-action :
-- Actionᴳ V₄-Group Crumb`, carrying the REAL act-id / act-∙ laws — where the
-- old `record Preserves-V4` was a VACUOUS placeholder (an empty record used as
-- an unproven homomorphism-tag). The action IS the Klein regular action
-- (F₂²-XOR); both laws hold by computation (V₄'s op + ε reduce). The Brick's
-- informational homomorphism-tag now NAMES this genuine action type.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples.RotateCrumb where
open import Substrate.Pipeline.Brick.Witnessing using (D⇒S)
open import Substrate.Pipeline.Brick.Record using (Brick)
open import Substrate.Pipeline.Brick.Unit using (⊤; tt)
open import Substrate.Pipeline.Brick.Type using (BrickType)

open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Pipeline.Brick
open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ)
open import Substrate.Groups.V4.Operations using (_·_)
open import Substrate.Groups.V4.Bundle using (V₄-Group)
open import Substrate.Algebra.GroupAction using (Actionᴳ)

-- Atomic types.
data Crumb : Set where      -- ⟦shape:16b523ba c₀ c₁ c₂ c₃⟧
  c₀ c₁ c₂ c₃ : Crumb

-- The Klein four-group acting on crumbs by its regular action (= F₂²-XOR),
-- over the CANONICAL V₄ (Groups.V4) — not a local carrier.
v4-xor : Crumb → V₄ → Crumb
v4-xor c₀ e = c₀ ; v4-xor c₁ e = c₁ ; v4-xor c₂ e = c₂ ; v4-xor c₃ e = c₃
v4-xor c₀ α = c₁ ; v4-xor c₁ α = c₀ ; v4-xor c₂ α = c₃ ; v4-xor c₃ α = c₂
v4-xor c₀ β = c₂ ; v4-xor c₁ β = c₃ ; v4-xor c₂ β = c₀ ; v4-xor c₃ β = c₁
v4-xor c₀ γ = c₃ ; v4-xor c₁ γ = c₂ ; v4-xor c₂ γ = c₁ ; v4-xor c₃ γ = c₀

-- v4-xor IS a genuine V₄ group action — the real content the old vacuous
-- `Preserves-V4` tag stood in for. Both laws hold by computation (ε reduces to
-- e; V₄'s Coxeter-routed op reduces to a concrete element, so every case is refl).
private
  act-idᶜ : (c : Crumb) → v4-xor c e ≡ c
  act-idᶜ c₀ = refl ; act-idᶜ c₁ = refl ; act-idᶜ c₂ = refl ; act-idᶜ c₃ = refl

  act-∙ᶜ : (g h : V₄) (c : Crumb) → v4-xor c (g · h) ≡ v4-xor (v4-xor c h) g
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

crumb-action : Actionᴳ V₄-Group Crumb
crumb-action = record
  { act    = λ g c → v4-xor c g
  ; act-id = act-idᶜ
  ; act-∙  = act-∙ᶜ
  }

-- ⟡set1-paydown: BrickType edges are now type indices — moved into the annotation; body is the tag.
RotateCrumb-Type : BrickType (Crumb × V₄) Crumb ⊤ ⊤
RotateCrumb-Type = record {}

rotate-crumb : Brick RotateCrumb-Type (Actionᴳ V₄-Group Crumb)
rotate-crumb = record
  { witnesses = D⇒S
  ; step      = λ ((c , g) , _) → v4-xor c g , tt
  }
