------------------------------------------------------------------------
-- Substrate.Category.NaturalIsomorphism
--
-- A NATURAL ISOMORPHISM α : F ≅ G — a natural transformation each of whose
-- components is an isomorphism (Category.Iso.IsIso) in the target category.
-- This is the honest witness of "F and G are naturally isomorphic," and the
-- data an EQUIVALENCE OF CATEGORIES requires (F∘G ≅ Id, G∘F ≅ Id with the ≅
-- meaning natural ISO, not a bare nat-trans).
--
-- Modelled on the wedge's `Algebra.Wedge.Iso.WedgeIso` (fwd + bwd + round-
-- trips): here the "bwd + round-trips" are packaged as pointwise IsIso, which
-- needs no vertical composition of nat-transformations (just per-component
-- inverses in D). Continues Ω2 (Group→groupoid / Category.Iso).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.NaturalIsomorphism where

open import Substrate.Foundation.Level using (Level; _⊔_)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)
open import Substrate.Category.NaturalTransformation
  using (NaturalTransformation; id-NaturalTransformation)
open import Substrate.Category.Iso using (IsIso; id-IsIso)

private
  variable
    ℓOC ℓMC ℓOD ℓMD : Level

------------------------------------------------------------------------
-- NaturalIsomorphism F G — a nat-trans F ⇒ G that is pointwise an iso.
------------------------------------------------------------------------

record NaturalIsomorphism
  {ObjC : Set ℓOC} {MorC : ObjC → ObjC → Set ℓMC}
  {ObjD : Set ℓOD} {MorD : ObjD → ObjD → Set ℓMD}
  {C : CategoryOf ObjC MorC}
  {D : CategoryOf ObjD MorD}
  (F G : Functor C D) : Set (ℓOC ⊔ ℓMC ⊔ ℓMD) where

  field
    transformation : NaturalTransformation F G
    -- every component is invertible in D (the "≅", not merely a "⇒").
    component-iso  :
      (a : ObjC) → IsIso D (NaturalTransformation.components transformation a)

open NaturalIsomorphism public

------------------------------------------------------------------------
-- Identity natural isomorphism: the identity nat-trans, pointwise the
-- identity iso.
------------------------------------------------------------------------

id-NaturalIsomorphism :
  {ObjC : Set ℓOC} {MorC : ObjC → ObjC → Set ℓMC}
  {ObjD : Set ℓOD} {MorD : ObjD → ObjD → Set ℓMD}
  {C : CategoryOf ObjC MorC}
  {D : CategoryOf ObjD MorD}
  (F : Functor C D) → NaturalIsomorphism F F
id-NaturalIsomorphism {D = D} F = record
  { transformation = id-NaturalTransformation F
  ; component-iso  = λ a → id-IsIso D (Functor.F-obj F a)
  }
