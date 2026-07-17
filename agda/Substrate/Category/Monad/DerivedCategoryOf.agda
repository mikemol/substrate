------------------------------------------------------------------------
-- Substrate.Category.Monad.DerivedCategoryOf
--
-- The 1:N cone witness for substrate categories arising from a Monad.
--
-- For a category C and a Monad M on C, several derived categories
-- carry substrate-level names: the Kleisli category (R5), the
-- Eilenberg-Moore category (R6), and any other (C, M)-indexed
-- CategoryOf that downstream arcs introduce. Each is a thin
-- substrate naming of a user-supplied CategoryOf instance; the
-- shared shape is exactly:
--
--   (C, M, Derived) ↦ Derived  with substrate-renaming on the output.
--
-- This module names that shared shape — the apex of the 1:N cone
-- whose legs are KleisliCategory / EilenbergMooreCategory / etc.
-- Each leg becomes a thin module that `open`s this skeleton and
-- renames `monad-derived-Category` to its specialised handle.
--
-- Per the skeleton-as-pullback principle: this skeleton is the
-- *witness*; KleisliCategory and EilenbergMooreCategory are the
-- *projections*. Adding a new "category-of-monad" specialisation
-- in the future means renaming one extra leg from this skeleton —
-- no new substrate shape is needed.
--
-- Per [[user-rosetta-code-contrastive-pedagogy]]: the substrate
-- names the abstraction (DerivedCategoryOf) so each downstream
-- specialisation reads as a contrastive substrate-vocabulary
-- entry on the same underlying pattern.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Monad using (Monad)

module Substrate.Category.Monad.DerivedCategoryOf
  {ℓO ℓM : Level}
  {ObjC : Set ℓO} {MorC : ObjC → ObjC → Set ℓM}
  (C : CategoryOf ObjC MorC)
  (M : Monad C)
  {ObjDerived : Set ℓO} {MorDerived : ObjDerived → ObjDerived → Set ℓM}
  (Derived : CategoryOf ObjDerived MorDerived)
  where

monad-derived-Category : CategoryOf ObjDerived MorDerived
monad-derived-Category = Derived
