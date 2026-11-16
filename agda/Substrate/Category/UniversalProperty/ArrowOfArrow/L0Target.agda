------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ArrowOfArrow.L0Target
--
-- Defines: L0-Target
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ArrowOfArrow; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.ArrowOfArrow.L0Target where

open import Substrate.Category.UniversalProperty
open import Substrate.Category.UniversalProperty.Morphism
-- ⚑ duplicate `variable` block deleted; `UPArrow2` (the cluster root) owns them.
-- See L0Source for why this is the fix rather than restoring `private`.
open import Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2



L0-Target : {A : UPArrowP S₁ T₁ W₁} {B : UPArrowP S₂ T₂ W₂}
          → UPArrow² A B → UPArrowP S₂ T₂ W₂
L0-Target {B = B} _ = B
