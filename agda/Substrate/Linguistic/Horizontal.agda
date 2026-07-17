------------------------------------------------------------------------
-- Substrate.Linguistic.Horizontal
--
-- B3 of the Bicategorical-lift arc per [scratch/bicategorical_arc_plan.md].
--
-- Horizontal composition of 2-morphisms: given α : f ⇒ g (at
-- L₁ → L₂) and β : h ⇒ k (at L₂ → L₃), produce β ∘H α : (h ∘L f)
-- ⇒ (k ∘L g) at L₁ → L₃.
--
-- Each component is built by combining the input 2-cells with
-- congruence: basis-eq uses cong on the outer (h-side) basis-map,
-- chained with the inner β-equality at the propagated argument.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Horizontal where

open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

open import Substrate.Category.FreeOverBasis using (LanguageWitness)
open import Substrate.Linguistic.Morphism
  using (LanguageMorphism; basis-map; carrier-map)
open import Substrate.Linguistic.Compose using (_∘L_)
open import Substrate.Linguistic.Language2Morphism
  using (Language2Morphism; mk2Mor; basis-eq; carrier-eq)

------------------------------------------------------------------------
-- 1. Horizontal composition.
--
-- α : f ⇒ g (at L₁ → L₂); β : h ⇒ k (at L₂ → L₃). Result:
-- β ∘H α : (h ∘L f) ⇒ (k ∘L g) at L₁ → L₃.
------------------------------------------------------------------------

infixr 9 _∘H_

_∘H_ :
  {B₁ F₁ B₂ F₂ B₃ F₃ : Set}
  {L₁ : LanguageWitness B₁ F₁} {L₂ : LanguageWitness B₂ F₂} {L₃ : LanguageWitness B₃ F₃}
  {f g : LanguageMorphism L₁ L₂}
  {h k : LanguageMorphism L₂ L₃} →
  Language2Morphism h k →
  Language2Morphism f g →
  Language2Morphism (h ∘L f) (k ∘L g)
_∘H_ {f = f} {g = g} {h = h} {k = k} β α = mk2Mor
  (λ b →
    trans
      (cong (basis-map h) (basis-eq α b))
      (basis-eq β (basis-map g b)))
  (λ x →
    trans
      (cong (carrier-map h) (carrier-eq α x))
      (carrier-eq β (carrier-map g x)))

------------------------------------------------------------------------
-- 2. Capstone for B3.
--
-- Horizontal composition is defined. B4 proves the INTERCHANGE
-- LAW relating vertical and horizontal composition; B5 bundles
-- the whole bicategorical structure.
------------------------------------------------------------------------
