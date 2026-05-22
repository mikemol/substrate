------------------------------------------------------------------------
-- Substrate.Category.CartanType.AsRootSystem
--
-- O6 of the O-arc. Forward functor CartanType → RootSystem.
--
-- L12 CartanType + L11 RootSystem are records; O6 names the forward
-- direction (Cartan data → root system data) as a substrate M1 Functor.
-- Closes the HIGH-PRIORITY M-arc residue row.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.CartanType.AsRootSystem
  {ℓOC ℓMC ℓOR ℓMR : Level}
  (CartanCat : CategoryOf {ℓOC} {ℓMC})
  (RootCat : CategoryOf {ℓOR} {ℓMR})
  (Cartan→Root : Functor CartanCat RootCat)
  where

CartanType-AsRootSystem-Functor : Functor CartanCat RootCat
CartanType-AsRootSystem-Functor = Cartan→Root
