------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2
--
-- Defines: L1-Witness, UPArrow²
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ArrowOfArrow; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2 where

open import Substrate.Category.UniversalProperty
open import Substrate.Category.UniversalProperty.Morphism
variable
  S₁ T₁ S₂ T₂ S₃ T₃ S₄ T₄ : Set
  W₁ : S₁ → T₁ → Set
  W₂ : S₂ → T₂ → Set
  W₃ : S₃ → T₃ → Set
  W₄ : S₄ → T₄ → Set



------------------------------------------------------------------------
-- 1. The meta-level UPArrow²: the arrow-of-arrows.
--
-- An object at L2: a UPArrow whose Source and Target are themselves
-- UPArrows, and whose Witness relates two UPArrows by "is there a
-- UPMorphism between them?"
--
-- UPArrow² IS literally an inhabitant of UPArrow (per Set₁), with:
--   * Source²  = UPArrow      (any UP at L0)
--   * Target²  = UPArrow      (any other UP at L0)
--   * Witness² = UPMorphism   (the proof-relevant arrow at L1)
------------------------------------------------------------------------

-- The meta-arrow UPCategory⃗ as a span of UPs.
-- UPArrow²-Source / Target / Witness are CHOICE FUNCTIONS — packaged
-- as a record bundling the meta-data.

record UPArrow² (L0-Source : UPArrowP S₁ T₁ W₁)
                (L0-Target : UPArrowP S₂ T₂ W₂) : Set where
  field
    L1-Witness : UPMorphism L0-Source L0-Target

open UPArrow² public
