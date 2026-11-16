------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Compose.ComposeUPMorphism
--
-- Defines: compose-UPMorphism
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.Compose; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Compose.ComposeUPMorphism where

open import Substrate.Category.UniversalProperty
open import Substrate.Category.UniversalProperty.Morphism
-- ⚑ THIS WAS ONE UNPARSEABLE LINE — a `private variable` block the horizontal split
-- flattened, so its four `:`-groups ran together and Agda reported [ParseError] at
-- `Set W₂ :`. A `variable` block needs one group per line.
--
-- ⚑⚑ AND MY FIRST REPAIR RE-EXPANDED IT HERE, WHICH WAS WRONG IN A WAY THE PARSE
-- ERROR HAD BEEN HIDING. I wrote that `private` was "pointless on a `variable`
-- block, whose names are never exported" — false: generalizable variables ARE
-- exported, and dropping `private` made three modules' copies of `S₁` collide as
-- [AmbiguousName] the moment a consumer imported two of them. The block is now
-- DELETED rather than re-privatised: `ArrowOfArrow.UPArrow2` declares the same
-- variables and is imported transitively, so this was a copy the split made, and
-- `private` had been hiding the duplication rather than resolving it — which is
-- precisely what the ban on `private` exists to surface.
open import Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2



------------------------------------------------------------------------
-- 2. Composition (paste squares horizontally).
------------------------------------------------------------------------

compose-UPMorphism :
  {U₁ : UPArrowP S₁ T₁ W₁} {U₂ : UPArrowP S₂ T₂ W₂} {U₃ : UPArrowP S₃ T₃ W₃} →
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
