------------------------------------------------------------------------
-- Substrate.Category.EilenbergMooreCategory
--
-- R6 of the R-arc. Eilenberg-Moore category of a Monad M : category
-- of T-algebras (R3) + algebra-morphisms.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.EilenbergMooreCategory where

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Monad using (Monad)

module _
  {ℓO ℓM : Level}
  (C : CategoryOf {ℓO} {ℓM})
  (M : Monad C)
  (EM-Cat : CategoryOf {ℓO} {ℓM})
  where

  EilenbergMoore-Category : CategoryOf
  EilenbergMoore-Category = EM-Cat
