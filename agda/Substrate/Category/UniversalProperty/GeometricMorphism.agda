------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.GeometricMorphism
--
-- UP36 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- A GEOMETRIC MORPHISM between topoi: an adjoint pair
--   f* ⊣ f_*
-- with f* (inverse image) preserving finite limits.
--
-- Substrate-native scope: signature-bearing record.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.GeometricMorphism where

open import Substrate.Category.UniversalProperty.Topos using (UPTopos)

------------------------------------------------------------------------
-- 1. GeometricMorphism record (signature).
------------------------------------------------------------------------

-- ⟡set1-paydown: parameterize inverse-image/direct-image/adjunction/inv-image-lex Sets
module _ (inverse-image-stated direct-image-stated
          adjunction-stated inv-image-lex-stated : Set) where
  record GeometricMorphism (E F : UPTopos) : Set where

  open GeometricMorphism public

------------------------------------------------------------------------
-- 2. Capstone for UP36.
--
-- GeometricMorphism shape lands. UP37 supplies the direct/inverse-
-- image-pair explicitly; UP38 the canonical Substrate UPTopos.
------------------------------------------------------------------------
