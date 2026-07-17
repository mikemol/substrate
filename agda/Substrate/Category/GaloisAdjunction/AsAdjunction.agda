------------------------------------------------------------------------
-- Substrate.Category.GaloisAdjunction.AsAdjunction
--
-- O4 of the O-arc. Substrate-level naming of the GaloisAdjunction as a
-- categorical adjunction: bundles N9 η + ε. (NOT "full" — the triangle
-- identities are USER OBLIGATIONS supplied separately, not fields/lemmas
-- here; so this is the η/ε bundle, not yet a coherence-complete adjunction.)
--
-- Per [[universal-property-discipline]]: N9 named the unit + counit;
-- O4 bundles them with the triangle identity obligations into a
-- complete adjunction object. EMERGENT orphan from the N-arc audit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor
  using (Functor; id-Functor; compose-Functor)
open import Substrate.Category.NaturalTransformation
  using (NaturalTransformation)

module Substrate.Category.GaloisAdjunction.AsAdjunction
  {ℓOC ℓMC ℓOD ℓMD : Level}
  {ObjC : Set ℓOC} {MorC : ObjC → ObjC → Set ℓMC}
  {ObjD : Set ℓOD} {MorD : ObjD → ObjD → Set ℓMD}
  (C : CategoryOf ObjC MorC)
  (D : CategoryOf ObjD MorD)
  (F : Functor C D)
  (G : Functor D C)
  (η : NaturalTransformation (id-Functor C) (compose-Functor G F))
  (ε : NaturalTransformation (compose-Functor F G) (id-Functor D))
  -- Triangle identities are user obligations; the substrate names
  -- the bundled adjunction.
  where

------------------------------------------------------------------------
-- Adjunction-record: bundles F, G, η, ε. Triangle identities are
-- user-supplied separately as downstream witnesses.
------------------------------------------------------------------------

record GaloisAdjunction-AsAdjunction : Set (ℓOC ⊔ ℓMC ⊔ ℓOD ⊔ ℓMD) where
  field
    forward  : Functor C D
    backward : Functor D C
    unit     : NaturalTransformation (id-Functor C) (compose-Functor backward forward)
    counit   : NaturalTransformation (compose-Functor forward backward) (id-Functor D)

GaloisAdjunction-bundle : GaloisAdjunction-AsAdjunction
GaloisAdjunction-bundle = record { forward = F ; backward = G ; unit = η ; counit = ε }

------------------------------------------------------------------------
-- Substrate-named full adjunction; triangle identities deferred.
------------------------------------------------------------------------
