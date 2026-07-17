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

open import Substrate.Foundation.Level using (Level)

open import Substrate.Algebra.F2.Linear.CategoryStructures
  using (F2LinearCategoryStructures)
open import Substrate.Category.CategoryOf using (CategoryOf)

module Substrate.Algebra.F2.Linear.AsAbelianCategory
  {ℓO ℓM : Level}
  {Obj : Set ℓO} {Mor : Obj → Obj → Set ℓM}
  (structures : F2LinearCategoryStructures Obj Mor)
  where

F2Linear-AsAbelianCategory : CategoryOf Obj Mor
F2Linear-AsAbelianCategory =
  F2LinearCategoryStructures.asAbelianCategory structures
