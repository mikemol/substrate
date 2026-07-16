------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Saturation
--
-- UP19 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The saturated pretopology: close the designated covers under
-- "refined-by" to form a coverage. A cover c is in the saturation iff
-- some refining c' is designated.
--
-- ⟡ta-upterm: objects are the Set₀ alphabet O; covers are UPCover O Hom.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Saturation where

open import Substrate.Foundation.Product using (Σ)
open import Substrate.Category.UniversalProperty.Coverage using (UPCover)
open import Substrate.Category.UniversalProperty.Refinement using (Refines)

module _ (O : Set) (Hom : O → O → Set) where

  Saturated :
    ((U : O) → UPCover O Hom U → Set) →
    (U : O) → UPCover O Hom U → Set₁
  Saturated designated U c =
    Σ (UPCover O Hom U) (λ c' →
    Σ (designated U c') (λ _ → Refines O Hom c c'))
