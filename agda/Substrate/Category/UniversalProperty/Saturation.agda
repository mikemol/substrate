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


module _ (O : Set) (Hom : O → O → Set) where

  -- ⟡rc-deletes (⟡rerank2-floor-dissolve): the `Saturated` statement-def
  -- (uninhabited, unconsumed; a Σ-over-Set existential "a designated
  -- refinement exists") is DELETED. If saturation is built it will be a real
  -- construction over a Set₀ cover-index universe, not a Set₁ signature.
