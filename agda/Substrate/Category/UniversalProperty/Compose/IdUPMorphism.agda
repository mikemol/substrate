------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Compose.IdUPMorphism
--
-- Defines: id-UPMorphism
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.Compose; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Compose.IdUPMorphism where

open import Substrate.Category.UniversalProperty
open import Substrate.Category.UniversalProperty.Morphism
-- ⚑ duplicate `variable` block deleted; `ArrowOfArrow.UPArrow2` owns these.
-- `--dup-variables` reports the whole cohort: S₁..W₃ were each declared in THREE
-- modules of this cluster, invisible to `def_index` (which does not carry
-- generalizable variables) and latent until two of them met in one scope.
open import Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2



------------------------------------------------------------------------
-- 1. Identity square.
------------------------------------------------------------------------

id-UPMorphism : (U : UPArrowP S₁ T₁ W₁) → UPMorphism U U
id-UPMorphism U = record
  { source-map = λ s → s
  ; target-map = λ i → i
  ; coherent   = λ _ _ p → p
  }
