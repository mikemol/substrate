------------------------------------------------------------------------
-- Substrate.Category.KanExtension
--
-- S4 of the S-arc. Left + right Kan extensions: universal way to
-- extend a functor F : A → C along K : A → B to a functor B → C.
--
-- Per the skeleton-as-pullback principle: LeftKan / RightKan is a
-- 1:2 cone (duality witness). With Functor.Opposite in scope, the
-- right Kan extension absorbs into the left:
--
--   RightKanExtension A B C K F
--     ≡ LeftKanExtension (Opposite A) (Opposite B) (Opposite C)
--                        (opposite-Functor K) (opposite-Functor F)
--
-- The underlying Lan : Functor B C lives in C up to morphism-
-- direction flipping; `from-opposite-Functor (LeftKanExtension.Lan _)`
-- recovers the substrate-level `Ran : Functor B C` projection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.KanExtension where

open import Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)
open import Substrate.Category.Functor.Opposite using (opposite-Functor)
open import Substrate.Category.Opposite using (Opposite)

record LeftKanExtension
  {ℓOA ℓMA ℓOB ℓMB ℓOC ℓMC : Level}
  (A : CategoryOf {ℓOA} {ℓMA})
  (B : CategoryOf {ℓOB} {ℓMB})
  (C : CategoryOf {ℓOC} {ℓMC})
  (K : Functor A B)
  (F : Functor A C) : Set (lsuc (ℓOB ⊔ ℓMB ⊔ ℓOC ⊔ ℓMC)) where
  field
    Lan : Functor B C

RightKanExtension :
  {ℓOA ℓMA ℓOB ℓMB ℓOC ℓMC : Level}
  (A : CategoryOf {ℓOA} {ℓMA})
  (B : CategoryOf {ℓOB} {ℓMB})
  (C : CategoryOf {ℓOC} {ℓMC})
  (K : Functor A B)
  (F : Functor A C) → Set _
RightKanExtension A B C K F =
  LeftKanExtension (Opposite A) (Opposite B) (Opposite C)
                   (opposite-Functor K) (opposite-Functor F)
