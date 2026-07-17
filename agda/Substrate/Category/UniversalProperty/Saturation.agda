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

  -- ⟡rc-topos (⟡set1-rerank2): UPCover's `Idx` is a PARAMETER now, so the
  -- existential cover c' also existentially quantifies over its index Set —
  -- this def stays Set₁ (a documented Σ-over-Set holder; the same shape
  -- Pretopology's `designated` and Refinement's `Refines` already carry).
  Saturated :
    ((U : O) (I : Set) → UPCover O Hom U I → Set) →
    (U : O) {I : Set} → UPCover O Hom U I → Set₁
  Saturated designated U {I} c =
    Σ Set (λ I' →
    Σ (UPCover O Hom U I') (λ c' →
    Σ (designated U I' c') (λ _ → Refines O Hom c c')))
