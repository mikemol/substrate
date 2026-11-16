------------------------------------------------------------------------
-- Substrate.Conway.Mul.ConwayMulType
--
-- Defines: ConwayMulType
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Conway.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.Mul.ConwayMulType where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Conway.SurrealFinite



------------------------------------------------------------------------
-- 1. The general multiplication type.
------------------------------------------------------------------------

ConwayMulType : Set
ConwayMulType =
  (m n : ℕ) →
  SurrealFinite (suc m) →
  SurrealFinite (suc n) →
  SurrealFinite (suc (m ℕ+ n))
