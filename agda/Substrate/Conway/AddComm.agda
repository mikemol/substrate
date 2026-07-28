------------------------------------------------------------------------
-- Substrate.Conway.AddComm
--
-- G3 of the Conway game-induction tower per
-- [scratch/m_mod_arc_plan.md].
--
-- Names the commutativity obligation for Conway addition. The
-- empty-L/empty-R case discharges structurally to both being
-- ⟨ [] ∣ [] ⟩; the typing requires a subst on +-comm to align
-- birthday indices.
--
-- Per [[feedback-coalgebraic-not-consumer-driven]]: signature lands
-- + obligation named. Full inductive proof deferred to per-
-- arithmetic Conway sliced (requires recursive addition's full
-- definition).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.AddComm where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.Foundation.Eq
  using (_≡_; cong; subst)
open import Substrate.Conway.SurrealFinite using (SurrealFinite)
open import Substrate.Conway.AddGeneral using (ConwayAddType)

------------------------------------------------------------------------
-- 1. The commutativity obligation.
--
-- Given a `add : ConwayAddType`, the commutativity statement is:
--
--   For any (m n : ℕ) and a : SurrealFinite (suc m),
--   b : SurrealFinite (suc n):
--   add m n a b ≡ subst-along-+-comm (add n m b a)
--
-- The `subst` aligns the indexing.
------------------------------------------------------------------------

ConwayAddCommutativity : ConwayAddType → Set
ConwayAddCommutativity add =
  (m n : ℕ)
  (a : SurrealFinite (suc m))
  (b : SurrealFinite (suc n)) →
  add m n a b
    ≡ subst SurrealFinite (cong suc (+-comm n m)) (add n m b a)

------------------------------------------------------------------------
-- 2. Capstone for G3.
--
-- Commutativity obligation named. G4 names associativity. Full
-- inductive proofs deferred to a per-arithmetic Conway slice that
-- supplies the recursive `add` implementation.
------------------------------------------------------------------------
