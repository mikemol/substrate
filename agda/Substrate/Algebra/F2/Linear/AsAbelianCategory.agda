------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.AsAbelianCategory
--
-- P8 of the P-arc. F₂-Linear as abelian category (kernels, cokernels,
-- additive structure, exact sequences).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)

module Substrate.Algebra.F2.Linear.AsAbelianCategory
  {ℓO ℓM : Level}
  (F2L-Abelian : CategoryOf {ℓO} {ℓM})
  -- Abelian-category data (kernels, cokernels, additive structure)
  -- supplied via user obligations.
  where

F2Linear-AsAbelianCategory : CategoryOf
F2Linear-AsAbelianCategory = F2L-Abelian
