------------------------------------------------------------------------
-- Substrate.Category.Comonoid.Sites.V4
--
-- Concrete site: V₄ (Klein four-group) as a comonoid.
--
-- V₄'s comonoid structure:
--   comult : V₄ → V₄ × V₄  is the diagonal x ↦ (x, x).
--   counit : V₄ → ⊤        is the unique map to the unit object.
--
-- This is the substrate's foundational comonoid carrier per
-- [[v4-typeclass-architecture]] and [[3plus1-parity-universal]].
-- V₄ shows up throughout the substrate; surfacing it as a comonoid
-- makes it explicitly compatible with Markov-category construction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Comonoid.Sites.V4 where

open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Unit using (⊤; tt)

open import Substrate.Category.Comonoid

------------------------------------------------------------------------
-- V₄ as a 4-element type. Per the substrate's existing Klein-four
-- conventions; here we use a small inductive type rather than
-- importing the existing V4 from Substrate.Algebra to keep this
-- site self-contained.

data V4 : Set where      -- ⟦shape:ceb5c2db e α β γ⟧
  e α β γ : V4

------------------------------------------------------------------------
-- The V₄ comonoid.
--
-- Diagonal comultiplication: x ↦ (x, x).
-- Terminal counit: x ↦ tt.

V4-Comonoid : Comonoid V4 _×_ ⊤
V4-Comonoid = record
  { comult = λ x → (x , x)
  ; counit = λ _ → tt
  }
