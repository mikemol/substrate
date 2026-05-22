------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.AdjointPair
--
-- UP37 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The direct-image / inverse-image adjoint pair (f_*, f*) of a
-- geometric morphism: f* ⊣ f_* with f* exact.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.AdjointPair where

open import Substrate.Category.UniversalProperty.Sheaf using (UPSheaf)

------------------------------------------------------------------------
-- 1. AdjointPair signature.
------------------------------------------------------------------------

record SheafAdjointPair : Set₁ where
  field
    direct-image-stated  : Set
    inverse-image-stated : Set
    unit-stated          : Set
    counit-stated        : Set
    triangle-1-stated    : Set
    triangle-2-stated    : Set

------------------------------------------------------------------------
-- 2. Capstone for UP37.
--
-- Adjoint-pair signature lands. UP38 supplies the canonical
-- Substrate UPTopos.
------------------------------------------------------------------------
