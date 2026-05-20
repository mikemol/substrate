------------------------------------------------------------------------
-- Substrate.Category.PresheafCategory
--
-- S5 of the S-arc. PresheafCategory[C] = the category of contravariant
-- functors C^op → Set + natural transformations.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PresheafCategory where

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)

module _
  {ℓO ℓM : Level}
  (C : CategoryOf {ℓO} {ℓM})
  (Psh : CategoryOf {ℓO} {ℓM})
  -- User supplies the presheaf-category instance directly per
  -- substrate-pragmatic parametric pattern.
  where

  PresheafCategory : CategoryOf
  PresheafCategory = Psh
