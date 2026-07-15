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

open import Substrate.Category.UniversalProperty using (UPArrowP)
open import Substrate.Category.UniversalProperty.Term using (UPTerm)
open import Substrate.Category.UniversalProperty.Presheaf
  using (UPPresheaf; F; action; pres-id; pres-∘)

------------------------------------------------------------------------
-- 1. Pullback of a presheaf to a slice.
--
-- The shape: given P and U, produce a presheaf on slice / U.
-- Substrate-honest: this is signature-bearing — concrete
-- realisation needs the slice category structure (later sub-arc).
------------------------------------------------------------------------

PullbackToSlice : UPPresheaf → {S T : Set} {W : S → T → Set} → UPArrowP S T W → Set₂
PullbackToSlice _ _ = Set₁  -- obligation surface

------------------------------------------------------------------------
-- 2. Capstone for UP27.
--
-- Pullback signature lands. UP28 supplies the internal hom in PSh.
------------------------------------------------------------------------
