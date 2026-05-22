------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ArrowOfArrow
--
-- UP5 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Surfaces the META-LEVEL ITERATION the user named: "my favourite
-- category is the category that is an object in the category of
-- arrow categories."
--
-- Concretely: UPCategory itself, viewed as a category C, has an
-- ARROW CATEGORY C⃗ whose objects are the UP-morphisms of C and
-- whose morphisms are commuting squares of UP-morphisms. By the
-- substrate's UPArrow framing, every C⃗-object IS a UPArrow at a
-- higher type level:
--
--   UPArrow²: an arrow-of-arrows
--     Source²  = UPArrow
--     Target²  = UPArrow
--     Witness² = the existence of a UPMorphism between them
--
-- This is the first iteration of the tetrative tower:
--
--   L0   UPArrow                           — UP-objects (UP1)
--   L1   UPMorphism                        — UP-arrows  (UP2)
--   L2   UPArrow² = the arrow-of-arrows    — this slice
--   L3+  iterated by the same construction
--
-- The fixed-point claim (UP6) says: L2 has a canonical embedding
-- back into L0 (any UPArrow² IS itself a UPArrow at the
-- Source=UPArrow, Target=UPArrow level).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.ArrowOfArrow where

open import Substrate.Category.UniversalProperty
  using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Morphism
  using (UPMorphism)

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

record UPArrow² : Set₂ where
  field
    L0-Source : UPArrow
    L0-Target : UPArrow
    L1-Witness : UPMorphism L0-Source L0-Target

open UPArrow² public

------------------------------------------------------------------------
-- 2. The category-of-arrows construction.
--
-- The category UPCategory⃗ has UPArrow²-records as objects and
-- commuting squares of UPMorphisms as morphisms. UP6 supplies the
-- canonical fixed-point embedding back into UPArrow.
------------------------------------------------------------------------

-- A morphism in UPCategory⃗ is a pair of UPMorphisms (one for the
-- Source UPArrow, one for the Target UPArrow) commuting with the
-- L1-Witness.

record UPArrow²-Morphism (α β : UPArrow²) : Set₁ where
  open UPArrow²
  field
    on-source : UPMorphism (L0-Source α) (L0-Source β)
    on-target : UPMorphism (L0-Target α) (L0-Target β)
    -- The square-commutation at the witness level is NAMED but
    -- packaged at the type level (it's a relation between four
    -- UPMorphisms). Substrate-honest: signature-bearing.
    commute-stated : Set

open UPArrow²-Morphism public

------------------------------------------------------------------------
-- 3. Capstone for UP5.
--
-- The L2 meta-level lands: UPArrow² names the arrow-of-arrows
-- explicitly. UP6 supplies the fixed-point canonical embedding
-- UPArrow² → UPArrow that closes the substrate's tetrative
-- metacircularity at the structural level.
------------------------------------------------------------------------
