------------------------------------------------------------------------
-- Substrate.Category.CartanType
--
-- The categorical primitive for Cartan types (= Coxeter matrices).
--
-- A Cartan type packages a finite root system by its DYNKIN DIAGRAM:
-- rank n + an n × n symmetric matrix of Coxeter exponents
--   m_ij ∈ ℕ ∪ {∞}  with m_ii = 1, m_ij ≥ 2 for i ≠ j.
-- For crystallographic types (the Lie-theoretic cases A/B/C/D/E/F/G),
-- m_ij ∈ {2, 3, 4, 6}. The substrate-level primitive captures the
-- general Coxeter matrix; the crystallographic constraint is a
-- separate predicate.
--
-- L12 of the L-arc. Foundation for L13 [[Coxeter.AsCartanType]]
-- (bridging Coxeter Word algebra to Cartan-type matrix data).
--
-- Per [[categorical-name-first]]: "Cartan matrix" / "Coxeter matrix"
-- / "Dynkin diagram" are standard names. The universal property is
-- "the data classifying semisimple Lie algebras up to isomorphism"
-- (Cartan-Killing 1894); equivalently "the data classifying finite-
-- type Coxeter groups" (Coxeter 1934).
--
-- Per [[expose-generator-not-orbit]]: rank + (m_ij) is the
-- GENERATOR; the full Coxeter group / Lie algebra is the orbit.
-- E_8 has rank 8 but 696,729,600 group elements; rank-data IS
-- the universal generator.
--
-- Per [[homology-cohomology-recursion]]: root-system data (L11) is
-- the OBSERVED side; Cartan-type matrix is the CATALOGED side. The
-- ADE / BCFG / I / H classification is the level-2 cohomology over
-- the L12 catalog.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CartanType where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_)

------------------------------------------------------------------------
-- The CartanType record (general Coxeter-matrix flavour).
--
-- Bundles:
--   * rank : ℕ — number of simple generators
--   * m : Fin rank → Fin rank → ℕ — the Coxeter exponent matrix.
--     m i i = 1 (relation s_i² = e); m i j ≥ 2 for i ≠ j (relation
--     (s_i s_j)^{m_ij} = e). The substrate uses ℕ here; ∞ (free
--     case) is represented as 0 by convention (no relation of finite
--     order; the substrate's L12 doesn't enforce finiteness, leaving
--     that to specific instances).
--   * m-diag : (i : Fin rank) → m i i ≡ 1
--   * m-symm : (i j : Fin rank) → m i j ≡ m j i
------------------------------------------------------------------------

record CartanType : Set where
  constructor mkCartanType
  field
    rank   : ℕ
    m      : Fin rank → Fin rank → ℕ
    m-diag : (i : Fin rank) → m i i ≡ 1
    m-symm : (i j : Fin rank) → m i j ≡ m j i

------------------------------------------------------------------------
-- Capstone — Cartan-type primitive in place.
--
-- L12 of the L-arc. Foundation for:
--   * L13 Coxeter.AsCartanType (bridge from Coxeter Word algebra
--     to Cartan-type data via the (s_i s_j)^{m_ij} relation
--     extraction)
--   * Concrete Cartan-type instances:
--     - A_n family (m_ij = 3 for adjacent, 2 otherwise)
--     - B_n / C_n / D_n / E_6,7,8 / F_4 / G_2 (crystallographic)
--     - H_3 / H_4 / I_2(p) (non-crystallographic)
--
-- The crystallographic predicate (m_ij ∈ {2,3,4,6}) layers on top
-- via a Cartan-Crystallographic record extending L12.
--
-- After L12: substrate has both the geometric/combinatorial side
-- (L11 RootSystem) and the matrix/labeling side (L12 CartanType).
-- L13 bridges to the Coxeter Word algebra.
--
-- Next: L13 Coxeter.AsCartanType.
------------------------------------------------------------------------
