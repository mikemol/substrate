------------------------------------------------------------------------
-- Substrate.Conway.Order
--
-- S4 of the Surreal-numbers arc per [scratch/surreal_arc_plan.md].
--
-- Conway's recursive order on surreals:
--
--   x ≤ y ⟺ (∀ x' ∈ x_L. ¬(y ≤ x')) ∧ (∀ y' ∈ y_R. ¬(y' ≤ x))
--
-- Encoded as a FUEL-BOUNDED Set-valued recursive function: each
-- ≤-comparison at fuel suc f recurses to ≤-comparisons at fuel f.
-- The substrate-canonical `--safe`-friendly encoding (avoiding
-- well-founded recursion machinery and sized types).
--
-- Per [[feedback-comments-dont-overclaim]]: fuel-bounded means
-- comparisons at large surreals need correspondingly large fuel.
-- The unfueled `_≤ⁿ_` form pre-applies birthday-sum-derived fuel.
-- A full well-founded encoding is deferred per
-- [[feedback-coalgebraic-not-consumer-driven]].
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.Order where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Conway.SurrealFinite using (SurrealFinite; ⟨_∣_⟩)

------------------------------------------------------------------------
-- 1. Fuel-bounded order.
--
-- General SurrealFinite indices accepted (the SurrealFinite 0
-- case never arises in practice since it's uninhabited; if a
-- Word (SurrealFinite 0) cons-pattern were somehow constructed,
-- the order would be definitionally trivial).
------------------------------------------------------------------------

mutual
  _≤ⁿ[_]_ :
    {m n : ℕ} →
    SurrealFinite m → ℕ → SurrealFinite n → Set
  x ≤ⁿ[ zero ] y = ⊤
  _≤ⁿ[_]_ ⟨ L₁ ∣ R₁ ⟩ (suc f) ⟨ L₂ ∣ R₂ ⟩ =
    no-above f ⟨ L₂ ∣ R₂ ⟩ L₁
    × no-below f ⟨ L₁ ∣ R₁ ⟩ R₂

  no-above :
    {m n : ℕ} →
    ℕ →
    SurrealFinite (suc n) →
    Word (SurrealFinite m) →
    Set
  no-above f y []       = ⊤
  no-above f y (x ∷ xs) =
    ((y ≤ⁿ[ f ] x) → ⊥)
    × no-above f y xs

  no-below :
    {m n : ℕ} →
    ℕ →
    SurrealFinite (suc n) →
    Word (SurrealFinite m) →
    Set
  no-below f x []        = ⊤
  no-below f x (y' ∷ ys) =
    ((y' ≤ⁿ[ f ] x) → ⊥)
    × no-below f x ys

------------------------------------------------------------------------
-- 2. Unfueled order: default fuel is birthday-sum + 2.
--
-- Sufficient for meaningful recursion at finite birthday. The
-- "+ 2" gives headroom for the constructor's outer step.
------------------------------------------------------------------------

_≤ⁿ_ :
  {m n : ℕ} →
  SurrealFinite (suc m) → SurrealFinite (suc n) → Set
_≤ⁿ_ {m} {n} x y = x ≤ⁿ[ suc (suc (m + n)) ] y

------------------------------------------------------------------------
-- 3. Capstone for S4.
--
-- The fuel-bounded order is defined. S5 will prove the order
-- laws (reflexivity, transitivity at finite birthdays).
------------------------------------------------------------------------
