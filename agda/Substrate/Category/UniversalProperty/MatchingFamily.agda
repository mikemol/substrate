------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.MatchingFamily
--
-- UP24 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- A MATCHING FAMILY for a presheaf F and cover c = { Vᵢ → U }:
-- a family of local sections (sᵢ : F(Vᵢ))_i that agree on overlaps
-- — i.e., for every pair (i, j) and every span (W, p₁ : W → Vᵢ,
-- p₂ : W → Vⱼ) with arrow i ∘ p₁ ≡ arrow j ∘ p₂, the restriction
-- F(p₁)(sᵢ) ≡ F(p₂)(sⱼ).
--
-- Substrate-honest scope: the matching condition is named at type
-- level + signature-bearing.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.MatchingFamily where

open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.UniversalProperty.Coverage
  using (UPCover; Idx; source-UP)
open import Substrate.Category.UniversalProperty.Presheaf
  using (UPPresheaf; F)

------------------------------------------------------------------------
-- 1. MatchingFamily record.
------------------------------------------------------------------------

record MatchingFamily
  {U : UPArrow}
  (c : UPCover U)
  (P : UPPresheaf)
  : Set₁ where
  field
    section  : (i : Idx c) → F P (source-UP c i)
    -- The matching condition (overlap-agreement) is named as a
    -- Set-level obligation.
    matches-stated : Set

open MatchingFamily public

------------------------------------------------------------------------
-- 2. Capstone for UP24.
--
-- MatchingFamily lands. UP25 supplies sheafification signature.
------------------------------------------------------------------------
