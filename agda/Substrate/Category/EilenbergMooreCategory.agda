------------------------------------------------------------------------
-- Substrate.Category.EilenbergMooreCategory
--
-- R6 of the R-arc. Eilenberg-Moore category of a Monad M : category
-- of T-algebras (R3) + algebra-morphisms.
--
-- Thin projection from Substrate.Category.Monad.DerivedCategoryOf:
-- the substrate's "category derived from (C, M)" skeleton, with
-- `monad-derived-Category` renamed to `EilenbergMoore-Category` for
-- this specialisation.
--
-- Per the skeleton-as-pullback principle: EilenbergMooreCategory is
-- one leg of the 1:N cone over the Monad-derived-CategoryOf witness;
-- KleisliCategory is another. See
-- Substrate.Category.Monad.DerivedCategoryOf for the apex.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Monad using (Monad)

module Substrate.Category.EilenbergMooreCategory
  {ℓO ℓM : Level}
  (C : CategoryOf {ℓO} {ℓM})
  (M : Monad C)
  (EM-Cat : CategoryOf {ℓO} {ℓM})
  where

open import Substrate.Category.Monad.DerivedCategoryOf C M EM-Cat public
  renaming (monad-derived-Category to EilenbergMoore-Category)
