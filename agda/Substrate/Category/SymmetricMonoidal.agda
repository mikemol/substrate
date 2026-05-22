------------------------------------------------------------------------
-- Substrate.Category.SymmetricMonoidal
--
-- The categorical primitive for symmetric monoidal categories.
--
-- A symmetric monoidal category extends a category C with:
--   * a tensor product ⊗ : C × C → C (bifunctor)
--   * a unit object I ∈ C
--   * a symmetry σ : a ⊗ b ≅ b ⊗ a satisfying σ_{b,a} ∘ σ_{a,b} = id
--   * coherence diagrams (pentagon, triangle, hexagon)
--
-- M3 of the M-arc. Foundation for tensor-bearing primitives (M5
-- ExteriorAlgebra as monoidal-Vect → graded-monoidal-ExtAlg; future
-- tensor compatibility of Λ, U, ★).
--
-- Per substrate convention (Z5 CategoryOf, M1 Functor): the
-- substrate-level primitive captures the OBJECT-level + IMMEDIATE
-- σ-INVOLUTION structure; the tensor's bifunctoriality on morphisms
-- + full coherence diagrams (pentagon, triangle, hexagon) are
-- DOWNSTREAM specialisation slices. Concrete instances at small
-- monoidal categories (Vect, Set, ChainComplex) can supply the
-- coherence; the substrate's M3 is the structural carrier.
--
-- Per [[universal-property-discipline]]: the symmetric-monoidal
-- universal property is "the free symmetric-monoidal category on a
-- generating set" (= the PROP / operadic side); the substrate's
-- M3 captures the object level + symmetry-involution and defers
-- the operadic universal property.
--
-- Per [[grothendieck-coherence-rule]]: M3 + M4 (DaggerCategory)
-- complete the substrate's higher-categorical infrastructure — once
-- ⊗ and † are first-class primitives, downstream structures (Λ, U,
-- ★) can be required to commute with them, structurally enforcing
-- compatibility instead of relying on author discipline.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.SymmetricMonoidal where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.CategoryOf using (CategoryOf)

private
  variable
    ℓO ℓM : Level

------------------------------------------------------------------------
-- The SymmetricMonoidal record.
--
-- Bundles:
--   * base : CategoryOf — the underlying category
--   * _⊗o_ : Obj → Obj → Obj — tensor on objects
--   * I : Obj — unit object
--   * σ : ∀ a b → Mor (a ⊗o b) (b ⊗o a) — symmetry
--   * σ-involution : ∀ a b → compose (σ b a) (σ a b) ≡ id (a ⊗o b)
--
-- The tensor's morphism action + pentagon/triangle/hexagon coherence
-- are downstream specialisation slices; the substrate-level primitive
-- carries the structural carrier + immediate σ-involution only.
------------------------------------------------------------------------

record SymmetricMonoidal : Set (lsuc (ℓO ⊔ ℓM)) where
  constructor mkSymmetricMonoidal

  field
    base : CategoryOf {ℓO} {ℓM}

  private
    module C = CategoryOf base

  field
    _⊗o_           : C.Obj → C.Obj → C.Obj
    I              : C.Obj
    σ              : (a b : C.Obj) → C.Mor (a ⊗o b) (b ⊗o a)
    σ-involution   : (a b : C.Obj) →
                     C.compose (σ b a) (σ a b) ≡ C.id (a ⊗o b)

------------------------------------------------------------------------
-- Capstone — symmetric monoidal primitive in place.
--
-- M3 of the M-arc. Substrate's first symmetric-monoidal structural
-- primitive. After M3:
--   * Tensor-bearing primitives (Vect, ChainComplex, Λ at degree-2)
--     can name their monoidal structure via M3
--   * Symmetry-involution (= σ² = id) is captured at the substrate
--     primitive layer
--
-- Per [[universal-property-discipline]]: full strict-symmetric-
-- monoidal category requires coherence diagrams (pentagon, triangle,
-- hexagon). These are downstream specialisation slices; the
-- substrate's M3 is the minimum-axiom carrier.
--
-- Concrete usage:
--   * Vect with ⊗ = tensor product, I = base field
--   * Set with ⊗ = cartesian product, I = singleton
--   * ChainComplex with ⊗ = total complex of tensor, I = ℤ in degree 0
--   * GradedAlgebra with ⊗ = graded tensor + sign rule (sym = (-1)^{|x||y|})
--
-- Next: M4 DaggerCategory (involutive structure for ★, complex
-- conjugation, adjoint).
------------------------------------------------------------------------
