------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.AsDaggerCategory
--
-- Substrate-level naming of F₂-Linear as a dagger category.
--
-- N8 of the N-arc.
--
-- F₂-Linear carries canonical dagger structure:
--   * For f : V → W (F₂-linear map), f† = the transpose
--     W → V (= adjoint w.r.t. the canonical bilinear form)
--   * (id)† = id (transpose of identity matrix is identity)
--   * (g ∘ f)† = f† ∘ g† (transpose-of-product reverses order)
--   * f†† = f (transpose is involutive)
--
-- Per [[grothendieck-coherence-rule]]: closes the M-arc OrphanAudit
-- row "F₂-Linear should be DaggerCategory." After N7+N8, F₂-Linear
-- is a symmetric monoidal dagger category at the substrate primitive
-- layer — the structural setting for quantum-like / TQFT-like
-- substrate primitives.
--
-- Per [[torsion-element-universal]]: F₂-Linear's HasOrder-at-2
-- endomaps (Hodge ★ being the canonical example) sit inside this
-- dagger category as the involutive 1-cells.
--
-- Projects the dagger-category facet from the bundled
-- F2LinearCategoryStructures record.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Algebra.F2.Linear.CategoryStructures
  using (F2LinearCategoryStructures)
open import Substrate.Category.DaggerCategory using (DaggerCategory)

module Substrate.Algebra.F2.Linear.AsDaggerCategory
  {ℓO ℓM : Level}
  (structures : F2LinearCategoryStructures {ℓO} {ℓM})
  where

------------------------------------------------------------------------
-- 1. F₂-Linear as the substrate's named DaggerCategory instance.
------------------------------------------------------------------------

F2Linear-AsDaggerCategory : DaggerCategory
F2Linear-AsDaggerCategory =
  F2LinearCategoryStructures.asDaggerCategory structures

------------------------------------------------------------------------
-- 2. Capstone — F₂-Linear as M4 DaggerCategory.
--
-- N8 of the N-arc. With N7 + N8 landed, F₂-Linear is a SYMMETRIC
-- MONOIDAL DAGGER CATEGORY at the substrate primitive layer — the
-- canonical higher-categorical setting for:
--   * Quantum-like primitives (deferred to dedicated arc)
--   * TQFT-style cobordism categories (deferred)
--   * The substrate's own F₂-Linear-Bijection with two-sided inverse
--     IS the dagger structure on the bijection sub-category
--   * Hodge ★ at HodgeDim4 = self-dagger (HasOrder 2) endomap inside
--     this dagger category
--
-- Per [[reserved-selfdual-bijection-gauge]]: the 168 F₂-linear
-- bijections at HodgeDim4 form a GL(3, F₂)-torsor INSIDE F₂-Linear-
-- as-DaggerCategory; the dagger gives each bijection its inverse-
-- as-adjoint witness.
--
-- After N7+N8: substrate's F₂-Linear is fully equipped with the
-- 4-level higher-categorical structure (category + tensor + symmetry
-- + dagger). Future N-arc successors can package compatibility
-- coherence (e.g., ⊗ + † = "self-dual compact closed category")
-- via a dedicated slice.
--
-- Next: N9 GaloisAdjunction.UnitCounit.
------------------------------------------------------------------------
