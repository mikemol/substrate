------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.AsAbelianCategory
--
-- P8 of the P-arc. F₂-Linear as abelian category (kernels, cokernels,
-- additive structure, exact sequences).
--
-- Projects the abelian-category facet from the bundled
-- F2LinearCategoryStructures record.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Algebra.F2.Linear.CategoryStructures
  using (F2LinearCategoryStructures)
open import Substrate.Category.CategoryOf using (CategoryOf)

module Substrate.Algebra.F2.Linear.AsAbelianCategory
  {ℓO ℓM : Level}
  (structures : F2LinearCategoryStructures {ℓO} {ℓM})
  where

F2Linear-AsAbelianCategory : CategoryOf
F2Linear-AsAbelianCategory =
  F2LinearCategoryStructures.asAbelianCategory structures
