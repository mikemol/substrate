------------------------------------------------------------------------
-- Substrate.Conway.OrderAntisym
--
-- G6 of the Conway game-induction tower per
-- [scratch/m_mod_arc_plan.md].
--
-- Names the antisymmetry obligation for Conway's surreal order
-- modulo equivalence: x ≤ⁿ y ∧ y ≤ⁿ x ⟹ x ≈ y.
--
-- Conway surreals are NOT antisymmetric under propositional
-- equality (distinct constructions can be order-equivalent). The
-- substrate's `Substrate.Conway.Equivalence` defines `≈` as the
-- order-induced equivalence; this slice names the antisymmetry
-- obligation up to that ≈.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.OrderAntisym where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Conway.SurrealFinite using (SurrealFinite)
open import Substrate.Conway.Order using (_≤ⁿ_)
open import Substrate.Conway.Equivalence using (_≈ⁿ_)

------------------------------------------------------------------------
-- 1. The antisymmetry obligation (up to ≈).
------------------------------------------------------------------------

ConwayOrderAntisymmetry : Set
ConwayOrderAntisymmetry =
  {m n : ℕ}
  (x : SurrealFinite (suc m))
  (y : SurrealFinite (suc n)) →
  x ≤ⁿ y → y ≤ⁿ x → x ≈ⁿ y

------------------------------------------------------------------------
-- 2. Capstone for G6.
--
-- Antisymmetry obligation named via _≈ⁿ_. Combined with G5's
-- transitivity and the existing reflexivity (Substrate.Conway.
-- OrderLaws), the Conway order forms a preorder up to ≈ⁿ.
------------------------------------------------------------------------
