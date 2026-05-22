------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.AsExactCategory
--
-- P9 of the P-arc. F₂-Linear as exact category (short exact sequences
-- 0 → A → B → C → 0 + their composition).
--
-- Projects the exact-category facet from the bundled
-- F2LinearCategoryStructures record.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Algebra.F2.Linear.CategoryStructures
  using (F2LinearCategoryStructures)

module Substrate.Algebra.F2.Linear.AsExactCategory
  {ℓO ℓM : Level}
  (structures : F2LinearCategoryStructures {ℓO} {ℓM})
  where

F2Linear-AsExactCategory : CategoryOf
F2Linear-AsExactCategory =
  F2LinearCategoryStructures.asExactCategory structures
