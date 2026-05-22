------------------------------------------------------------------------
-- Substrate.Conway.IntegerEmbedding
--
-- S9 of the Surreal-numbers arc per [scratch/surreal_arc_plan.md].
--
-- Embed ℤ (positive and negative integers) into the SurrealFinite
-- hierarchy. Positive n maps to a "successor tower":
--
--   nat→surreal 0 = ⟨ [] ∣ [] ⟩       (= Zero)
--   nat→surreal 1 = ⟨ Zero ∷ [] ∣ [] ⟩      (= One)
--   nat→surreal 2 = ⟨ One ∷ [] ∣ [] ⟩       (= Two)
--   ...
--   nat→surreal n = ⟨ (nat→surreal (n-1)) ∷ [] ∣ [] ⟩
--
-- Negative integers use the negation from S8:
--
--   nat→surreal-neg n = -ⁿ (nat→surreal n)
--
-- Per [[feedback-categorical-name-first]]: this is the canonical
-- ℤ → No embedding ("No" = the universe of surreals).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.IntegerEmbedding where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Conway.SurrealFinite using (SurrealFinite; ⟨_∣_⟩)
open import Substrate.Conway.Examples using (Zero; One; NegOne)
open import Substrate.Conway.Neg using (-ⁿ_)

------------------------------------------------------------------------
-- 1. Non-negative integer embedding.
--
-- nat→surreal n : SurrealFinite (suc n) builds the canonical
-- surreal representing the integer n via the successor tower.
------------------------------------------------------------------------

nat→surreal : (n : ℕ) → SurrealFinite (suc n)
nat→surreal zero    = ⟨ [] ∣ [] ⟩
nat→surreal (suc n) = ⟨ nat→surreal n ∷ [] ∣ [] ⟩

------------------------------------------------------------------------
-- 2. Smoke tests: ℤ values agree with S3 examples.
------------------------------------------------------------------------

nat→surreal-0 : nat→surreal 0 ≡ Zero
nat→surreal-0 = refl

nat→surreal-1 : nat→surreal 1 ≡ One
nat→surreal-1 = refl

------------------------------------------------------------------------
-- 3. Negative-integer embedding.
--
-- For positive n, the negative integer -n maps to -ⁿ (nat→surreal n).
-- For n = 0, this is just Zero (since -0 = 0).
------------------------------------------------------------------------

nat→surreal-neg : (n : ℕ) → SurrealFinite (suc n)
nat→surreal-neg n = -ⁿ (nat→surreal n)

------------------------------------------------------------------------
-- 4. Smoke tests for negatives.
------------------------------------------------------------------------

nat→surreal-neg-0 : nat→surreal-neg 0 ≡ Zero
nat→surreal-neg-0 = refl

nat→surreal-neg-1 : nat→surreal-neg 1 ≡ NegOne
nat→surreal-neg-1 = refl

------------------------------------------------------------------------
-- 5. Successor and predecessor at the surreal level.
--
-- The successor of nat→surreal n is nat→surreal (suc n); the
-- predecessor (in the negative direction) is nat→surreal-neg (suc n).
-- Both are SurrealFinite at higher birthday than the input.
------------------------------------------------------------------------

surreal-successor :
  (n : ℕ) →
  SurrealFinite (suc (suc n))
surreal-successor n = nat→surreal (suc n)

------------------------------------------------------------------------
-- 6. Capstone for S9.
--
-- ℤ → No embedding lands; positive and negative integers have
-- canonical surreal representations. The embedding respects
-- 0 = Zero, 1 = One, -1 = NegOne (verified by refl).
--
-- S10 builds the categorical home via Cone.
------------------------------------------------------------------------
