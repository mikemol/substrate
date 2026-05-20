------------------------------------------------------------------------
-- Substrate.Category.Monad
--
-- R1 of the R-arc. Monad primitive: endofunctor T : C → C with
-- η : Id ⇒ T and μ : T² ⇒ T satisfying associativity + unit laws.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Monad where

open import Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor
  using (Functor; id-Functor; compose-Functor)
open import Substrate.Category.NaturalTransformation
  using (NaturalTransformation)

record Monad
  {ℓO ℓM : Level}
  (C : CategoryOf {ℓO} {ℓM}) : Set (lsuc (ℓO ⊔ ℓM)) where
  field
    T  : Functor C C
    η  : NaturalTransformation (id-Functor C) T
    μ  : NaturalTransformation (compose-Functor T T) T
  -- Associativity + unit laws: user obligations per substrate-pragmatic
  -- minimum.
