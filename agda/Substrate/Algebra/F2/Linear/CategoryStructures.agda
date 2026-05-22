------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.CategoryStructures
--
-- Bundled record of F₂-Linear's structural facets — one field per
-- categorical structure F₂-Linear instantiates.
--
-- Aggregates the per-file As*Category declarations
-- (AsAbelianCategory, AsExactCategory, AsRigidCategory,
-- AsSymmetricMonoidal, AsDaggerCategory) into a single record so
-- callers that want multiple structures at once can supply one value
-- and project. Per-file As* modules remain as the substrate-native
-- catalog entries with per-arc docstring attribution (N7 / N8 /
-- P4 / P8 / P9); they become projection shims over this record.
--
-- AsCompactClosed (O1) is a binary lift (consumes DaggerCategory +
-- SymmetricMonoidal, produces two compact-closed views) and stays
-- as its own per-file module rather than joining this record.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.CategoryStructures where

open import Level using (Level; suc; _⊔_)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.SymmetricMonoidal using (SymmetricMonoidal)
open import Substrate.Category.DaggerCategory using (DaggerCategory)

------------------------------------------------------------------------
-- The bundled record.
--
-- One field per structural facet F₂-Linear inhabits:
--   asAbelianCategory   — F₂-Linear has kernels/cokernels/additive
--                         structure (CategoryOf carrier).
--   asExactCategory     — F₂-Linear admits short exact sequences
--                         (CategoryOf carrier).
--   asRigidCategory     — Every object has a dual; SymmetricMonoidal
--                         carrier refined with rigidity obligations.
--   asSymmetricMonoidal — ⊗ + I + σ with σ² = id.
--   asDaggerCategory    — f† = transpose; f†† = f.
--
-- AsCompactClosed (binary, O1) lives separately.
------------------------------------------------------------------------

record F2LinearCategoryStructures {ℓO ℓM : Level}
  : Set (suc (ℓO ⊔ ℓM)) where
  field
    asAbelianCategory   : CategoryOf {ℓO} {ℓM}
    asExactCategory     : CategoryOf {ℓO} {ℓM}
    asRigidCategory     : SymmetricMonoidal {ℓO} {ℓM}
    asSymmetricMonoidal : SymmetricMonoidal {ℓO} {ℓM}
    asDaggerCategory    : DaggerCategory {ℓO} {ℓM}
