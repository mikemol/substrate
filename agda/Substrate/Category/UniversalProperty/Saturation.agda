------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Saturation
--
-- UP19 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The saturated pretopology: close the designated covers under
-- "refined-by" to form a coverage. A cover c is in the saturation
-- iff some refining c' is designated.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Saturation where

open import Substrate.Foundation.Product using (Σ)
open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.UniversalProperty.Coverage using (UPCover)
open import Substrate.Category.UniversalProperty.Refinement using (Refines)

------------------------------------------------------------------------
-- 1. Saturation of a pretopology.
--
-- Given a pretopology designated : (U : UPArrow) → UPCover U → Set,
-- its saturation is "cover c is saturated iff there exists c'
-- designated and c refines c'."
------------------------------------------------------------------------

Saturated :
  ((U : UPArrow) → UPCover U → Set) →
  (U : UPArrow) → UPCover U → Set₂
Saturated designated U c =
  Σ (UPCover U) (λ c' →
  Σ (designated U c') (λ _ → Refines c c'))

------------------------------------------------------------------------
-- 2. Capstone for UP19.
--
-- Saturation lands. UP20 supplies the Phase-2 capstone.
------------------------------------------------------------------------
