------------------------------------------------------------------------
-- Substrate.Category.CartanRootEquivalence
--
-- O8 of the O-arc. Equivalence of categories between Cartan-types and
-- RootSystems witnessed by O6 forward + O7 backward + isomorphism
-- nat-trans (user-supplied: F ∘ G ≅ Id, G ∘ F ≅ Id).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor
  using (Functor; id-Functor; compose-Functor)
open import Substrate.Category.NaturalTransformation
  using (NaturalTransformation)

module Substrate.Category.CartanRootEquivalence
  {ℓOC ℓMC ℓOR ℓMR : Level}
  (CartanCat : CategoryOf {ℓOC} {ℓMC})
  (RootCat : CategoryOf {ℓOR} {ℓMR})
  (F : Functor CartanCat RootCat)
  (G : Functor RootCat CartanCat)
  (FG≅Id : NaturalTransformation (compose-Functor F G) (id-Functor RootCat))
  (GF≅Id : NaturalTransformation (compose-Functor G F) (id-Functor CartanCat))
  where

record CartanRoot-Equivalence : Set (lsuc (ℓOC ⊔ ℓMC ⊔ ℓOR ⊔ ℓMR)) where
  field
    forward       : Functor CartanCat RootCat
    backward      : Functor RootCat CartanCat
    forward-back  : NaturalTransformation (compose-Functor forward backward) (id-Functor RootCat)
    back-forward  : NaturalTransformation (compose-Functor backward forward) (id-Functor CartanCat)

CartanRoot-bundle : CartanRoot-Equivalence
CartanRoot-bundle = record
  { forward = F
  ; backward = G
  ; forward-back = FG≅Id
  ; back-forward = GF≅Id
  }
