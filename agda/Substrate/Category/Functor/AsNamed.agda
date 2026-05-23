------------------------------------------------------------------------
-- Substrate.Category.Functor.AsNamed
--
-- The 1:N cone witness for substrate-level naming of a Functor.
--
-- Many substrate sites name a user-supplied Functor under a specific
-- handle (Aut as a functor, CategoryOf as a meta-functor, U as the
-- universal-enveloping functor, S1-Lift as a functor, …). Each is a
-- thin substrate-naming of a user-supplied Functor; the shared
-- shape is exactly:
--
--   (F : Functor S T) ↦ F  with substrate-renaming on the output.
--
-- This module names that shared shape — the apex of the 1:N cone
-- whose legs are AutomorphismGroup.AsFunctor,
-- CategoryOf.AsFunctor, GrothendieckConstruction.AsFunctor,
-- LieAlgebra.AsFunctor, ExteriorAlgebra.AsFunctor,
-- UniversalEnvelopingAlgebra.AsFunctor, PrimeFactoredGauge.AsFunctor,
-- S1-Lift.AsFunctor, S2-Lift.AsFunctor, Coxeter.AsCartanType.Functor,
-- CartanType.AsCoxeter.Functor, JordanAlgebra.UnderlyingCNAA, …
--
-- Each leg opens this skeleton and renames `named-Functor` to its
-- site-specific handle.
--
-- Per [[project-named-categorical-structure-skeletons]] (the
-- skeleton-as-pullback principle): this skeleton is the *witness*;
-- the substrate-named leg modules are the *projections*. Adding a
-- new "Functor at site X" specialisation in the future means one
-- open + rename — no new substrate shape needed.
--
-- Siblings: Category.DaggerCategory.AsNamed,
-- Category.SymmetricMonoidal.AsNamed (same pattern for the named
-- structure records).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.Functor.AsNamed
  {ℓOS ℓMS ℓOT ℓMT : Level}
  (Source : CategoryOf {ℓOS} {ℓMS})
  (Target : CategoryOf {ℓOT} {ℓMT})
  (F : Functor Source Target)
  where

named-Functor : Functor Source Target
named-Functor = F
