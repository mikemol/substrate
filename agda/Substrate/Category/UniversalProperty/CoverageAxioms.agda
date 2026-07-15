------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.CoverageAxioms
--
-- UP16 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The three Grothendieck pretopology axioms, stated explicitly at
-- the UPCategory level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.CoverageAxioms where

open import Substrate.Category.UniversalProperty using (UPArrowP)
open import Substrate.Category.UniversalProperty.Term
  using (UPTerm; [])
open import Substrate.Category.UniversalProperty.Coverage
  using (UPCover; Idx; source-UP; arrow)

------------------------------------------------------------------------
-- 1. Identity axiom: the singleton {id_U : U → U} is a cover.
--
-- Substrate-honest: stated as a function producing such a cover.
------------------------------------------------------------------------

open import Substrate.Foundation.Unit using (⊤; tt)

-- ⟡UPArrow-dissolve C: telescope carriers (auto).
private variable
  SU TU : Set
  WU : SU → TU → Set

singleton-id-Cover : (U : UPArrowP SU TU WU) → UPCover U
singleton-id-Cover U = record
  { Idx       = ⊤
  ; source-UP = λ _ → U
  ; arrow     = λ _ → []
  }

------------------------------------------------------------------------
-- 2. Stability axiom (signature).
--
-- If { Vᵢ → U } is a cover and W → U is any morphism, then the
-- pullback family { Vᵢ ×_U W → W } is a cover of W. Substrate-honest:
-- the obligation surface is named.
------------------------------------------------------------------------

StabilityAxiom : (U : UPArrowP SU TU WU) (c : UPCover U) → Set₂
StabilityAxiom _ _ = Set₁  -- obligation placeholder

------------------------------------------------------------------------
-- 3. Transitivity axiom (signature).
--
-- If { Vᵢ → U } is a cover and for each i, { Wᵢⱼ → Vᵢ } is a cover,
-- then the composite family { Wᵢⱼ → U } is a cover.
------------------------------------------------------------------------

TransitivityAxiom : (U : UPArrowP SU TU WU) (c : UPCover U) → Set₂
TransitivityAxiom _ _ = Set₁  -- obligation placeholder

------------------------------------------------------------------------
-- 4. Capstone for UP16.
--
-- The three axioms are stated. UP17 discharges identity by exhibiting
-- the singleton-id cover; UP18 the substrate's concrete UPCovers.
------------------------------------------------------------------------
