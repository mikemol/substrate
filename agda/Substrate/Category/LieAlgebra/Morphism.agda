------------------------------------------------------------------------
-- Substrate.Category.LieAlgebra.Morphism
--
-- The morphism layer for L2 LieAlgebra primitives — a Lie-algebra
-- morphism between two Lie algebras is a function on carriers that
-- preserves the bracket:
--   f [x, y] = [f x, f y]
-- (where _·_ is the ACA-bracket).
--
-- L8 of the L-arc; structurally analogous to Z6 [[Cone.Morphism]] +
-- Z7 [[GTorsor.Morphism]] for the L2 LieAlgebra primitive. Foundation
-- for the Lie-algebra category Lie (per [[universal-property-discipline]]).
--
-- Per the substrate convention (Z-arc Grothendieck-closure): every
-- categorical primitive gets a morphism layer via Z1 Morphism so the
-- corresponding objects form a category (and the rest of the
-- Grothendieck-construction infrastructure becomes available).
--
-- The substrate-level Lie-morphism captures bracket preservation
-- only; preservation of additive structure (+V, 0V) is implicit in
-- the underlying-ACA + linear-map structure of concrete instances
-- (e.g., sl₂-morphism, Bivector-Lie morphism).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.LieAlgebra.Morphism where

open import Level using (Level; _⊔_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Category.LieAlgebra using (LieAlgebra)
open import Substrate.Category.Morphism using (Morphism; mkMorphism)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- 1. The bracket-preservation predicate.
--
-- Given two Lie algebras L₁, L₂, the predicate "f preserves the
-- bracket" holds iff for all x, y in L₁.V,
--   f (x [L₁] y) ≡ (f x) [L₂] (f y)
-- where [·] is the bracket _·_ of each Lie algebra.
------------------------------------------------------------------------

preserves-bracket :
  (L₁ L₂ : LieAlgebra {ℓ}) →
  (LieAlgebra.V L₁ → LieAlgebra.V L₂) → Set ℓ
preserves-bracket L₁ L₂ f =
  (x y : LieAlgebra.V L₁) →
  f (LieAlgebra._·_ L₁ x y) ≡ LieAlgebra._·_ L₂ (f x) (f y)

------------------------------------------------------------------------
-- 2. The LieAlgebra-morphism type.
--
-- A Lie-morphism L₁ → L₂ is a Morphism (from Z1) whose preservation
-- predicate is "preserves-bracket."
------------------------------------------------------------------------

LieAlgebraMorphism :
  (L₁ L₂ : LieAlgebra {ℓ}) → Set ℓ
LieAlgebraMorphism L₁ L₂ =
  Morphism (LieAlgebra.V L₁) (LieAlgebra.V L₂) (preserves-bracket L₁ L₂)

------------------------------------------------------------------------
-- 3. Identity Lie-morphism.
--
-- The identity function preserves the bracket trivially: f x = x
-- gives f [x,y] = [x,y] = [f x, f y].
------------------------------------------------------------------------

id-LieAlgebraMorphism :
  (L : LieAlgebra {ℓ}) → LieAlgebraMorphism L L
id-LieAlgebraMorphism L = mkMorphism (λ x → x) (λ _ _ → refl)

------------------------------------------------------------------------
-- 4. Capstone — Lie-algebra morphism layer in place.
--
-- L8 of the L-arc. With L8 landed, Lie algebras form a category
-- (specifically, the category Lie of Lie algebras + bracket-
-- preserving maps).
--
-- Closes the Lie-algebra layer's Grothendieck closure. Concrete
-- usage:
--   * sl₂ → so₃ morphism (after L14 + L15)
--   * Adjoint representation L → End(L) (= the canonical embedding
--     of every L into its own endomorphism Lie algebra)
--   * Lie algebra projection from MonsterLieAlgebra to its Cartan
--     subalgebra (L19's downstream)
--
-- Composition of Lie-morphisms follows from Z1's compose-Morphism +
-- a bracket-preservation-composes lemma (which holds by direct
-- computation: f preserves-bracket + g preserves-bracket ⇒ g∘f
-- preserves-bracket).
--
-- Next: L9 ExteriorAlgebra.Morphism.
------------------------------------------------------------------------
