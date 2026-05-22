------------------------------------------------------------------------
-- Substrate.Category.Colimit
--
-- S3 of the S-arc. Colimit primitive (dual of S2 Limit): for a
-- diagram D : J → C, a colimit is a universal cocone.
--
-- Per the skeleton-as-pullback principle: Limit/Colimit is a 1:2
-- cone (duality witness). With Substrate.Category.Functor.Opposite
-- supplying opposite-Functor, the dual specialization is exactly
-- the primal applied to Opposite-coerced inputs:
--
--   Colimit J C D ≡ Limit (Opposite J) (Opposite C) (opposite-Functor D)
--
-- The apex object lives in C, which has the same Obj-set as
-- Opposite C; the user-side universal-property obligations dualise
-- through the morphism-direction flip on Opposite.
--
-- (Earlier the docstring noted "deferred pending Functor-on-Opposite
-- coercion." That coercion is now Substrate.Category.Functor.Opposite,
-- and this absorption replaces the parallel one-field record.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Colimit where

open import Substrate.Foundation.Level using (Level; _⊔_)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)
open import Substrate.Category.Functor.Opposite using (opposite-Functor)
open import Substrate.Category.Limit using (Limit)
open import Substrate.Category.Opposite using (Opposite)

Colimit :
  {ℓOC ℓMC ℓOJ ℓMJ : Level}
  (J : CategoryOf {ℓOJ} {ℓMJ})
  (C : CategoryOf {ℓOC} {ℓMC})
  (D : Functor J C) → Set _
Colimit J C D = Limit (Opposite J) (Opposite C) (opposite-Functor D)
