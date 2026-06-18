------------------------------------------------------------------------
-- Substrate.Category.DeloopingGroup
--
-- The Group → GROUPOID half of the Algebra→Category bridge. `Delooping`
-- showed every Monoid is a one-object CategoryOf (BM); this shows that when
-- the monoid is a GROUP, BM is a one-object GROUPOID — every morphism is an
-- isomorphism, with inverse given by the group inverse. The categorical
-- invertibility laws ARE the group's inv-left / inv-right (under the deloop's
-- diagrammatic compose g f = f · g):
--
--   iso-l : compose f (inv f) = (inv f) · f ≡ ε   -- = inv-left
--   iso-r : compose (inv f) f = f · (inv f) ≡ ε   -- = inv-right
--
-- This is the "fix once at the hierarchy level" the categorical-grounding
-- advisory asks for: any Algebra.Group is now provably a substrate groupoid,
-- not just per-module. A leaf bridge module (nothing in Category.* imports it).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.DeloopingGroup where

open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Group using (Group; monoid; inv; inv-left; inv-right)
open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Delooping using (deloop)

private
  variable
    ℓO ℓM : Level

open CategoryOf

------------------------------------------------------------------------
-- A morphism f : Mor a b is an ISOMORPHISM if it has a two-sided inverse.
------------------------------------------------------------------------

record IsIso (C : CategoryOf {ℓO} {ℓM}) {a b : Obj C} (f : Mor C a b) : Set ℓM where
  field
    inv⁻  : Mor C b a
    iso-l : compose C f inv⁻ ≡ id C b
    iso-r : compose C inv⁻ f ≡ id C a

-- C is a GROUPOID iff every morphism is an isomorphism.
IsGroupoid : CategoryOf {ℓO} {ℓM} → Set (ℓO ⊔ ℓM)
IsGroupoid C = {a b : Obj C} (f : Mor C a b) → IsIso C f

------------------------------------------------------------------------
-- THE bridge: delooping a Group yields a groupoid. inverse = group inverse;
-- the iso laws are exactly inv-left / inv-right.
------------------------------------------------------------------------

deloop-group-isGroupoid : {A : Set} (grp : Group A) → IsGroupoid (deloop (monoid grp))
deloop-group-isGroupoid grp f = record
  { inv⁻  = inv grp f
  ; iso-l = inv-left grp f
  ; iso-r = inv-right grp f
  }
