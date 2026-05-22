------------------------------------------------------------------------
-- Substrate.Category.DaggerCategory
--
-- The categorical primitive for dagger categories.
--
-- A dagger category extends a category C with an involutive
-- contravariant identity-on-objects functor † : C^op → C:
--   * f† : Mor b a   for every f : Mor a b
--   * (id a)† ≡ id a
--   * (g ∘ f)† ≡ f† ∘ g†
--   * f†† ≡ f
--
-- M4 of the M-arc. Foundation for the involutive structure of:
--   * Hodge ★ (★ ★ = ±id; canonical dagger candidate)
--   * Adjoint operators in finite-dim inner-product spaces
--   * F₂-Linear bijections (Bijection's two-sided inverse IS a
--     dagger structure when the inverse coincides with adjoint)
--   * Quantum-like primitives (deferred)
--
-- Per [[categorical-name-first]]: "dagger category" is the standard
-- name (Selinger 2007; categorical quantum mechanics). The universal
-- property: † is a contravariant identity-on-objects functor with
-- †² = id. Captures "morphisms have adjoints / inverses" structurally.
--
-- Per [[grothendieck-coherence-rule]]: dagger structure is the
-- mechanism by which the substrate's involution-bearing primitives
-- (HodgeStar with ★² = id; Bijection; HasOrder at 2) acquire a
-- HIGHER-CATEGORICAL handle. Without M4, ★² = id is a per-instance
-- property; WITH M4, it instantiates the universal involution
-- structure.
--
-- Per [[torsion-element-universal]]: HasOrder at order 2 IS the
-- substrate's local dagger structure on a single endomorphism;
-- DaggerCategory globalises this to the level of an entire category.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.DaggerCategory where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.CategoryOf using (CategoryOf)

private
  variable
    ℓO ℓM : Level

------------------------------------------------------------------------
-- The DaggerCategory record.
--
-- Bundles:
--   * base : CategoryOf — the underlying category
--   * _† : ∀ {a b} → Mor a b → Mor b a — the dagger
--   * id-† : ∀ a → (id a)† ≡ id a
--   * compose-† : ∀ {a b c} (f : Mor a b) (g : Mor b c) →
--                 (compose g f)† ≡ compose f† g†
--   * involution : ∀ {a b} (f : Mor a b) → f†† ≡ f
------------------------------------------------------------------------

record DaggerCategory : Set (lsuc (ℓO ⊔ ℓM)) where
  constructor mkDaggerCategory

  field
    base : CategoryOf {ℓO} {ℓM}

  private
    module C = CategoryOf base

  field
    _† : {a b : C.Obj} → C.Mor a b → C.Mor b a
    id-†
      : (a : C.Obj) → (C.id a) † ≡ C.id a
    compose-†
      : {a b c : C.Obj} (f : C.Mor a b) (g : C.Mor b c) →
        (C.compose g f) † ≡ C.compose (f †) (g †)
    involution
      : {a b : C.Obj} (f : C.Mor a b) → ((f †) †) ≡ f

------------------------------------------------------------------------
-- Capstone — dagger category primitive in place.
--
-- M4 of the M-arc. Closes the M1-M4 higher-categorical foundation:
--   M1 Functor       — 1-cells (functors between categories)
--   M2 NaturalTransformation — 2-cells (between functors)
--   M3 SymmetricMonoidal — ⊗ + I + σ structure
--   M4 DaggerCategory — involutive † structure (THIS)
--
-- Combined: substrate has the 4 pieces of a "symmetric monoidal
-- dagger category" — the canonical higher-categorical setting for
-- categorical quantum mechanics, TQFT, and the substrate's own
-- involution-bearing primitives.
--
-- Per [[universal-property-discipline]]: M3 + M4 jointly capture
-- "tensor + symmetry + dagger" structure. Concrete instances that
-- need ALL of them simultaneously (= symmetric monoidal dagger
-- category) supply them via M3-instance + M4-instance + compatibility
-- coherence (tensor-of-daggers, σ-self-dagger, etc.); the substrate's
-- primitives M3/M4 are the building blocks.
--
-- Concrete usage anticipated:
--   * FdHilb (finite-dim Hilbert spaces over ℂ) with † = adjoint
--   * F₂-Linear with † = transpose (= adjoint for the canonical
--     bilinear form)
--   * Cobordism / TQFT (deferred)
--   * F₂-Bijection: forward + backward IS the dagger structure
--
-- After M4: the substrate's HIGHER-CATEGORICAL infrastructure is
-- structurally complete for the M-arc's downstream functorial
-- closure. M5-M9 land concrete L-arc primitives in this
-- infrastructure.
--
-- Next: M5 ExteriorAlgebra.AsFunctor.
------------------------------------------------------------------------
