------------------------------------------------------------------------
-- Substrate.Category.Coxeter.AsCartanType
--
-- The bridge from Coxeter-system data to L12 [[CartanType]].
--
-- L13 of the L-arc. Closes the structural identification:
--   A Coxeter system (rank + relation orders) IS a Cartan-type matrix.
--
-- This is a STRUCTURAL bridge per substrate convention (compare
-- Z9 Monster.AsAutGriess, T8 Monster.AsCoalgebra): take the Coxeter
-- data as module parameters; package it as the L12 CartanType. The
-- substrate-side formal identification is the constructed CartanType
-- value.
--
-- Per [[universal-property-discipline]]: the Coxeter Word algebra +
-- (m_ij) matrix carry the same structural information. The Word
-- algebra is the GENERATIVE side (= compute relations, enumerate
-- group elements); the (m_ij) matrix is the DESCRIPTIVE side
-- (= Cartan-type / Dynkin-diagram classification).
--
-- Per [[homology-cohomology-recursion]]: Word-algebra-side ↔
-- matrix-side IS the homology/cohomology recursion at the L-arc's
-- Coxeter ↔ Lie pivot. L13 names the bridge structurally.
--
-- The bridge takes the substrate's existing Coxeter framework's
-- "rank + m_ij data" and lifts it to L12 CartanType. Concrete
-- consumers (L14 sl₂, L15 so₃) supply the m matrix per Cartan type
-- (A₁ for sl₂: rank=1, m_11=1).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.CartanType using (CartanType; mkCartanType)

module Substrate.Category.Coxeter.AsCartanType
  -- The Coxeter system data: rank + relation-orders matrix.
  (rank   : ℕ)
  (m      : Fin rank → Fin rank → ℕ)
  (m-diag : (i : Fin rank) → m i i ≡ 1)
  (m-symm : (i j : Fin rank) → m i j ≡ m j i)
  where

------------------------------------------------------------------------
-- 1. The CartanType-of-Coxeter bridge.
--
-- Direct lift: the Coxeter system data IS the Cartan type. The
-- substrate-side formal target is the constructed CartanType value.
------------------------------------------------------------------------

Coxeter-AsCartanType : CartanType
Coxeter-AsCartanType = mkCartanType rank m m-diag m-symm

------------------------------------------------------------------------
-- 2. Capstone — Coxeter ↔ Cartan bridge closed.
--
-- L13 of the L-arc. With L13 landed, the substrate has the
-- structural identification:
--   Coxeter system (rank + relations) ≅ Cartan type
-- The substrate's Coxeter Word framework (Substrate.Groups.Coxeter.*)
-- can now be re-cast via this bridge to expose Cartan-type data.
--
-- Closes phase Λ'' (L11-L13) of the L-arc:
--   L11 RootSystem (combinatorial root data)
--   L12 CartanType (Coxeter matrix labels)
--   L13 Coxeter.AsCartanType (bridge from Word algebra to matrix)
--
-- The 3-slice mini-arc is structurally analogous to T4
-- GaloisAdjunction (PFG ↔ ConjugationCoalgebra bridge): both
-- bridges name a structural equivalence already implicit at the
-- generative/descriptive split.
--
-- Concrete usage:
--   * sl₂ (L14): rank=1, m = (λ _ _ → 1), so Cartan type A₁
--   * so₃ (L15): same A₁ (rank 1, same matrix)
--   * Higher: A_n family with n×n matrix m_ij = 3 if |i-j|=1, 2 if
--     |i-j|≥2; D_n, E_6/7/8 etc. by their Dynkin diagrams
--
-- Per the user's "find the pullback" observation: L13 IS the
-- structural pullback identifying Coxeter algebraic data + Cartan
-- matrix data + Lie root-system data at the substrate's bridge layer.
--
-- Next: L14 sl₂ (concrete Lie algebra at A₁ Cartan type).
------------------------------------------------------------------------
