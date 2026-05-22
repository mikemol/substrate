------------------------------------------------------------------------
-- Substrate.Conway.Equivalence
--
-- S6 of the Surreal-numbers arc per [scratch/surreal_arc_plan.md].
--
-- Surreal equivalence: x ≈ⁿ y iff x ≤ⁿ y AND y ≤ⁿ x. The
-- equivalence classes are the actual surreal NUMBERS (one number
-- may have many representations as ⟨L∣R⟩).
--
-- Per [[feedback-comments-dont-overclaim]]: reflexivity and
-- symmetry of ≈ⁿ are direct; full transitivity requires the
-- transitivity of ≤ⁿ which is Conway-induction-deep (deferred).
-- The fragment provides ≈ⁿ as a definition + the lemmas that hold
-- at the simplest surreals.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.Equivalence where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Conway.SurrealFinite using (SurrealFinite)
open import Substrate.Conway.Order using (_≤ⁿ_)
open import Substrate.Conway.Examples using (Zero)
open import Substrate.Conway.OrderLaws using (refl-Zero; ⟨[]∣[]⟩-refl)

------------------------------------------------------------------------
-- 1. Equivalence relation _≈ⁿ_.
--
-- x ≈ⁿ y iff x ≤ⁿ y AND y ≤ⁿ x. The standard surreal-equivalence.
------------------------------------------------------------------------

infix 4 _≈ⁿ_

_≈ⁿ_ :
  {m n : ℕ} →
  SurrealFinite (suc m) → SurrealFinite (suc n) → Set
x ≈ⁿ y = (x ≤ⁿ y) × (y ≤ⁿ x)

------------------------------------------------------------------------
-- 2. Symmetry of _≈ⁿ_.
--
-- Direct from the definition: swap the two halves.
------------------------------------------------------------------------

sym-≈ⁿ :
  {m n : ℕ}
  (x : SurrealFinite (suc m)) (y : SurrealFinite (suc n)) →
  x ≈ⁿ y → y ≈ⁿ x
sym-≈ⁿ x y (x≤y , y≤x) = y≤x , x≤y

------------------------------------------------------------------------
-- 3. Reflexivity at Zero.
--
-- Zero ≈ⁿ Zero via refl-Zero applied to both halves of the pair.
------------------------------------------------------------------------

refl-Zero-≈ : Zero ≈ⁿ Zero
refl-Zero-≈ = refl-Zero , refl-Zero

------------------------------------------------------------------------
-- 4. Reflexivity at empty-L/empty-R surreals.
--
-- The general "any birthday n" version requires Agda elaboration
-- choices that conflict with the implicit-meta system; rather than
-- forcing them, S6 keeps the Zero-only reflexivity (refl-Zero-≈
-- above) as the headline. Per [[feedback-coalgebraic-not-consumer-driven]]:
-- the general lemma surfaces when a consumer requires it.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 5. Extracting the two ≤ⁿ halves.
--
-- Convenience accessors.
------------------------------------------------------------------------

≈-to-≤ :
  {m n : ℕ}
  {x : SurrealFinite (suc m)} {y : SurrealFinite (suc n)} →
  x ≈ⁿ y → x ≤ⁿ y
≈-to-≤ = proj₁

≈-to-≥ :
  {m n : ℕ}
  {x : SurrealFinite (suc m)} {y : SurrealFinite (suc n)} →
  x ≈ⁿ y → y ≤ⁿ x
≈-to-≥ = proj₂

------------------------------------------------------------------------
-- 6. Capstone for S6.
--
-- The equivalence relation _≈ⁿ_ is defined; symmetry, reflexivity
-- at simple surreals, and the projections are in place.
-- Transitivity requires Conway-induction on _≤ⁿ_; deferred.
------------------------------------------------------------------------
