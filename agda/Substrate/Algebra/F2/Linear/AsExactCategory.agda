------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.AsExactCategory
--
-- P9 of the P-arc. F₂-Linear as exact category (short exact sequences
-- 0 → A → B → C → 0 + their composition).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)

module Substrate.Algebra.F2.Linear.AsExactCategory
  {ℓO ℓM : Level}
  (F2L-Exact : CategoryOf {ℓO} {ℓM})
  where

F2Linear-AsExactCategory : CategoryOf
F2Linear-AsExactCategory = F2L-Exact
