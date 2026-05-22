------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Compose
--
-- UP3 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Identity + composition for UPMorphism (square composition in
-- Arr(Span)). Composition pastes squares horizontally:
--
--   U₁ ─f─▶ U₂ ─g─▶ U₃
--
-- gives source-maps composing covariantly, target-maps composing
-- contravariantly, coherence chaining through both.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Compose where

open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.UniversalProperty.Morphism
  using (UPMorphism; source-map; target-map; coherent)

------------------------------------------------------------------------
-- 1. Identity square.
------------------------------------------------------------------------

id-UPMorphism : (U : UPArrow) → UPMorphism U U
id-UPMorphism U = record
  { source-map = λ s → s
  ; target-map = λ i → i
  ; coherent   = λ _ _ p → p
  }

------------------------------------------------------------------------
-- 2. Composition (paste squares horizontally).
------------------------------------------------------------------------

compose-UPMorphism :
  {U₁ U₂ U₃ : UPArrow} →
  UPMorphism U₂ U₃ →
  UPMorphism U₁ U₂ →
  UPMorphism U₁ U₃
compose-UPMorphism g f = record
  { source-map = λ s → source-map g (source-map f s)
  ; target-map = λ i → target-map f (target-map g i)
  ; coherent   = λ s i p →
      coherent f s (target-map g i)
        (coherent g (source-map f s) i p)
  }

------------------------------------------------------------------------
-- 3. Capstone for UP3.
--
-- Identity + composition land at the SEMANTIC level (records of
-- maps and coherence proofs). UP4 supplies the term-algebra
-- encoding (UPGen + UPTerm) that ABSTRACTS over these records.
-- UP5+ build the higher meta-structure on top.
------------------------------------------------------------------------
