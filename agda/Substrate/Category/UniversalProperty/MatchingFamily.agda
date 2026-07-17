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
--
-- ⟡ta-upterm: objects are the Set₀ alphabet O; homs are UPTerm O Hom.
-- (O, Hom) via the enclosing section.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.MatchingFamily where

open import Substrate.Category.UniversalProperty.Coverage
  using (UPCover; source-UP)
open import Substrate.Category.UniversalProperty.Presheaf
  using (UPPresheaf)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- 1. MatchingFamily record.
  ------------------------------------------------------------------------

  -- ⟡set1-paydown: parameterize matches-stated (the overlap-agreement obligation Set)
  module _ (matches-stated : Set) where

    record MatchingFamily
      {U : O} {FP : O → Set} {I : Set}
      (c : UPCover O Hom U I)
      (P : UPPresheaf O Hom FP)
      : Set where
      field
        section  : (i : I) → FP (source-UP O Hom c i)

    open MatchingFamily public

------------------------------------------------------------------------
-- 2. Capstone for UP24.
--
-- MatchingFamily lands. UP25 supplies sheafification signature.
------------------------------------------------------------------------
