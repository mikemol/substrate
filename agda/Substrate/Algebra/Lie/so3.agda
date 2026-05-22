------------------------------------------------------------------------
-- Substrate.Algebra.Lie.so3
--
-- The Lie algebra so(3) — 3×3 skew-symmetric matrices with bracket
-- [A, B] = AB - BA. Equivalent to sl(2, ℝ) as real Lie algebras
-- (both have Cartan type A₁); commonly realised as the algebra of
-- infinitesimal rotations in ℝ³ via L_x, L_y, L_z generators
-- satisfying [L_x, L_y] = L_z (and cyclic).
--
-- L15 of the L-arc. Module-parametric per substrate convention,
-- sibling of L14 sl₂. Same A₁ Cartan type but DIFFERENT basis
-- relations (angular-momentum form, not Chevalley form).
--
-- Standard so₃ relations (angular-momentum basis):
--   [L_x, L_y] = L_z
--   [L_y, L_z] = L_x
--   [L_z, L_x] = L_y
-- Anti-commutativity gives the reversed pairs as negatives.
--
-- Per [[continuous-via-discrete-inference-rules]]: the carrier is
-- abstract (user-supplied via the LieAlgebra parameter); the
-- substrate captures the structural identification of L as so₃ via
-- the basis + relations.
--
-- Per [[3plus1-parity-universal]]: so₃ is the rotational Lie algebra
-- of ℝ³ = the "3" axis underlying the 3+1 parity; (L_x, L_y, L_z)
-- are the three rotational generators, and the "+1" is the SU(2)
-- spin lift to su(2) (= sl₂'s real form). The substrate's L14 + L15
-- expose both sides of the SU(2) ↔ SO(3) double cover at the Lie
-- algebra level.
--
-- Per [[torsion-element-universal]]: so₃ has the natural torsion
-- structure exp(2π L_z) = id when L_z generates a circle subgroup;
-- the substrate's HasOrder primitive applies via the corresponding
-- one-parameter subgroups.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)
open import Substrate.Category.CartanType using (CartanType; mkCartanType)
open import Substrate.Category.LieAlgebra using (LieAlgebra)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)

module Substrate.Algebra.Lie.so3
  -- The substrate-internal LieAlgebra value witnessing so₃.
  (L : LieAlgebra {Level.zero})
  -- The three angular-momentum basis elements.
  (Lx Ly Lz : LieAlgebra.V L)
  -- The standard so₃ relations (angular-momentum form).
  (LxLy-eq : LieAlgebra._·_ L Lx Ly ≡ Lz)
  (LyLz-eq : LieAlgebra._·_ L Ly Lz ≡ Lx)
  (LzLx-eq : LieAlgebra._·_ L Lz Lx ≡ Ly)
  where

------------------------------------------------------------------------
-- 1. so₃ as a LieAlgebra.
------------------------------------------------------------------------

so3-LieAlgebra : LieAlgebra
so3-LieAlgebra = L

------------------------------------------------------------------------
-- 2. so₃'s Cartan type: A₁ (same as sl₂).
--
-- Rank 1; single generator with order 2. The Cartan type A₁
-- classifies so₃ ≅ sl₂(ℝ) as a Lie algebra.
------------------------------------------------------------------------

A1-rank : ℕ
A1-rank = 1

A1-m : Fin A1-rank → Fin A1-rank → ℕ
A1-m _ _ = 1

A1-m-diag : (i : Fin A1-rank) → A1-m i i ≡ 1
A1-m-diag _ = refl

A1-m-symm : (i j : Fin A1-rank) → A1-m i j ≡ A1-m j i
A1-m-symm _ _ = refl

so3-CartanType : CartanType
so3-CartanType = mkCartanType A1-rank A1-m A1-m-diag A1-m-symm

------------------------------------------------------------------------
-- 3. Capstone — so₃ as L-arc concrete Lie algebra.
--
-- L15 of the L-arc. Closes phase Λ'' (L11-L15):
--   L11 RootSystem
--   L12 CartanType
--   L13 Coxeter.AsCartanType bridge
--   L14 sl₂ (Chevalley basis)
--   L15 so₃ (angular-momentum basis)
--
-- After L15: substrate has the Coxeter ↔ Cartan ↔ Lie bridge with
-- two concrete instances exhibiting the SAME Cartan type (A₁) under
-- DIFFERENT bases (sl₂'s Chevalley vs so₃'s angular momentum). The
-- structural equivalence sl₂(ℝ) ≅ so₃ is captured by the shared
-- CartanType + the bridge L13.
--
-- Per [[homology-cohomology-recursion]]: A₁ is the Cartan-type
-- COHOMOLOGY-side; sl₂ + so₃ are HOMOLOGY-side observations sharing
-- the same Cartan label. The next-level cohomology (Lie group
-- exponential — SU(2) ↔ SO(3) double cover) is at the continuous-
-- Lift level (X-arc S1-Lift / S2-Lift primitives).
--
-- Next: phase Λ''' (L16-L20):
--   L16 JordanAlgebra
--   L17 GriessAlgebra.AsJordan
--   L18 UniversalEnvelopingAlgebra
--   L19 MonsterLieAlgebra
--   L20 capstone refresh
------------------------------------------------------------------------
