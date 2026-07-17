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

open import Substrate.Foundation.Level using (Level)

open import Substrate.Algebra.F2.Linear.CategoryStructures
  using (F2LinearCategoryStructures)
open import Substrate.Category.CategoryOf using (CategoryOf)

module Substrate.Algebra.F2.Linear.AsExactCategory
  {ℓO ℓM : Level}
  {Obj : Set ℓO} {Mor : Obj → Obj → Set ℓM}
  (structures : F2LinearCategoryStructures Obj Mor)
  where

F2Linear-AsExactCategory : CategoryOf Obj Mor
F2Linear-AsExactCategory =
  F2LinearCategoryStructures.asExactCategory structures
