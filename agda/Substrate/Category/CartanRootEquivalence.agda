------------------------------------------------------------------------
-- Substrate.Category.CartanRootEquivalence
--
-- O8 of the O-arc. Equivalence of categories between Cartan-types and
-- RootSystems witnessed by O6 forward + O7 backward + NATURAL ISOMORPHISMS
-- (user-supplied: F ∘ G ≅ Id, G ∘ F ≅ Id). The ≅ is now genuine: the
-- witnesses are `NaturalIsomorphism` (each component invertible), so this is
-- a real equivalence of categories, not a pair of one-directional nat-trans.
-- (An earlier version typed the witnesses as bare NaturalTransformation,
-- which does NOT make F, G an equivalence; Ω2's Category.Iso gave the iso
-- building block and Category.NaturalIsomorphism the natural-iso layer.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor
  using (Functor; id-Functor; compose-Functor)
open import Substrate.Category.NaturalIsomorphism
  using (NaturalIsomorphism)

module Substrate.Category.CartanRootEquivalence
  {ℓOC ℓMC ℓOR ℓMR : Level}
  {ObjCartanCat : Set ℓOC} {MorCartanCat : ObjCartanCat → ObjCartanCat → Set ℓMC}
  {ObjRootCat : Set ℓOR} {MorRootCat : ObjRootCat → ObjRootCat → Set ℓMR}
  (CartanCat : CategoryOf ObjCartanCat MorCartanCat)
  (RootCat : CategoryOf ObjRootCat MorRootCat)
  (F : Functor CartanCat RootCat)
  (G : Functor RootCat CartanCat)
  (FG≅Id : NaturalIsomorphism (compose-Functor F G) (id-Functor RootCat))
  (GF≅Id : NaturalIsomorphism (compose-Functor G F) (id-Functor CartanCat))
  where

record CartanRoot-Equivalence : Set (ℓOC ⊔ ℓMC ⊔ ℓOR ⊔ ℓMR) where
  field
    forward       : Functor CartanCat RootCat
    backward      : Functor RootCat CartanCat
    forward-back  : NaturalIsomorphism (compose-Functor forward backward) (id-Functor RootCat)
    back-forward  : NaturalIsomorphism (compose-Functor backward forward) (id-Functor CartanCat)

CartanRoot-bundle : CartanRoot-Equivalence
CartanRoot-bundle = record
  { forward = F
  ; backward = G
  ; forward-back = FG≅Id
  ; back-forward = GF≅Id
  }
