------------------------------------------------------------------------
-- Substrate.Category.CategoryOf.AsFunctor
--
-- Substrate-level naming of CategoryOf(_) as a functor — the
-- substrate's "2-functor from primitive data to its category."
--
-- N2 of the N-arc.
--
-- Z5 CategoryOf packages "primitive type + morphism notion + axioms"
-- as a single substrate CategoryOf value. The assignment "primitive-
-- data P ↦ category-of-P-instances" is itself functorial in P (in a
-- meta-category whose objects are substrate primitives + whose
-- morphisms are primitive-respecting transformations).
--
-- Per [[grothendieck-coherence-rule]]: this is a 2-functor between
-- meta-categories; the substrate-level minimum captures the 1-functor
-- view (PrimitiveMeta → Cat) via M1 Functor where Cat = (substrate's
-- meta-category of CategoryOf instances).
--
-- Module-parametric per substrate convention.
--
-- HIGH PRIORITY orphan: CategoryOf is structurally pervasive across
-- the substrate's Z-arc; the functorial view enables next-iteration
-- Grothendieck constructions over substrate primitives generically.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.CategoryOf.AsFunctor
  {ℓOP ℓMP ℓOC ℓMC : Level}
  -- The meta-category of substrate primitives + primitive-respecting
  -- transformations (user-supplied; conceptually a sub-category of
  -- Set).
  (PrimitiveMeta : CategoryOf {ℓOP} {ℓMP})
  -- The meta-category of CategoryOf instances + functors between them.
  (CatMeta : CategoryOf {ℓOC} {ℓMC})
  -- The CategoryOf assignment functor.
  (CategoryOf-assignment : Functor PrimitiveMeta CatMeta)
  where

------------------------------------------------------------------------
-- 1. CategoryOf as the substrate's named meta-functor.
------------------------------------------------------------------------

open import Substrate.Category.Functor.AsNamed
  PrimitiveMeta CatMeta CategoryOf-assignment public
  renaming (named-Functor to CategoryOf-Functor)
------------------------------------------------------------------------
-- 2. Capstone — CategoryOf as M1 Functor (meta-level).
--
-- N2 of the N-arc. With N2 landed, the "primitive ↦ category-of-
-- primitive-instances" assignment is a substrate Functor; downstream
-- substrate primitives can name their CategoryOf instances functorially.
--
-- Per [[universal-property-discipline]]: this functor exhibits the
-- substrate's "category-of" assignment as a structural 1-functor,
-- one Grothendieck-iteration short of the full 2-functor it actually
-- is (the substrate-pragmatic minimum).
--
-- Next: N3 GrothendieckConstruction.AsFunctor.
------------------------------------------------------------------------
