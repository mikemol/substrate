------------------------------------------------------------------------
-- Substrate.Conway.SurrealFinite
--
-- S1 of the Surreal-numbers arc per [scratch/surreal_arc_plan.md].
--
-- The birthday-indexed recursive carrier for Conway surreals,
-- substrate-compatible (--safe --without-K). A `SurrealFinite (suc
-- n)` is built from L and R Coxeter-Word collections of lower-
-- birthday sub-surreals; the strict-decrease in index gives Agda's
-- termination check the measure it needs.
--
-- Per [[project-surreals-term-algebra-alignment]]: the carrier
-- shape lines up with the substrate's existing term-algebra
-- primitives (Coxeter Word as the L/R bound carrier). This is
-- not Conway's set-theoretic definition but the constructive
-- finite-birthday slice that's substrate-native.
--
-- Per [[feedback-prefer-coxeter-backed]]: L and R bounds are
-- Coxeter Words, not stdlib Lists. The cons-list structure is
-- the substrate-canonical choice.
--
-- INDEXING CONVENTION: SurrealFinite 0 is uninhabited (no
-- constructor); the simplest surreal Zero lives at SurrealFinite
-- 1 with empty L and R. Conway's "birthday 0" maps to my
-- SurrealFinite 1 (a 1-shift), and birthday : SurrealFinite (suc
-- n) → ℕ recovers Conway's birthday as n. (S2 lands this.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.SurrealFinite where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

------------------------------------------------------------------------
-- 1. The recursive carrier.
--
-- A SurrealFinite (suc n) consists of a constructor ⟨_∣_⟩ taking
-- two Coxeter Words of sub-surreals at strictly lower birthday n.
-- Positive recursion via Word's container shape; Agda's positivity
-- check accepts this.
------------------------------------------------------------------------

data SurrealFinite : ℕ → Set where
  ⟨_∣_⟩ :
    {n : ℕ} →
    Word (SurrealFinite n) →
    Word (SurrealFinite n) →
    SurrealFinite (suc n)

------------------------------------------------------------------------
-- 2. Capstone for S1.
--
-- The carrier is named. S2 supplies birthday extraction and
-- monotonicity; S3 demonstrates Zero / One / NegOne as concrete
-- inhabitants; S4-S10 build order + arithmetic + integer
-- embedding + Cone bridge.
------------------------------------------------------------------------
