------------------------------------------------------------------------
-- Substrate.Category.Coalgebra-of-Comonad
--
-- R4 of the R-arc. S-coalgebra: pair (A, β : A → S(A)) satisfying
-- counit + comultiplication compatibility (dual of R3).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Coalgebra-of-Comonad where

open import Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)
open import Substrate.Category.Comonad using (Comonad)

record CoalgebraOfComonad
  {ℓO ℓM : Level}
  (C : CategoryOf {ℓO} {ℓM})
  (W : Comonad C) : Set (ℓO ⊔ ℓM) where
  field
    A : CategoryOf.Obj C
    β : CategoryOf.Mor C A (Functor.F-obj (Comonad.S W) A)
