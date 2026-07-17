------------------------------------------------------------------------
-- Substrate.Category.NaturalTransformation.AsNamed
--
-- The 1:N cone witness for substrate-level naming of a
-- NaturalTransformation. Sibling of Category.Functor.AsNamed,
-- Category.DaggerCategory.AsNamed, Category.SymmetricMonoidal.AsNamed
-- (the AsNamed family — see [[project-named-categorical-structure-
-- skeletons]]).
--
-- Many substrate sites name a user-supplied NaturalTransformation under
-- a specific handle (Hodge ★ as Λᵏ ⇒ Λⁿ⁻ᵏ, gauge-torsor transports,
-- …). Each is a thin substrate-naming of a user-supplied
-- NaturalTransformation; the shared shape is exactly:
--
--   (α : NaturalTransformation F G) ↦ α  with substrate-renaming.
--
-- This module names that shared shape — the apex of the 1:N cone whose
-- legs are HodgeStar.AsNaturalTransformation,
-- ReservedBridge.GaugeTorsor.AsNaturalTransformation, …. Each leg opens
-- this skeleton and renames `named-NaturalTransformation` to its
-- site-specific handle. Adding a new "NaturalTransformation at site X"
-- specialisation means one open + rename — no new substrate shape.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)
open import Substrate.Category.NaturalTransformation
  using (NaturalTransformation)

module Substrate.Category.NaturalTransformation.AsNamed
  {ℓOS ℓMS ℓOT ℓMT : Level}
  {ObjSource : Set ℓOS} {MorSource : ObjSource → ObjSource → Set ℓMS}
  {ObjTarget : Set ℓOT} {MorTarget : ObjTarget → ObjTarget → Set ℓMT}
  (Source : CategoryOf ObjSource MorSource)
  (Target : CategoryOf ObjTarget MorTarget)
  (F G : Functor Source Target)
  (α : NaturalTransformation F G)
  where

named-NaturalTransformation : NaturalTransformation F G
named-NaturalTransformation = α
