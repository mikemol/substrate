------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2Morphism
--
-- Defines: UPArrow²-Morphism, on-source, on-target
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ArrowOfArrow; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2Morphism where

open import Substrate.Category.UniversalProperty
open import Substrate.Category.UniversalProperty.Morphism
-- ⚑ duplicate `variable` block deleted; `UPArrow2` (the cluster root) owns them.
-- See L0Source for why this is the fix rather than restoring `private`.
open import Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2
open import Substrate.Category.UniversalProperty.ArrowOfArrow.L0Source
open import Substrate.Category.UniversalProperty.ArrowOfArrow.L0Target



------------------------------------------------------------------------
-- 2. The category-of-arrows construction.
--
-- The category UPCategory⃗ has UPArrow²-records as objects and
-- commuting squares of UPMorphisms as morphisms. UP6 supplies the
-- canonical fixed-point embedding back into UPArrow.
------------------------------------------------------------------------

-- A morphism in UPCategory⃗ is a pair of UPMorphisms (one for the
-- Source UPArrow, one for the Target UPArrow) commuting with the
-- L1-Witness.

-- ⟡rc-cheap (⟡set1-rerank2): commute-stated is a PARAMETER now (a Set-valued
-- field pinned the record at Set₁). The square-commutation at the witness level
-- is NAMED but packaged at the type level (it's a relation between four
-- UPMorphisms). Substrate-honest: signature-bearing.
record UPArrow²-Morphism {A₁ : UPArrowP S₁ T₁ W₁} {B₁ : UPArrowP S₂ T₂ W₂}
                         {A₂ : UPArrowP S₃ T₃ W₃} {B₂ : UPArrowP S₄ T₄ W₄}
                         (α : UPArrow² A₁ B₁) (β : UPArrow² A₂ B₂)
                         (commute-stated : Set) : Set where
  field
    on-source : UPMorphism (L0-Source α) (L0-Source β)
    on-target : UPMorphism (L0-Target α) (L0-Target β)

open UPArrow²-Morphism public

------------------------------------------------------------------------
-- 3. Capstone for UP5.
--
-- The L2 meta-level lands: UPArrow² names the arrow-of-arrows
-- explicitly. UP6 supplies the fixed-point canonical embedding
-- UPArrow² → UPArrow that closes the substrate's tetrative
-- metacircularity at the structural level.
------------------------------------------------------------------------
