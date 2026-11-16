------------------------------------------------------------------------
-- Substrate.Conway.BirthdayOrdered.BirthdayOrdered
--
-- Defines: BirthdayOrdered, index, surreal
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Conway.BirthdayOrdered; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.BirthdayOrdered.BirthdayOrdered where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Conway.SurrealFinite



------------------------------------------------------------------------
-- 1. The BirthdayOrdered record.
--
-- A BirthdayOrdered is a (Σ-bundled) SurrealFinite with its index
-- exposed at the type level for recursion-tracking.
------------------------------------------------------------------------

record BirthdayOrdered : Set where
  field
    index   : ℕ
    surreal : SurrealFinite (suc index)

open BirthdayOrdered public
