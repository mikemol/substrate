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

record GeometricMorphism (E F : UPTopos) : Set₁ where
  field
    -- The inverse-image and direct-image functor signatures
    -- (deferred — relies on UPTopos's Sh-Obj structure).
    inverse-image-stated : Set
    direct-image-stated  : Set
    adjunction-stated    : Set
    -- The inverse-image preserves finite limits:
    inv-image-lex-stated : Set

open GeometricMorphism public

------------------------------------------------------------------------
-- 2. Capstone for UP36.
--
-- GeometricMorphism shape lands. UP37 supplies the direct/inverse-
-- image-pair explicitly; UP38 the canonical Substrate UPTopos.
------------------------------------------------------------------------
