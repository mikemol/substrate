------------------------------------------------------------------------
-- Substrate.Category.SymmetricMonoidal.AsNamed
--
-- The 1:N cone witness for substrate-level naming of a
-- SymmetricMonoidal.
--
-- Several substrate sites name a user-supplied SymmetricMonoidal
-- under a specific handle (Hodge ★ self-dual morphism context;
-- Bivector compact-closed-dual context; F₂-Linear bijection SM
-- context; etc.). Each is a thin substrate-naming of a user-supplied
-- SymmetricMonoidal; the shared shape is exactly:
--
--   (SM) ↦ SM  with substrate-renaming on the output.
--
-- Per the skeleton-as-pullback principle: this skeleton is the
-- *witness*; substrate-named leg modules are the *projections*.
--
-- Sibling: Substrate.Category.DaggerCategory.AsNamed (same pattern
-- for DaggerCategory). Two-structure sites (SM + Dag) open both
-- skeletons; the two projections compose without needing a separate
-- combined skeleton.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.SymmetricMonoidal using (SymmetricMonoidal)

module Substrate.Category.SymmetricMonoidal.AsNamed
  {ℓO ℓM : Level}
  {Obj : Set ℓO} {Mor : Obj → Obj → Set ℓM}
  (SM : SymmetricMonoidal Obj Mor)
  where

named-SymmetricMonoidal : SymmetricMonoidal Obj Mor
named-SymmetricMonoidal = SM
