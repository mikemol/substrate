------------------------------------------------------------------------
-- Substrate.Algebra.Q.Capstone
--
-- Q10 of the constructive ℚ arc per [scratch/q_arc_plan.md].
--
-- Capstone: re-export of Q1-Q9 + smoke tests + the bridge note
-- to a future FreeLinearization-over-ℚ generalisation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Capstone where

-- Re-export the Q-arc slices publicly.
open import Substrate.Algebra.Z
open import Substrate.Algebra.Q
open import Substrate.Algebra.Q.DecidableEq
open import Substrate.Algebra.Q.Reduction
open import Substrate.Algebra.Q.Arithmetic
open import Substrate.Algebra.Q.Order
open import Substrate.Algebra.Q.Embeddings
open import Substrate.Algebra.Q.Vector
open import Substrate.Algebra.Q.Linear
------------------------------------------------------------------------
-- 1. Smoke test: 1 + 1 in ℚ.
--
-- Result: 1ℚ +ℚ 1ℚ should be (definitionally) some form of 2/1.
-- Storage: (1*1 + 1*1, 1*1 - 1) = (2, 0). Verified by inspection.
------------------------------------------------------------------------

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Q using (ℚ; mkℚ)

1+1-storage : (1ℚ +ℚ 1ℚ) ≡ mkℚ (+ 2) 0
1+1-storage = refl

------------------------------------------------------------------------
-- 2. Smoke test: -1 + 1 = 0 in ℚ.
------------------------------------------------------------------------

-1+1-storage : (-1ℚ +ℚ 1ℚ) ≡ mkℚ (+ 0) 0
-1+1-storage = refl

------------------------------------------------------------------------
-- 3. Smoke test: 2 * 3 in ℚ.
--
-- (2/1) * (3/1) = (6/1) = mkℚ (+ 6) 0.
------------------------------------------------------------------------

2*3-storage :
  (mkℚ (+ 2) 0 *ℚ mkℚ (+ 3) 0) ≡ mkℚ (+ 6) 0
2*3-storage = refl

------------------------------------------------------------------------
-- 4. Capstone for the Q-arc.
--
-- The substrate now has:
--   * Substrate-native ℤ (Q1) with negation + decidable equality
--   * ℚ as ℤ-ℕ⁺ pair (Q2) + smart constructors
--   * Syntactic decidable equality (Q3)
--   * Reduction predicate + gcd-of-ℚ (Q4)
--   * Arithmetic: +, *, − (Q5)
--   * Cross-product ordering (Q6)
--   * ℕ → ℚ and ℤ → ℚ embeddings (Q7)
--   * ℚ-Vector + ℚ-Linear sister structures (Q8, Q9)
--
-- Future arcs:
--   * Full reduce function (needs ℤ-by-ℕ division with NonZero)
--   * ℚ ring laws (commutativity, associativity, distributivity)
--   * FreeLinearization over ℚ (generalising
--     Substrate.Category.FreeLinearization from F₂ to ℚ)
--   * Toki Pona retrofit with ℚ-vectors (more semantic richness)
--   * Conway-surreal arithmetic with ℚ-valued embeddings
--
-- E-arc (slices 11-20) starts the pedagogical-export layer
-- independently; no dependency on Q-arc.
------------------------------------------------------------------------
