------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.FixedPoint.Op
--
-- Defines: ι
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.FixedPoint; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.FixedPoint.Op where

open import Substrate.Category.UniversalProperty
open import Substrate.Category.UniversalProperty.ArrowOfArrow.L0Source
open import Substrate.Category.UniversalProperty.ArrowOfArrow.L0Target
open import Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2
open import Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2Morphism
-- ⚑ duplicate `variable` block deleted — the rewire above now brings `UPArrow2`
-- into scope, which declares the same generalizable variables. Two declarations of
-- `S₁` is [ClashingDefinition]; `UPArrow2` is the owner. Same call as the
-- ArrowOfArrow leaves: de-duplicate rather than re-privatise, since `private`
-- would only hide a duplication the ban exists to surface.
open import Substrate.Foundation.Product
open import Substrate.Category.UniversalProperty.FixedPoint.W



-- ⟡UPArrow-dissolve C: ι packages the meta-arrow as the (trivial) object whose
-- carriers are (SourceP A, TargetP B) and whose witness is the composite ι-W.
ι : {A : UPArrowP S₁ T₁ W₁} {B : UPArrowP S₂ T₂ W₂}
  → UPArrow² A B → UPArrowP (SourceP A) (TargetP B) (ι-W A B)
ι _ = mkUP
