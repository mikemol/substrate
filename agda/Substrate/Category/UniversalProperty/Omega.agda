------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Omega
--
-- UP32 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The subobject classifier Ω in PSh(UPCategory) / Sh(UPSite):
--
--   Ω(U) = "the set of sieves on U"
--
-- This is the canonical Grothendieck-topos Ω. Substrate-native: a
-- sieve at U is the Sieve record (UP13); Ω(U) is the family of all
-- such sieves.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Omega where

open import Substrate.Category.UniversalProperty using (UPArrowP)
open import Substrate.Category.UniversalProperty.Sieve using (Sieve)

------------------------------------------------------------------------
-- 1. Ω as a presheaf-like function on UPArrows.
--
-- Substrate-honest: Sieve U lives at Set₂ (because UPTerm-indexed
-- predicates land at Set₁ to support set-quantification). Ω lands
-- as a presheaf at the bumped level.
------------------------------------------------------------------------

Ω : {S T : Set} {W : S → T → Set} → UPArrowP S T W → Set₂
Ω U = Sieve U

------------------------------------------------------------------------
-- 2. Capstone for UP32.
--
-- Subobject classifier signature lands. UP33 supplies the truth
-- value interpretation; UP34 internal logic.
------------------------------------------------------------------------
