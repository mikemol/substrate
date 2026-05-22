------------------------------------------------------------------------
-- Substrate.Conway.Add
--
-- S7 of the Surreal-numbers arc per [scratch/surreal_arc_plan.md].
--
-- Conway's surreal addition:
--
--   x + y = ⟨ x_L + y, x + y_L ∣ x_R + y, x + y_R ⟩
--
-- where x_L + y is shorthand for "the Word of x' + y for each
-- x' ∈ x_L" (similar for the other components).
--
-- The full general recursive definition requires careful index
-- arithmetic at the SurrealFinite 0 case (uninhabited; pattern-
-- matching there needs absurd patterns) AND Agda's termination
-- checker to see strict descent in the combined birthday measure.
-- Both are tractable but exceed the 1-slice scope.
--
-- Per [[feedback-comments-dont-overclaim]]: S7 lands the API
-- TYPE for addition + the simplest worked instance (Zero + Zero
-- = Zero); the general recursive definition is deferred per
-- [[feedback-coalgebraic-not-consumer-driven]] until a consumer
-- requires it. The substrate-internal Cone interpretation (S10)
-- gives a CATEGORICAL home for addition as a binary operation on
-- the Cone-apex side.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.Add where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Conway.SurrealFinite using (SurrealFinite; ⟨_∣_⟩)
open import Substrate.Conway.Examples using (Zero)

------------------------------------------------------------------------
-- 1. Addition for empty-L/empty-R surreals.
--
-- The simplest case: adding two ⟨ [] ∣ [] ⟩ surreals at any
-- birthday gives ⟨ [] ∣ [] ⟩ at the combined birthday. This is
-- the Zero + Zero case and similar.
------------------------------------------------------------------------

add-empties :
  (m n : ℕ) → SurrealFinite (suc (m + n))
add-empties m n = ⟨ [] ∣ [] ⟩

------------------------------------------------------------------------
-- 2. Zero + Zero = Zero (computationally).
--
-- Zero is the SurrealFinite 1 surreal ⟨ [] ∣ [] ⟩. Adding it to
-- itself: the result type SurrealFinite (suc (0 + 0)) = SurrealFinite 1.
-- The "result" matches Zero structurally.
------------------------------------------------------------------------

Zero+Zero : SurrealFinite 1
Zero+Zero = add-empties 0 0

Zero+Zero-≡-Zero : Zero+Zero ≡ Zero
Zero+Zero-≡-Zero = refl

------------------------------------------------------------------------
-- 3. Addition signature (deferred general implementation).
--
-- The full
--
--   _+ⁿ_ : SurrealFinite (suc m) → SurrealFinite (suc n) →
--          SurrealFinite (suc (m + n))
--
-- requires the recursive Conway definition with simultaneous
-- induction on both arguments and absurd-pattern handling at the
-- SurrealFinite 0 base case. Both are tractable but exceed the
-- 1-slice scope. The signature is recorded as a comment for
-- consumer reference; `postulate` would violate `--safe`.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 4. Capstone for S7.
--
-- Addition's TYPE is named; the Zero+Zero specific case is
-- discharged. General implementation deferred. S8 supplies
-- negation (which is easier — just swap L and R); S9 builds
-- integer embeddings; S10 the Cone bridge.
------------------------------------------------------------------------
