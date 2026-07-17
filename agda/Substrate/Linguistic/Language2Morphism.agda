------------------------------------------------------------------------
-- Substrate.Linguistic.Language2Morphism
--
-- B1 of the Bicategorical-lift arc per [scratch/bicategorical_arc_plan.md].
--
-- Promotes Y4's `_≈M_` extensional-equality relation to a proper
-- BICATEGORICAL 2-CELL between parallel LanguageMorphisms. A
-- 2-morphism α : f ⇒ g consists of pointwise-equality witnesses
-- on the basis-map and carrier-map components.
--
-- Per [[feedback-categorical-name-first]]: this is the bicategorical
-- 2-cell, the standard categorical name. The substrate's existing
-- Substrate.Category.TwoCategory infrastructure (codec arc) provides
-- the generic primitive; this module specialises to LanguageMorphism.
--
-- B2 + B3 add vertical and horizontal composition; B4 the
-- interchange law; B5 bundles the BicategoryOfLanguages.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Language2Morphism where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.FreeOverBasis
  using (LanguageWitness)
open import Substrate.Linguistic.Morphism
  using (LanguageMorphism; basis-map; carrier-map)

------------------------------------------------------------------------
-- 1. The Language2Morphism record.
--
-- A 2-cell α : f ⇒ g between parallel 1-cells f, g : L₁ → L₂
-- consists of pointwise-equality witnesses on both maps.
------------------------------------------------------------------------

record Language2Morphism
  {B₁ F₁ B₂ F₂ : Set} {L₁ : LanguageWitness B₁ F₁} {L₂ : LanguageWitness B₂ F₂}
  (f g : LanguageMorphism L₁ L₂) : Set where
  constructor mk2Mor
  field
    basis-eq :
      (b : B₁) → basis-map f b ≡ basis-map g b
    carrier-eq :
      (x : F₁) → carrier-map f x ≡ carrier-map g x

open Language2Morphism public

------------------------------------------------------------------------
-- 2. Identity 2-cell.
--
-- For any 1-cell f, the identity 2-cell id-2mor f : f ⇒ f is
-- given by refl on both components.
------------------------------------------------------------------------

id-2mor :
  {B₁ F₁ B₂ F₂ : Set} {L₁ : LanguageWitness B₁ F₁} {L₂ : LanguageWitness B₂ F₂}
  (f : LanguageMorphism L₁ L₂) →
  Language2Morphism f f
id-2mor f = mk2Mor (λ _ → refl) (λ _ → refl)

------------------------------------------------------------------------
-- 3. Capstone for B1.
--
-- 2-morphism record defined; identity supplied. B2 adds vertical
-- composition (α : f⇒g, β : g⇒h ⊢ β ∘V α : f⇒h); B3 adds horizontal.
------------------------------------------------------------------------
