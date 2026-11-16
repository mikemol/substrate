------------------------------------------------------------------------
-- Substrate.Conway.AddGeneral.ConwayAddType
--
-- Defines: ConwayAddType
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Conway.AddGeneral; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.AddGeneral.ConwayAddType where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Conway.SurrealFinite



------------------------------------------------------------------------
-- 1. The general addition type.
------------------------------------------------------------------------

ConwayAddType : Set
ConwayAddType =
  (m n : ℕ) →
  SurrealFinite (suc m) →
  SurrealFinite (suc n) →
  SurrealFinite (suc (m ℕ+ n))
