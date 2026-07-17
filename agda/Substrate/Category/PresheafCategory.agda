------------------------------------------------------------------------
-- Substrate.Category.PresheafCategory
--
-- S5 of the S-arc. PresheafCategory[C] = the category of contravariant
-- functors C^op → Set + natural transformations.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PresheafCategory where

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)

module _
  {ℓO ℓM : Level}
  {ObjC : Set ℓO} {MorC : ObjC → ObjC → Set ℓM}
  (C : CategoryOf ObjC MorC)
  {ObjPsh : Set ℓO} {MorPsh : ObjPsh → ObjPsh → Set ℓM}
  (Psh : CategoryOf ObjPsh MorPsh)
  -- User supplies the presheaf-category instance directly per
  -- substrate-pragmatic parametric pattern.
  where

  PresheafCategory : CategoryOf ObjPsh MorPsh
  PresheafCategory = Psh
