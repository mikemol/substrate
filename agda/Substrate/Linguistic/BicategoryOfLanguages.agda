------------------------------------------------------------------------
-- Substrate.Linguistic.BicategoryOfLanguages
--
-- B5 of the Bicategorical-lift arc per [scratch/bicategorical_arc_plan.md].
--
-- The bicategorical bundle: objects (LanguageWitness) + 1-morphisms
-- (LanguageMorphism) + 2-morphisms (Language2Morphism) + vertical
-- + horizontal composition + identities. Generalises Y5's
-- CategoryOfLanguages by adding the 2-cell layer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.BicategoryOfLanguages where

open import Substrate.Category.FreeOverBasis using (LanguageWitness)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.IdMorphism using (id-morphism)
open import Substrate.Linguistic.Compose using (_∘L_)
open import Substrate.Linguistic.Language2Morphism
  using (Language2Morphism; id-2mor)
open import Substrate.Linguistic.Vertical using (_∘V_)
open import Substrate.Linguistic.Horizontal using (_∘H_)

------------------------------------------------------------------------
-- 1. The BicategoryOfLanguages record.
------------------------------------------------------------------------

record BicategoryOfLanguages : Set₂ where
  field
    -- Object layer
    Object : Set₁
    -- 1-morphism layer
    OneCell : Object → Object → Set
    -- 2-morphism layer
    TwoCell :
      {L₁ L₂ : Object} → OneCell L₁ L₂ → OneCell L₁ L₂ → Set
    -- 1-identity
    Id-1 : (L : Object) → OneCell L L
    -- 1-composition
    Compose-1 :
      {L₁ L₂ L₃ : Object} →
      OneCell L₂ L₃ → OneCell L₁ L₂ → OneCell L₁ L₃
    -- 2-identity
    Id-2 :
      {L₁ L₂ : Object} (f : OneCell L₁ L₂) → TwoCell f f
    -- Vertical 2-composition
    ∘V-2 :
      {L₁ L₂ : Object} {f g h : OneCell L₁ L₂} →
      TwoCell g h → TwoCell f g → TwoCell f h
    -- Horizontal 2-composition
    ∘H-2 :
      {L₁ L₂ L₃ : Object}
      {f g : OneCell L₁ L₂}
      {h k : OneCell L₂ L₃} →
      TwoCell h k → TwoCell f g →
      TwoCell (Compose-1 h f) (Compose-1 k g)

------------------------------------------------------------------------
-- 2. The canonical instance.
------------------------------------------------------------------------

LanguageBicategory : BicategoryOfLanguages
LanguageBicategory = record
  { Object    = LanguageWitness
  ; OneCell   = LanguageMorphism
  ; TwoCell   = Language2Morphism
  ; Id-1      = id-morphism
  ; Compose-1 = _∘L_
  ; Id-2      = id-2mor
  ; ∘V-2      = _∘V_
  ; ∘H-2      = _∘H_
  }

------------------------------------------------------------------------
-- 3. Capstone for B5.
--
-- The substrate's language classification now lives in a proper
-- bicategorical structure. B6-B9 supply naturality machinery and
-- close the Yoneda lemma's reverse direction (Y9 deferral).
------------------------------------------------------------------------
