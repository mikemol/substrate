------------------------------------------------------------------------
-- Substrate.Algebra.Lie.so3
--
-- The Lie algebra so(3) — 3×3 skew-symmetric matrices with bracket
-- [A, B] = AB - BA. Shares the A₁ Cartan type with sl₂ (their
-- complexifications agree); as a REAL Lie algebra it is the COMPACT
-- form (≅ su(2)), a DIFFERENT real form from the split sl(2, ℝ) — NOT
-- isomorphic over ℝ. Commonly realised as the algebra of
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

open import Substrate.Foundation.Level using (Level; 0ℓ)
open import Substrate.Category.CartanType using (CartanType)
open import Substrate.Category.LieAlgebra using (LieAlgebra)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Lie.CartanA1 using (A1-CartanType)

module Substrate.Algebra.Lie.so3
  -- The substrate-internal LieAlgebra value witnessing so₃.
  (L : LieAlgebra {0ℓ})
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
-- 2. so₃'s Cartan type: the SHARED A₁ (Substrate.Algebra.Lie.CartanA1).
--
-- so3-CartanType IS the one `A1-CartanType` that sl2-CartanType also is — the
-- "shared CartanType" now a literal shared definition, not asserted prose.
-- This says their COMPLEXIFICATIONS agree (both = sl₂(ℂ) = A₁). It does NOT
-- say so₃ ≅ sl₂(ℝ) as real Lie algebras: they are distinct real forms (so₃ ≅
-- su(2), the compact form; sl₂(ℝ), the split form), NOT isomorphic over ℝ. A
-- shared Cartan type is the complex classification, not a real iso.
------------------------------------------------------------------------

so3-CartanType : CartanType
so3-CartanType = A1-CartanType

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
-- shared COMPLEX classification is captured by the literal shared
-- CartanType (A1-CartanType) + the bridge L13 — NOT a real iso (sl₂ and
-- so₃ are distinct real forms: split vs compact).
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
