------------------------------------------------------------------------
-- Substrate.Category.Comonad
--
-- R2 of the R-arc. Comonad primitive: dual of R1 Monad — endofunctor
-- S : C → C with ε : S ⇒ Id and δ : S ⇒ S² satisfying coassociativity
-- + counit laws.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Comonad where

open import Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor
  using (Functor; id-Functor; compose-Functor)
open import Substrate.Category.NaturalTransformation
  using (NaturalTransformation)

record Comonad
  {ℓO ℓM : Level}
  (C : CategoryOf {ℓO} {ℓM}) : Set (lsuc (ℓO ⊔ ℓM)) where
  field
    S : Functor C C
    ε : NaturalTransformation S (id-Functor C)
    δ : NaturalTransformation S (compose-Functor S S)
