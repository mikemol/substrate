------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.SheafPullback
--
-- UP27 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Pullback of presheaves: given P : UPPresheaf and U : UPArrow,
-- the pullback P|_U restricts P to the slice (UPCategory / U). This
-- is the "restriction" / "comma" presheaf supporting local
-- properties.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.SheafPullback where

-- ⟡rc-topos (⟡set1-rerank2): UPPresheaf's `F` is now a PARAMETER, so the
-- hollow `PullbackToSlice` obligation-placeholder (`= Set₁`, unconsumed
-- beyond its own re-export) is DELETED; concrete slice-restriction
-- obligations live at the sites that state them.

------------------------------------------------------------------------
-- 2. Capstone for UP27.
--
-- Pullback signature lands. UP28 supplies the internal hom in PSh.
------------------------------------------------------------------------
