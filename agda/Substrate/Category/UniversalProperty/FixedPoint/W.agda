------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.FixedPoint.W
--
-- Defines: ι-W
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.FixedPoint; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.FixedPoint.W where

open import Substrate.Category.UniversalProperty
-- ⚑ duplicate `variable` block deleted; `ArrowOfArrow.UPArrow2` owns these. This
-- was the FOURTH module in the cluster carrying the same declarations — the split
-- copied the preamble into every leaf, which was harmless only while `private`
-- kept each copy invisible. Repairing the flattened blocks exposed all of it at
-- once, which is the ban's stated purpose: `private` hid a duplication.
open import Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2
open import Substrate.Foundation.Product



-- the composite-witness relation, over the L0 objects' carriers.
ι-W : (A : UPArrowP S₁ T₁ W₁) (B : UPArrowP S₂ T₂ W₂) → SourceP A → TargetP B → Set
ι-W A B s i =
  Σ (TargetP A) (λ t-src →
  Σ (SourceP B) (λ s-tgt →
    WitnessP A s t-src ×
    WitnessP B s-tgt i))
