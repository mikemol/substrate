------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Morphism
--
-- UP2 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- A UPMorphism is a commuting square in Arr(Span). Concretely, given
-- two UPArrows U₁ and U₂:
--
--    Source U₁ ────source-map────▶ Source U₂
--        │                              │
--    Witness U₁                     Witness U₂
--        │                              │
--        ▼                              ▼
--    Target U₁ ◀───target-map──── Target U₂
--
-- The square commutes UP TO `coherent`: if i₂ witnesses (source-map s₁)
-- in U₂, then (target-map i₂) witnesses s₁ in U₁.
--
-- The source-map is COVARIANT (specs translate forward); the
-- target-map is CONTRAVARIANT (instances pull back). This is the
-- standard span-category morphism direction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Morphism where

open import Substrate.Category.UniversalProperty
  using (UPArrowP; SourceP; TargetP; WitnessP)

------------------------------------------------------------------------
-- 1. The UPMorphism record (= commuting square in Arr(Span)).
--    ⟡UPArrow-dissolve C: indexed by the UPArrowP telescope (carriers as
--    params); the projections are the SourceP/TargetP/WitnessP shims.
------------------------------------------------------------------------

record UPMorphism {S₁ T₁ : Set} {W₁ : S₁ → T₁ → Set}
                  {S₂ T₂ : Set} {W₂ : S₂ → T₂ → Set}
                  (U₁ : UPArrowP S₁ T₁ W₁) (U₂ : UPArrowP S₂ T₂ W₂) : Set where
  field
    source-map :
      SourceP U₁ → SourceP U₂
    target-map :
      TargetP U₂ → TargetP U₁
    coherent :
      (s : SourceP U₁) (i : TargetP U₂) →
      WitnessP U₂ (source-map s) i →
      WitnessP U₁ s (target-map i)

open UPMorphism public

------------------------------------------------------------------------
-- 2. Capstone for UP2.
--
-- The morphism = square shape lands. UP3 supplies identity +
-- composition; UP4 the term-algebra (UPGen + UPTerm); UP5 the
-- arrow-of-arrow meta-level; UP6 the fixed-point embedding.
------------------------------------------------------------------------
