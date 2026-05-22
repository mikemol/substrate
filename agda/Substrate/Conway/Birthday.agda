------------------------------------------------------------------------
-- Substrate.Conway.Birthday
--
-- S2 of the Surreal-numbers arc per [scratch/surreal_arc_plan.md].
--
-- Birthday extraction for SurrealFinite. Each `SurrealFinite (suc
-- n)` has Conway-birthday n (the 1-shift between my indexing and
-- Conway's). The birthday function recovers this, and the strict-
-- descent into sub-surreals (always at lower birthday) is the
-- termination measure that S4 (Order) and S7 (Add) consume.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.Birthday where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Conway.SurrealFinite using (SurrealFinite; ⟨_∣_⟩)

------------------------------------------------------------------------
-- 1. Birthday extraction.
--
-- For a SurrealFinite (suc n), the Conway-birthday is n (the
-- 1-shift). SurrealFinite 0 is uninhabited (no constructor), so
-- the function only needs the (suc n) case.
------------------------------------------------------------------------

birthday : {n : ℕ} → SurrealFinite n → ℕ
birthday {suc n} _ = n

------------------------------------------------------------------------
-- 2. Birthday equals the index minus one.
--
-- A SurrealFinite (suc n) always has birthday n. Refl by
-- definition of birthday.
------------------------------------------------------------------------

birthday-≡ :
  {n : ℕ} (s : SurrealFinite (suc n)) → birthday s ≡ n
birthday-≡ _ = refl

------------------------------------------------------------------------
-- 3. Birthday-zero characterisation.
--
-- The simplest surreal Zero (S3) has birthday 0. Any SurrealFinite
-- 1 inhabitant has birthday 0.
------------------------------------------------------------------------

birthday-of-day-0 :
  (s : SurrealFinite 1) → birthday s ≡ 0
birthday-of-day-0 _ = refl

------------------------------------------------------------------------
-- 4. Strict descent (the termination measure).
--
-- Built into the type: a SurrealFinite (suc n) has L and R
-- bound-sub-surreals at SurrealFinite n, with index strictly
-- less. This is the well-founded measure on which S4's recursive
-- order and S7's recursive addition descend.
--
-- Per [[feedback-categorical-name-first]]: this is the standard
-- recursion-on-birthday termination ("Conway induction").
------------------------------------------------------------------------

-- The strict-descent is structural; no explicit lemma needed.
-- Birthday n+1 implies sub-surreals at birthday n, which is < n+1
-- as ℕ.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 5. Capstone for S2.
--
-- birthday is defined; the strict descent into sub-surreals is
-- typed-in. S3 instantiates Zero / One / NegOne with their
-- corresponding birthdays; S4 uses the measure for recursive
-- order.
------------------------------------------------------------------------
