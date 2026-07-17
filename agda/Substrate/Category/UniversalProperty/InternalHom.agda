------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.InternalHom
--
-- UP28 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The internal hom [P, Q] in PSh(UPCategory): a presheaf whose
-- sections at U are natural transformations Yoneda(U) × P → Q.
--
-- PSh(C) is cartesian closed for any small C; the signature of the
-- internal hom lands here. Concrete construction (using the
-- naturality square) is canonical category-theoretic content.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.InternalHom where

open import Substrate.Foundation.Product using (Σ)
open import Substrate.Category.UniversalProperty.Presheaf using (UPPresheaf)

------------------------------------------------------------------------
-- 1. Internal-hom signature.
------------------------------------------------------------------------

module _ (O : Set) (Hom : O → O → Set) where

  -- ⟡rc-topos (⟡set1-rerank2): UPPresheaf's `F` is now a PARAMETER — the
  -- internal-hom's resulting fiber family is genuinely quantified over, so
  -- this stays a documented Set₁ Σ-holder.
  InternalHomType : Set₁
  InternalHomType = (F G : O → Set) → UPPresheaf O Hom F → UPPresheaf O Hom G →
                     Σ (O → Set) (UPPresheaf O Hom)

-- Standard construction: [P, Q](U) = naturality-respecting maps
-- (V → U) × P(V) → Q(V) parametric in V. The Yoneda lemma gives
-- this Set explicitly. Concrete bridge deferred.

------------------------------------------------------------------------
-- 2. Capstone for UP28.
--
-- Internal-hom signature lands. UP29 supplies substrate examples.
------------------------------------------------------------------------
