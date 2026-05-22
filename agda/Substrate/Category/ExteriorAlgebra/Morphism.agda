------------------------------------------------------------------------
-- Substrate.Category.ExteriorAlgebra.Morphism
--
-- The morphism layer for L3 ExteriorAlgebra primitives — an exterior-
-- algebra morphism between two Λ-algebras is a function on the
-- graded carriers that preserves the wedge product:
--   f (x ∧ y) ≡ (f x) ∧ (f y)
--
-- L9 of the L-arc; structurally analogous to L8 [[LieAlgebra.Morphism]]
-- for the L3 ExteriorAlgebra primitive. Foundation for the category
-- ExtAlg of exterior algebras + wedge-preserving maps.
--
-- The substrate-level minimum: wedge preservation. Concrete instances
-- may additionally require preservation of the V_base inclusion +
-- additive structure; these layer on top.
--
-- Per the Z-arc Grothendieck-closure convention: every categorical
-- primitive gets a morphism layer via Z1 Morphism.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ExteriorAlgebra.Morphism where

open import Level using (Level; _⊔_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Category.ExteriorAlgebra using (ExteriorAlgebra)
open import Substrate.Category.Morphism using (Morphism; mkMorphism)

private
  variable
    ℓ ℓB : Level

------------------------------------------------------------------------
-- 1. The wedge-preservation predicate.
--
-- Given two exterior algebras E₁, E₂, the predicate "f preserves the
-- wedge" holds iff for all x, y in E₁.V_alg,
--   f (x ∧[E₁] y) ≡ (f x) ∧[E₂] (f y)
------------------------------------------------------------------------

preserves-wedge :
  (E₁ E₂ : ExteriorAlgebra {ℓ} {ℓB}) →
  (ExteriorAlgebra.V_alg E₁ → ExteriorAlgebra.V_alg E₂) → Set ℓ
preserves-wedge E₁ E₂ f =
  (x y : ExteriorAlgebra.V_alg E₁) →
  f (ExteriorAlgebra._∧_ E₁ x y) ≡ ExteriorAlgebra._∧_ E₂ (f x) (f y)

------------------------------------------------------------------------
-- 2. The ExteriorAlgebra-morphism type.
------------------------------------------------------------------------

ExteriorAlgebraMorphism :
  (E₁ E₂ : ExteriorAlgebra {ℓ} {ℓB}) → Set ℓ
ExteriorAlgebraMorphism E₁ E₂ =
  Morphism (ExteriorAlgebra.V_alg E₁) (ExteriorAlgebra.V_alg E₂)
           (preserves-wedge E₁ E₂)

------------------------------------------------------------------------
-- 3. Identity exterior-algebra morphism.
------------------------------------------------------------------------

id-ExteriorAlgebraMorphism :
  (E : ExteriorAlgebra {ℓ} {ℓB}) → ExteriorAlgebraMorphism E E
id-ExteriorAlgebraMorphism E = mkMorphism (λ x → x) (λ _ _ → refl)

------------------------------------------------------------------------
-- 4. Capstone — exterior-algebra morphism layer in place.
--
-- L9 of the L-arc. With L9 landed, exterior algebras form a category
-- (ExtAlg). Concrete usage:
--   * Λ(V) → Λ(W) induced from V → W (the functoriality of Λ)
--   * Hodge ★ as a wedge-anti-morphism (the substrate's existing
--     HodgeStar is a graded-algebra-twisted-morphism; full
--     formalisation would extend this layer)
--   * Bivector ∧²(F₂⁴) self-morphisms (= the F₂-linear endomorphisms
--     of Vector 6 that respect the wedge structure)
--
-- Next: L10 AntiCommutativeAlgebra.Morphism (the base-level
-- morphism layer underneath both L8 and L9).
------------------------------------------------------------------------
