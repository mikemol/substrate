------------------------------------------------------------------------
-- Substrate.Conway.OrderTrans
--
-- G5 of the Conway game-induction tower per
-- [scratch/m_mod_arc_plan.md].
--
-- Names the transitivity obligation for Conway's surreal order
-- (`_≤ⁿ_` from Substrate.Conway.Order).
--
-- Conway's order transitivity descends through birthday-induction:
-- x ≤ⁿ y and y ≤ⁿ z reduce, by the recursive definition, to
-- no-above/no-below claims at strictly smaller fuel that can be
-- combined into the transitive claim at the original fuel.
--
-- Substrate-honest: the signature is named; the recursive proof
-- requires the full birthday-induction machinery and is deferred.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.OrderTrans where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Conway.SurrealFinite using (SurrealFinite)
open import Substrate.Conway.Order using (_≤ⁿ_)

------------------------------------------------------------------------
-- 1. The transitivity obligation.
------------------------------------------------------------------------

ConwayOrderTransitivity : Set
ConwayOrderTransitivity =
  {l m n : ℕ}
  (x : SurrealFinite (suc l))
  (y : SurrealFinite (suc m))
  (z : SurrealFinite (suc n)) →
  x ≤ⁿ y → y ≤ⁿ z → x ≤ⁿ z

------------------------------------------------------------------------
-- 2. Capstone for G5.
--
-- Transitivity obligation named. G6 names antisymmetry up to ≈.
-- Full recursive proof of ConwayOrderTransitivity is the canonical
-- Conway-induction discharge target.
------------------------------------------------------------------------
