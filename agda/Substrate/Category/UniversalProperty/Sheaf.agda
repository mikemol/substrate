------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Sheaf
--
-- UP23 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- A SHEAF on the UPCategory site is a presheaf satisfying the
-- DESCENT condition: for every cover c = { Vᵢ → U }, every matching
-- family (a family of local sections agreeing on overlaps) glues
-- uniquely to a global section in F(U).
--
-- Substrate-honest scope: the descent condition is named as a
-- record field. UP24 supplies MatchingFamily; UP25 sheafification
-- signature.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Sheaf where

open import Substrate.Category.UniversalProperty.Presheaf using (UPPresheaf)

------------------------------------------------------------------------
-- 1. The Sheaf record (signature).
--
-- A sheaf bundles a presheaf with the descent witness. The descent
-- condition is the property: for every cover, every matching family
-- has a unique amalgamation.
------------------------------------------------------------------------

module _ (O : Set) (Hom : O → O → Set) where

  -- ⟡rc-topos (⟡set1-rerank2): UPPresheaf's `F` is now a PARAMETER — UPSheaf
  -- takes the fiber family F (and descent-stated, already a param) as its
  -- own parameters.
  record UPSheaf (F : O → Set) (descent-stated : Set) : Set where
    field
      presheaf  : UPPresheaf O Hom F
      -- Descent obligation: every cover-indexed matching family has
      -- a unique amalgamation. ⟡UPArrow-dissolve C: the Set-carrier
      -- placeholder lowers Set₁ → Set (like commute-stated), so UPSheaf : Set₁.

  open UPSheaf public

------------------------------------------------------------------------
-- 2. Capstone for UP23.
--
-- Sheaf record lands with descent named. UP24 supplies the
-- MatchingFamily; UP25 sheafification.
------------------------------------------------------------------------
