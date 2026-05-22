------------------------------------------------------------------------
-- Substrate.Category.DaggerCategory.AsNamed
--
-- The 1:N cone witness for substrate-level naming of a DaggerCategory.
--
-- Several substrate sites name a user-supplied DaggerCategory under
-- a specific handle (Hodge ★ as a self-dagger endomap; F₂-Linear
-- bijection sub-category as a dagger category; future analogues).
-- Each is a thin substrate-naming of a user-supplied DaggerCategory;
-- the shared shape is exactly:
--
--   (Dag) ↦ Dag  with substrate-renaming on the output.
--
-- This module names that shared shape — the apex of the 1:N cone
-- whose legs are HodgeStar.AsDaggerEndomap, Bijection.AsDagger, etc.
-- Each leg opens this skeleton and renames `named-DaggerCategory` to
-- its site-specific handle.
--
-- Per the skeleton-as-pullback principle: this skeleton is the
-- *witness*; the substrate-named leg modules are the *projections*.
-- Adding a new "DaggerCategory at site X" specialisation in the
-- future means one open + rename — no new substrate shape is needed.
--
-- Sibling: Substrate.Category.SymmetricMonoidal.AsNamed (same
-- pattern for SymmetricMonoidal).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.DaggerCategory using (DaggerCategory)

module Substrate.Category.DaggerCategory.AsNamed
  {ℓO ℓM : Level}
  (Dag : DaggerCategory {ℓO} {ℓM})
  where

named-DaggerCategory : DaggerCategory
named-DaggerCategory = Dag
