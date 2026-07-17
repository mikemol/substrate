------------------------------------------------------------------------
-- Substrate.Linguistic.CategoryLaws
--
-- Y4 of the Yoneda-lift arc per [scratch/yoneda_lift_arc_plan.md].
--
-- The category laws for LanguageMorphism: associativity, left
-- identity, right identity. Proven up to POINTWISE EXTENSIONAL
-- equality (`_≈M_`) because the η-coherence witness in the
-- morphism record makes naive propositional equality on records
-- too strict (function extensionality would be required, which the
-- substrate avoids per [[feedback-minimize-stdlib-deps]]).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.CategoryLaws where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.FreeOverBasis
  using (LanguageWitness)
open import Substrate.Linguistic.Morphism
  using (LanguageMorphism; basis-map; carrier-map)
open import Substrate.Linguistic.IdMorphism using (id-morphism)
open import Substrate.Linguistic.Compose using (_∘L_)

------------------------------------------------------------------------
-- 1. Pointwise extensional equality on LanguageMorphism.
--
-- Two morphisms are equal iff their basis-maps and carrier-maps
-- agree pointwise. The η-coherence proofs are propositional
-- witnesses and don't need to be compared (proof irrelevance for
-- propositional equality holds at --without-K).
------------------------------------------------------------------------

infix 4 _≈M_

record _≈M_ {B₁ F₁ B₂ F₂ : Set} {L₁ : LanguageWitness B₁ F₁} {L₂ : LanguageWitness B₂ F₂}
  (f g : LanguageMorphism L₁ L₂) : Set where
  field
    basis-≈ :
      (b : B₁) → basis-map f b ≡ basis-map g b
    carrier-≈ :
      (x : F₁) → carrier-map f x ≡ carrier-map g x

open _≈M_ public

------------------------------------------------------------------------
-- 2. Left identity: id-morphism L₂ ∘L f ≈M f.
--
-- The identity precomposed on the right has no effect.
------------------------------------------------------------------------

∘L-identityˡ :
  {B₁ F₁ B₂ F₂ : Set} {L₁ : LanguageWitness B₁ F₁} {L₂ : LanguageWitness B₂ F₂}
  (f : LanguageMorphism L₁ L₂) →
  (id-morphism L₂) ∘L f ≈M f
∘L-identityˡ f = record
  { basis-≈   = λ _ → refl
  ; carrier-≈ = λ _ → refl
  }

------------------------------------------------------------------------
-- 3. Right identity: f ∘L id-morphism L₁ ≈M f.
------------------------------------------------------------------------

∘L-identityʳ :
  {B₁ F₁ B₂ F₂ : Set} {L₁ : LanguageWitness B₁ F₁} {L₂ : LanguageWitness B₂ F₂}
  (f : LanguageMorphism L₁ L₂) →
  f ∘L (id-morphism L₁) ≈M f
∘L-identityʳ f = record
  { basis-≈   = λ _ → refl
  ; carrier-≈ = λ _ → refl
  }

------------------------------------------------------------------------
-- 4. Associativity: (h ∘L g) ∘L f ≈M h ∘L (g ∘L f).
------------------------------------------------------------------------

∘L-assoc :
  {B₁ F₁ B₂ F₂ B₃ F₃ B₄ F₄ : Set}
  {L₁ : LanguageWitness B₁ F₁} {L₂ : LanguageWitness B₂ F₂}
  {L₃ : LanguageWitness B₃ F₃} {L₄ : LanguageWitness B₄ F₄}
  (h : LanguageMorphism L₃ L₄)
  (g : LanguageMorphism L₂ L₃)
  (f : LanguageMorphism L₁ L₂) →
  (h ∘L g) ∘L f ≈M h ∘L (g ∘L f)
∘L-assoc h g f = record
  { basis-≈   = λ _ → refl
  ; carrier-≈ = λ _ → refl
  }

------------------------------------------------------------------------
-- 5. Reflexivity of _≈M_.
------------------------------------------------------------------------

≈M-refl :
  {B₁ F₁ B₂ F₂ : Set} {L₁ : LanguageWitness B₁ F₁} {L₂ : LanguageWitness B₂ F₂}
  {f : LanguageMorphism L₁ L₂} →
  f ≈M f
≈M-refl = record
  { basis-≈   = λ _ → refl
  ; carrier-≈ = λ _ → refl
  }

------------------------------------------------------------------------
-- 6. Capstone for Y4.
--
-- The category laws hold up to _≈M_. The substrate's category-of-
-- languages is well-defined; Y5 packages it.
------------------------------------------------------------------------
