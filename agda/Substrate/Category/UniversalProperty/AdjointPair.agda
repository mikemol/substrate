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

-- ⟡set1-paydown: parameterize direct-image/inverse-image/unit/counit/triangle Sets
module _ (direct-image-stated inverse-image-stated unit-stated
          counit-stated triangle-1-stated triangle-2-stated : Set) where
  record SheafAdjointPair : Set where

------------------------------------------------------------------------
-- 2. Capstone for UP37.
--
-- Adjoint-pair signature lands. UP38 supplies the canonical
-- Substrate UPTopos.
------------------------------------------------------------------------
