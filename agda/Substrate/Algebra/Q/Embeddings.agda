------------------------------------------------------------------------
-- Substrate.Algebra.Q.Embeddings
--
-- Q7 of the constructive ℚ arc per [scratch/q_arc_plan.md].
--
-- Canonical embeddings ℕ → ℚ and ℤ → ℚ. Each maps n to n/1
-- (denominator = 1, stored as den-1 = 0).
--
-- These are RING-HOMOMORPHISMS (they preserve +, *, and 0/1);
-- the homomorphism witnesses are deferred to a follow-up arc
-- since they require ℚ canonical-form lemmas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Embeddings where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 0ℤ; 1ℤ)
open import Substrate.Algebra.Q using (ℚ; mkℚ; 0ℚ; 1ℚ; -1ℚ)

------------------------------------------------------------------------
-- 1. ℕ → ℚ.
--
-- n ↦ n/1.
------------------------------------------------------------------------

ℕ→ℚ : ℕ → ℚ
ℕ→ℚ n = mkℚ (+ n) 0

------------------------------------------------------------------------
-- 2. ℤ → ℚ.
--
-- z ↦ z/1.
------------------------------------------------------------------------

ℤ→ℚ : ℤ → ℚ
ℤ→ℚ z = mkℚ z 0

------------------------------------------------------------------------
-- 3. Smoke tests: the embeddings match the named constants.
------------------------------------------------------------------------

ℕ→ℚ-of-0 : ℕ→ℚ 0 ≡ 0ℚ
ℕ→ℚ-of-0 = refl

ℕ→ℚ-of-1 : ℕ→ℚ 1 ≡ 1ℚ
ℕ→ℚ-of-1 = refl

ℤ→ℚ-of-0ℤ : ℤ→ℚ 0ℤ ≡ 0ℚ
ℤ→ℚ-of-0ℤ = refl

ℤ→ℚ-of-1ℤ : ℤ→ℚ 1ℤ ≡ 1ℚ
ℤ→ℚ-of-1ℤ = refl

------------------------------------------------------------------------
-- 4. Inverse-when-possible: extract ℤ from a ℚ with denominator 1.
--
-- If den-1 = 0 (i.e., denominator = 1), the ℚ is the embedding
-- of its numerator-as-ℤ. Otherwise, no extraction is meaningful
-- without reduction (deferred).
------------------------------------------------------------------------

ℚ-as-ℤ-when-d=1 :
  (q : ℚ) → ℚ.den-1 q ≡ 0 → ℤ
ℚ-as-ℤ-when-d=1 q _ = ℚ.num q
  where open import Substrate.Algebra.Q using (module ℚ)

------------------------------------------------------------------------
-- 5. Capstone for Q7.
--
-- ℕ, ℤ embed into ℚ at the n/1 fiber. Q8 builds ℚ-Vector; Q9
-- builds ℚ-Linear.
------------------------------------------------------------------------
