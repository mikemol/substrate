------------------------------------------------------------------------
-- Substrate.Category.AntiCommutativeAlgebra.Morphism
--
-- The morphism layer for L1 AntiCommutativeAlgebra primitives — an
-- ACA morphism is a function on carriers that preserves the
-- bilinear product:
--   f (x · y) ≡ (f x) · (f y)
--
-- L10 of the L-arc. The base-level morphism underneath both L8
-- LieAlgebra.Morphism (LieAlgebra extends ACA with Jacobi; Lie-
-- morphism IS ACA-morphism on the underlying ACA) and L9
-- ExteriorAlgebra.Morphism (graded-ACA extension).
--
-- Per the Z-arc Grothendieck-closure convention: every categorical
-- primitive gets a morphism layer via Z1 Morphism. With L10 landed,
-- the base ACA category exists and L8 / L9 sit on top as
-- specialisations.
--
-- Closes the L8-L10 mini-arc: morphism layers for L1-L3 are all in
-- place, mirroring the Z6-Z7 Cone/GTorsor morphism layers from the
-- Z-arc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.AntiCommutativeAlgebra.Morphism where

open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Category.AntiCommutativeAlgebra
  using (AntiCommutativeAlgebra)
open import Substrate.Category.Morphism using (Morphism; mkMorphism)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- 1. The product-preservation predicate.
------------------------------------------------------------------------

preserves-product :
  (A₁ A₂ : AntiCommutativeAlgebra {ℓ}) →
  (AntiCommutativeAlgebra.V A₁ → AntiCommutativeAlgebra.V A₂) → Set ℓ
preserves-product A₁ A₂ f =
  (x y : AntiCommutativeAlgebra.V A₁) →
  f (AntiCommutativeAlgebra._·_ A₁ x y) ≡
  AntiCommutativeAlgebra._·_ A₂ (f x) (f y)

------------------------------------------------------------------------
-- 2. The AntiCommutativeAlgebra-morphism type.
------------------------------------------------------------------------

AntiCommutativeAlgebraMorphism :
  (A₁ A₂ : AntiCommutativeAlgebra {ℓ}) → Set ℓ
AntiCommutativeAlgebraMorphism A₁ A₂ =
  Morphism (AntiCommutativeAlgebra.V A₁)
           (AntiCommutativeAlgebra.V A₂)
           (preserves-product A₁ A₂)

------------------------------------------------------------------------
-- 3. Identity ACA morphism.
------------------------------------------------------------------------

id-AntiCommutativeAlgebraMorphism :
  (A : AntiCommutativeAlgebra {ℓ}) → AntiCommutativeAlgebraMorphism A A
id-AntiCommutativeAlgebraMorphism A = mkMorphism (λ x → x) (λ _ _ → refl)

------------------------------------------------------------------------
-- 4. Capstone — ACA morphism layer + L8-L10 mini-arc closed.
--
-- L10 of the L-arc. With L8 + L9 + L10 landed:
--   * L1 ACA, L2 LieAlgebra, L3 ExteriorAlgebra each have morphism
--     layers
--   * The categories ACA, Lie, ExtAlg are all available
--   * L2 Lie sits over L1 ACA: a Lie-morphism IS an ACA-morphism
--     on the underlying ACA (LieAlgebra.acaBase) that additionally
--     respects Jacobi (which is automatic via preserves-bracket =
--     preserves-product)
--   * L3 ExteriorAlgebra has its own preserves-wedge predicate that
--     specialises the ACA pattern to the graded setting
--
-- Closes the L-arc's mini-arc on morphisms (L8-L10) mirroring the
-- Z-arc's morphism additions (Z6 Cone.Morphism + Z7 GTorsor.Morphism)
-- + L8 LieAlgebra.Morphism + L9 ExteriorAlgebra.Morphism.
--
-- Next: Phase Λ'' (L11-L15) — RootSystem / CartanType bridge +
-- Coxeter-AsCartanType + sl₂ + so₃ concrete instances.
------------------------------------------------------------------------
