------------------------------------------------------------------------
-- Substrate.Category.Iso
--
-- The general categorical ISOMORPHISM, given its proper home. A morphism
-- f : Mor C a b is an iso when it has a two-sided inverse; C is a GROUPOID
-- when every morphism is. These were first defined inside
-- `Category.DeloopingGroup` (the Group→groupoid bridge, Ω2), but they are
-- pure CategoryOf notions with nothing group-specific — so they live here,
-- and DeloopingGroup re-exports them. This is the building block for
-- `Category.NaturalIsomorphism` (a nat-trans that is pointwise an iso),
-- modelled on the wedge's `WedgeIso` (fwd + bwd + round-trips).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Iso where

open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Category.CategoryOf using (CategoryOf)

private
  variable
    ℓO ℓM : Level

open CategoryOf

------------------------------------------------------------------------
-- IsIso C f — f has a two-sided inverse (the iso laws are compose-with-
-- inverse = identity, in C).
------------------------------------------------------------------------

record IsIso (C : CategoryOf {ℓO} {ℓM}) {a b : Obj C} (f : Mor C a b) : Set ℓM where
  field
    inv⁻  : Mor C b a
    iso-l : compose C f inv⁻ ≡ id C b
    iso-r : compose C inv⁻ f ≡ id C a

------------------------------------------------------------------------
-- IsGroupoid C — every morphism is an isomorphism.
------------------------------------------------------------------------

IsGroupoid : CategoryOf {ℓO} {ℓM} → Set (ℓO ⊔ ℓM)
IsGroupoid C = {a b : Obj C} (f : Mor C a b) → IsIso C f

------------------------------------------------------------------------
-- The identity morphism is an isomorphism (it is its own inverse).
------------------------------------------------------------------------

id-IsIso : (C : CategoryOf {ℓO} {ℓM}) (o : Obj C) → IsIso C (id C o)
id-IsIso C o = record
  { inv⁻  = id C o
  ; iso-l = left-id C (id C o)
  ; iso-r = left-id C (id C o)
  }
