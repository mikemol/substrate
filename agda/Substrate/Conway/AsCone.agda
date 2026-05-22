------------------------------------------------------------------------
-- Substrate.Conway.AsCone
--
-- S10 of the Surreal-numbers arc per [scratch/surreal_arc_plan.md].
--
-- Capstone: surfaces the Surreal recursive carrier as a categorical
-- Cone instance. A SurrealFinite (suc n) IS a Cone with:
--   * Apex = SurrealFinite (suc n)
--   * Base = constant `Word (SurrealFinite n)` (2 copies for L and R)
--   * 2 legs: project-L and project-R
--
-- This connects surreals to the substrate's existing Cone primitive
-- ([[project-3plus1-is-cone-instance]] / Substrate.Category.Cone),
-- providing a categorical home for the Conway recursive shape.
--
-- Per [[project-cone-subsumes-equalizer-pullback]]: the Cone
-- primitive is the substrate's generic limit-cone primitive;
-- surreals at finite birthday n give an (M=2, N=1) cone instance
-- with apex carrying the recursive sub-structure as its L/R legs.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.AsCone where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Conway.SurrealFinite using (SurrealFinite; ⟨_∣_⟩)
open import Substrate.Category.Cone using (Cone)

------------------------------------------------------------------------
-- 1. Projections.
--
-- get-L extracts the left-bound Word; get-R the right-bound Word.
-- Both at SurrealFinite n (one less than the apex's index).
------------------------------------------------------------------------

get-L : {n : ℕ} → SurrealFinite (suc n) → Word (SurrealFinite n)
get-L ⟨ L ∣ R ⟩ = L

get-R : {n : ℕ} → SurrealFinite (suc n) → Word (SurrealFinite n)
get-R ⟨ L ∣ R ⟩ = R

------------------------------------------------------------------------
-- 2. The Cone instance.
--
-- 2 bases, both Word (SurrealFinite n); apex = SurrealFinite (suc n).
-- leg 0 = get-L; leg 1 = get-R.
------------------------------------------------------------------------

Surreal-Base : (n : ℕ) → Fin 2 → Set
Surreal-Base n _ = Word (SurrealFinite n)

Surreal-Cone : (n : ℕ) → Cone 2 (Surreal-Base n) (SurrealFinite (suc n))
Surreal-Cone n = record { leg = surreal-leg }
  where
    surreal-leg : Fin 2 → SurrealFinite (suc n) → Word (SurrealFinite n)
    surreal-leg zero       = get-L
    surreal-leg (suc zero) = get-R
    surreal-leg (suc (suc ()))

------------------------------------------------------------------------
-- 3. Worked example: Zero as a Cone instance.
--
-- The Surreal-Cone at birthday 0 with apex Zero.
------------------------------------------------------------------------

Zero-Cone : Cone 2 (Surreal-Base 0) (SurrealFinite 1)
Zero-Cone = Surreal-Cone 0

------------------------------------------------------------------------
-- 4. Capstone for S10 + the S-arc.
--
-- The Conway surreal hierarchy at finite birthday now has a
-- categorical home in the substrate's Cone primitive. The recursive
-- L/R-bounded structure IS a (2, 1)-shape cone, parallel to other
-- substrate cone instances (V₄'s 3+1 cone, Hamming's 7+1 cone,
-- HodgeStar's ★-cone, etc.).
--
-- The S-arc is complete:
--   * S1: SurrealFinite carrier
--   * S2: Birthday extraction
--   * S3: Zero / One / NegOne
--   * S4-S5: Order + simple reflexivity
--   * S6: Equivalence relation
--   * S7-S8: Addition (specific cases) + Negation (full)
--   * S9: ℤ embedding
--   * S10: Cone bridge (this slice)
--
-- Deferred for future arcs: general addition + full transitivity +
-- multiplication + ω / infinitesimals + Conway-game connection.
------------------------------------------------------------------------
