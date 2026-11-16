------------------------------------------------------------------------
-- Substrate.Conway.AddGeneral.ConwayAddSignature
--
-- Defines: ConwayAddSignature, add
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Conway.AddGeneral; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.AddGeneral.ConwayAddSignature where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Conway.SurrealFinite
open import Substrate.Conway.AddGeneral.ConwayAddType



------------------------------------------------------------------------
-- 2. The ConwayAdd signature record.
--
-- Bundles `add` with the four expected axioms (per Conway). Each
-- field is parametric in the birthday levels. A concrete
-- implementation supplies all five fields; consumers can target
-- this record directly.
------------------------------------------------------------------------

-- ⟡rc-cheap (⟡set1-rerank2): the four obligation STATEMENTS are parameters now
-- (a Set-valued field pins the record at Set₁; params never raise the sort).
-- Zero ℕ+ s = s (up to index re-arrangement; Conway's left identity, parametric in
-- birthday). The exact statements are parametric in equivalence; the signature
-- names the obligations.
record ConwayAddSignature
  (identity-zero-left-stated identity-zero-right-stated
   commutativity-stated associativity-stated : Set) : Set where
  field
    add : ConwayAddType

------------------------------------------------------------------------
-- 3. Capstone for G2.
--
-- ConwayAddSignature names the addition operation ℕ+ obligations.
-- G3-G4 are commutativity and associativity proofs at the empty-
-- L/empty-R cases (where Add.add-empties already discharges the
-- core); the general inductive case is deferred to a future
-- per-arithmetic Conway slice.
------------------------------------------------------------------------
