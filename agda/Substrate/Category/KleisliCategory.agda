------------------------------------------------------------------------
-- Substrate.Category.KleisliCategory
--
-- R5 of the R-arc. Kleisli category of a Monad M : same objects as
-- base C, morphisms a → b are C-morphisms a → T(b).
--
-- Thin projection from Substrate.Category.Monad.DerivedCategoryOf:
-- the substrate's "category derived from (C, M)" skeleton, with
-- `monad-derived-Category` renamed to `KleisliCategory` for this
-- specialisation.
--
-- Per the skeleton-as-pullback principle: KleisliCategory is one
-- leg of the 1:N cone over the Monad-derived-CategoryOf witness;
-- EilenbergMooreCategory is another. See
-- Substrate.Category.Monad.DerivedCategoryOf for the apex.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Monad using (Monad)

module Substrate.Category.KleisliCategory
  {ℓO ℓM : Level}
  (C : CategoryOf {ℓO} {ℓM})
  (M : Monad C)
  -- User supplies the Kleisli CategoryOf instance directly per the
  -- substrate-pragmatic parametric pattern.
  (Kleisli : CategoryOf {ℓO} {ℓM})
  where

open import Substrate.Category.Monad.DerivedCategoryOf C M Kleisli public
  renaming (monad-derived-Category to KleisliCategory)
