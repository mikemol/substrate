------------------------------------------------------------------------
-- Substrate.Category.RootSystem.AsCartanType
--
-- O7 of the O-arc. Backward functor RootSystem → CartanType.
--
-- Sibling of O6 forward. Together (O6, O7) form the candidate
-- adjoint/equivalence pair closed by O8.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.RootSystem.AsCartanType
  {ℓOR ℓMR ℓOC ℓMC : Level}
  {ObjRootCat : Set ℓOR} {MorRootCat : ObjRootCat → ObjRootCat → Set ℓMR}
  {ObjCartanCat : Set ℓOC} {MorCartanCat : ObjCartanCat → ObjCartanCat → Set ℓMC}
  (RootCat : CategoryOf ObjRootCat MorRootCat)
  (CartanCat : CategoryOf ObjCartanCat MorCartanCat)
  (Root→Cartan : Functor RootCat CartanCat)
  where

RootSystem-AsCartanType-Functor : Functor RootCat CartanCat
RootSystem-AsCartanType-Functor = Root→Cartan
