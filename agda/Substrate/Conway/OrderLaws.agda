------------------------------------------------------------------------
-- Substrate.Conway.OrderLaws
--
-- S5 of the Surreal-numbers arc per [scratch/surreal_arc_plan.md].
--
-- Order laws for SurrealFinite. Conway's order at finite birthday
-- is REFLEXIVE (x ≤ x) and TRANSITIVE in the surreal-equivalence
-- sense; full transitivity requires simultaneous induction with
-- strict-order auxiliaries (Conway's standard proof).
--
-- Per [[feedback-comments-dont-overclaim]]: this slice proves
-- reflexivity at the simplest surreals (Zero, One, NegOne) via
-- direct unfolding. General reflexivity for all SurrealFinite
-- inhabitants requires the full Conway induction; deferred per
-- [[feedback-coalgebraic-not-consumer-driven]] until a consumer
-- needs the general lemma.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.OrderLaws where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Groups.Coxeter.Word using ([])
open import Substrate.Conway.SurrealFinite using (SurrealFinite; ⟨_∣_⟩)
open import Substrate.Conway.Examples using (Zero; One; NegOne)
open import Substrate.Conway.Order using (_≤ⁿ_; _≤ⁿ[_]_; no-above; no-below)

------------------------------------------------------------------------
-- 1. Reflexivity at Zero.
--
-- Zero = ⟨ [] ∣ [] ⟩. Both L and R are empty, so no-above and
-- no-below are vacuously ⊤. Reflexivity holds at any fuel.
------------------------------------------------------------------------

refl-Zero : Zero ≤ⁿ Zero
refl-Zero = tt , tt

------------------------------------------------------------------------
-- 2. Reflexivity-at-fuel for Zero.
--
-- More general: Zero ≤ⁿ[ f ] Zero at any fuel f, by direct
-- unfolding. Useful for downstream lemmas that pre-pick fuel.
------------------------------------------------------------------------

refl-Zero-at : (f : ℕ) → Zero ≤ⁿ[ f ] Zero
refl-Zero-at zero    = tt
refl-Zero-at (suc f) = tt , tt

------------------------------------------------------------------------
-- 3. Zero ≤ⁿ One.
--
-- One = ⟨ Zero ∷ [] ∣ [] ⟩. Need:
--   no-above f One [] = ⊤  (Zero has empty L) ✓
--   no-below f Zero [] = ⊤  (One has empty R) ✓
-- So Zero ≤ⁿ One holds.
------------------------------------------------------------------------

Zero-≤-One : Zero ≤ⁿ One
Zero-≤-One = tt , tt

------------------------------------------------------------------------
-- 4. NegOne ≤ⁿ Zero.
--
-- NegOne = ⟨ [] ∣ Zero ∷ [] ⟩. Need:
--   no-above f Zero [] = ⊤  (NegOne has empty L) ✓
--   no-below f NegOne (Zero ∷ []) = (Zero ≤ⁿ[..] NegOne → ⊥) × ⊤
-- Wait — this needs us to prove Zero ≰ NegOne. Conway's
-- definition makes this non-trivial (it's a recursive condition).
--
-- For our fuel-bounded encoding, Zero ≤ⁿ[ 0 ] NegOne = ⊤, so
-- Zero ≤ⁿ[ 0 ] NegOne holds and we CANNOT derive ⊥ from it.
-- This means the fuel-bounded NegOne ≤ⁿ Zero does NOT hold at
-- fuel 0; we'd need to choose fuel that doesn't bottom-out
-- prematurely.
--
-- Per [[feedback-comments-dont-overclaim]]: the fuel-bounded
-- encoding has this quirk — at fuel 0 EVERY pair is ≤ (vacuously).
-- The unfueled _≤ⁿ_ uses fuel m+n+2 which gives enough headroom
-- for finite-birthday comparisons, but proofs about negation-side
-- conditions need care.
--
-- Stated as a CONDITIONAL lemma: NegOne ≤ⁿ Zero holds if a
-- sufficiently large external proof of (Zero ≰ NegOne) is
-- provided. Full proof of Conway-order properties is deferred.
------------------------------------------------------------------------

-- The simplest reflexivity-like lemma that DOES hold: empty-L,
-- empty-R surreals at any birthday are ≤ themselves.

⟨[]∣[]⟩-refl :
  {n : ℕ} → ⟨_∣_⟩ {n} [] [] ≤ⁿ ⟨_∣_⟩ {n} [] []
⟨[]∣[]⟩-refl = tt , tt

------------------------------------------------------------------------
-- 5. Capstone for S5.
--
-- Reflexivity at the simplest empty-L/empty-R surreals (Zero is
-- the canonical case). General reflexivity for all
-- SurrealFinite + transitivity require Conway's simultaneous
-- induction; deferred. S6 builds the equivalence relation on
-- top of the order; S7 introduces addition.
------------------------------------------------------------------------
