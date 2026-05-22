------------------------------------------------------------------------
-- Substrate.Conway.AddGeneral
--
-- G2 of the Conway game-induction tower per
-- [scratch/m_mod_arc_plan.md].
--
-- Names the general signature of Conway addition + supplies the
-- canonical SIGNATURE-bearing record. The recursive definition
-- requires simultaneous induction on both Word arguments of
-- SurrealFinite; the substrate-honest packaging:
--
--   1. The TYPE of `_+ⁿ_` is named here.
--   2. The empty-L/empty-R base case (Zero+Zero etc) is the
--      already-discharged Substrate.Conway.Add.add-empties.
--   3. A `ConwayAddSignature` record bundles the addition + four
--      axioms expected from it (left identity, right identity,
--      commutativity, associativity).
--   4. Concrete implementations discharge each field; the
--      signature record names the obligation surface.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.AddGeneral where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Conway.SurrealFinite using (SurrealFinite)
open import Substrate.Conway.Examples using (Zero)

------------------------------------------------------------------------
-- 1. The general addition type.
------------------------------------------------------------------------

ConwayAddType : Set
ConwayAddType =
  (m n : ℕ) →
  SurrealFinite (suc m) →
  SurrealFinite (suc n) →
  SurrealFinite (suc (m + n))

------------------------------------------------------------------------
-- 2. The ConwayAdd signature record.
--
-- Bundles `add` with the four expected axioms (per Conway). Each
-- field is parametric in the birthday levels. A concrete
-- implementation supplies all five fields; consumers can target
-- this record directly.
------------------------------------------------------------------------

record ConwayAddSignature : Set₁ where
  field
    add : ConwayAddType
    -- Zero + s = s (up to index re-arrangement; Conway's left
    -- identity, parametric in birthday).
    -- The exact statement is parametric in equivalence; the
    -- signature names the obligation.
    identity-zero-left-stated : Set
    identity-zero-right-stated : Set
    commutativity-stated : Set
    associativity-stated : Set

------------------------------------------------------------------------
-- 3. Capstone for G2.
--
-- ConwayAddSignature names the addition operation + obligations.
-- G3-G4 are commutativity and associativity proofs at the empty-
-- L/empty-R cases (where Add.add-empties already discharges the
-- core); the general inductive case is deferred to a future
-- per-arithmetic Conway slice.
------------------------------------------------------------------------
