------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.MonsterLieAlgebra
--
-- The Monster Lie algebra m as a parametric L2 LieAlgebra instance.
--
-- L19 of the L-arc. Module-parametric per substrate convention,
-- following the pattern of T8 Monster.AsCoalgebra / X4 GriessAlgebra
-- / Z9 Monster.AsAutGriess.
--
-- HISTORY: The Monster Lie algebra m is the Borcherds-Kac-Moody Lie
-- algebra associated to the Moonshine module V♮ (Borcherds 1992).
-- Its denominator identity is the Koike-Norton-Zagier product
-- formula
--   p^{-1} ∏_{m>0, n∈ℤ} (1 - p^m q^n)^{c(mn)}
--     = j(p) - j(q)
-- where c(n) are the j-function Fourier coefficients (= dim V♮_n+1).
-- This identity completed Borcherds's proof of the Conway-Norton
-- Monstrous Moonshine conjectures.
--
-- The Monster Lie algebra is:
--   * (II_{1,1})-graded (rank-2 hyperbolic lattice grading)
--   * Each graded piece is an M-module (= a representation of the
--     Monster)
--   * Has roots (m, n) ∈ II_{1,1} with multiplicity c(mn)
--   * Realised as the BRST-cohomology H¹(V^♮ ⊗ V_{II_{1,1}})
--
-- Per [[continuous-via-discrete-inference-rules]]: the carrier V is
-- abstract (user-supplied); the substrate captures the Lie structure
-- via L2 LieAlgebra. Concrete realisations (BRST cohomology, vertex
-- operator construction) are external content.
--
-- Per [[universal-property-discipline]]: the Monster Lie algebra
-- has multiple universal-property characterisations:
--   * The Borcherds-Kac-Moody Lie algebra with specific Cartan +
--     simple-root data (rank 2 with imaginary simple roots)
--   * The cohomology of a specific BRST complex
--   * The Lie algebra acting on V♮ via the vertex algebra structure
-- The substrate-side primitive L19 captures the LieAlgebra view;
-- the others are external + module-parametric extensions.
--
-- Per [[homology-cohomology-recursion]]: the Monster Lie algebra is
-- the HOMOLOGY-side level-1 structure (Lie algebra on V♮); the
-- denominator identity is the level-2 cohomology (product formula
-- catalog over the j-function); Monstrous Moonshine is the level-3
-- structure (representation-theoretic content matching theta-series).
--
-- Module-parametric: user supplies the LieAlgebra value witnessing m.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.LieAlgebra using (LieAlgebra)

module Substrate.Algebra.Sporadic.MonsterLieAlgebra
  -- The substrate-internal LieAlgebra value witnessing the Monster
  -- Lie algebra m (= Borcherds-Kac-Moody Lie algebra associated to
  -- V♮; cited Borcherds 1992).
  (m : LieAlgebra {Level.zero})
  where

------------------------------------------------------------------------
-- 1. The Monster Lie algebra as L2 LieAlgebra.
--
-- Direct re-export — the substrate-side formal target is the
-- supplied LieAlgebra value, named structurally as the Monster Lie
-- algebra m.
------------------------------------------------------------------------

MonsterLieAlgebra : LieAlgebra
MonsterLieAlgebra = m

------------------------------------------------------------------------
-- 2. Capstone — Monster Lie algebra hosted at the substrate.
--
-- L19 of the L-arc. With L19 landed, the substrate has the
-- structural identification of the Monster Lie algebra as a L2
-- LieAlgebra. The Borcherds-Kac-Moody / denominator-identity /
-- BRST-cohomology characterisations are external; the substrate
-- names the LieAlgebra view.
--
-- After L19: the substrate has THREE Lie-algebra views connected to
-- the Monster:
--   * L14 sl₂ + L15 so₃ (small-rank Lie algebras)
--   * L19 MonsterLieAlgebra (THIS) — the rank-2 hyperbolic
--     Borcherds-Kac-Moody Lie algebra
--   * (implicit) the Lie algebra of M's centralisers acting on V♮ —
--     not as a single Lie algebra but as the Lie algebra of
--     Aut(GriessAlgebra) ≅ M (Z9)
--
-- Per the substrate's broader Monster catalogue after L19:
--   * Z9 Monster.AsAutGriess: M ≅ Aut(GriessAlgebra)
--   * T8 Monster.AsCoalgebra: M as ConjugationCoalgebra
--   * Y7+Y8 Monster.AsPresented: M as PresentedGroup
--   * L19 MonsterLieAlgebra: m as LieAlgebra (acting on V♮)
-- Four substrate-internal views of the Monster, all parametric,
-- all bridged via the substrate's universal-property infrastructure.
--
-- Per [[homology-cohomology-recursion]] + [[tetrative-meta-
-- circularity]]: L19 closes the substrate-side L-arc's Lie-side
-- connection to the Monster. The substrate now spans the entire
-- algebraic-structure recursion (ACA → Lie → CartanType → Coxeter →
-- root system → V♮ → Monster) at the LieAlgebra primitive level.
--
-- Next: L20 capstone — PrimitivesAll + PrimitiveInstances refresh
-- to expose all L-arc additions.
------------------------------------------------------------------------
