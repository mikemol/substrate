------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.AsSymmetricMonoidal
--
-- Substrate-level naming of F₂-Linear as a symmetric monoidal
-- category.
--
-- N7 of the N-arc.
--
-- F₂-Linear (= category of F₂-vector spaces + F₂-linear maps) carries
-- canonical symmetric monoidal structure:
--   * tensor product = tensor product of F₂-vector spaces
--   * unit object = F₂ itself
--   * symmetry = canonical swap V ⊗ W → W ⊗ V satisfying σ² = id
--
-- Per [[grothendieck-coherence-rule]]: closes the M-arc OrphanAudit
-- row "F₂-Linear should be SymmetricMonoidal." After N7, the
-- substrate's canonical algebraic category carries the tensor /
-- symmetry structure required by future tensor-bearing primitives
-- (Λ at degree-1+, ChainComplex, GradedAlgebra).
--
-- Module-parametric per substrate convention: the F₂-Linear
-- CategoryOf instance + tensor / unit / symmetry data are user-
-- supplied; the substrate names the identification.
--
-- This is the N-arc's first M3 SymmetricMonoidal instance — closing
-- the orphan loop for tensor structure at the substrate's
-- foundational vector-space layer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.SymmetricMonoidal
  using (SymmetricMonoidal)

module Substrate.Algebra.F2.Linear.AsSymmetricMonoidal
  {ℓO ℓM : Level}
  -- The substrate-internal SymmetricMonoidal value witnessing F₂-
  -- Linear with ⊗ + I + σ structure (user-supplied; concrete
  -- consumer constructs via the F₂.Linear.* infrastructure).
  (F2Linear-SM : SymmetricMonoidal {ℓO} {ℓM})
  where

------------------------------------------------------------------------
-- 1. F₂-Linear as the substrate's named SymmetricMonoidal instance.
------------------------------------------------------------------------

F2Linear-AsSymmetricMonoidal : SymmetricMonoidal
F2Linear-AsSymmetricMonoidal = F2Linear-SM

------------------------------------------------------------------------
-- 2. Capstone — F₂-Linear as M3 SymmetricMonoidal.
--
-- N7 of the N-arc. With N7 landed, F₂-Linear is structurally a
-- symmetric monoidal category at the substrate primitive layer.
-- Downstream primitives (Λ, U, future tensor-bearing constructions)
-- can compose with this monoidal structure functorially.
--
-- Per [[universal-property-discipline]]: full coherence (pentagon,
-- triangle, hexagon) is downstream specialisation per M3's
-- substrate-pragmatic minimum; the user's F2Linear-SM supplies
-- whichever coherence level the consumer needs.
--
-- Next: N8 F2.Linear.AsDaggerCategory.
------------------------------------------------------------------------
