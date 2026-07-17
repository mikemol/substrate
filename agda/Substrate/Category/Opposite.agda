------------------------------------------------------------------------
-- Substrate.Category.Opposite
--
-- The opposite category C^op of a CategoryOf C: same objects, but with
-- morphism direction flipped. C^op.Mor a b = C.Mor b a.
--
-- The opposite construction is the substrate-native vehicle for
-- absorbing categorical duality: any "dual of X" concept (Comonad =
-- dual of Monad, Colimit = dual of Limit, etc.) can be defined as
-- "X in the opposite category" rather than as a separately-stated
-- dual structure.
--
-- Per [[homology-cohomology-recursion]]: the observed/catalogued
-- recursion makes duals into formal artefacts rather than parallel
-- catalog entries. After Opposite lands, each dual concept becomes
-- a thin alias of its primal counterpart.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Opposite where

open import Substrate.Foundation.Level using (Level)
open import Substrate.Foundation.Eq using (_≡_; sym)

open import Substrate.Category.CategoryOf using (CategoryOf; mkCategoryOf)

------------------------------------------------------------------------
-- Opposite : CategoryOf → CategoryOf.
--
-- Flipped morphisms; identity unchanged; composition reversed;
-- left/right unit laws swap roles; associativity reverses (i.e.,
-- uses sym on the original assoc).
------------------------------------------------------------------------

Opposite : {ℓO ℓM : Level} {Obj : Set ℓO} {Mor : Obj → Obj → Set ℓM}
         → CategoryOf Obj Mor → CategoryOf Obj (λ a b → Mor b a)
Opposite C = mkCategoryOf
  id
  (λ g f → compose f g)
  (λ f → right-id f)
  (λ f → left-id f)
  (λ f g h → sym (assoc h g f))
  where open CategoryOf C
