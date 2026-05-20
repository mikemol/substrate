------------------------------------------------------------------------
-- Substrate.Category.RootSystem.AsCartanType
--
-- O7 of the O-arc. Backward functor RootSystem → CartanType.
--
-- Sibling of O6 forward. Together (O6, O7) form the candidate
-- adjoint/equivalence pair closed by O8.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.RootSystem.AsCartanType
  {ℓOR ℓMR ℓOC ℓMC : Level}
  (RootCat : CategoryOf {ℓOR} {ℓMR})
  (CartanCat : CategoryOf {ℓOC} {ℓMC})
  (Root→Cartan : Functor RootCat CartanCat)
  where

RootSystem-AsCartanType-Functor : Functor RootCat CartanCat
RootSystem-AsCartanType-Functor = Root→Cartan
