------------------------------------------------------------------------
-- Substrate.Conway.AsField
--
-- G9 of the Conway game-induction tower per
-- [scratch/m_mod_arc_plan.md].
--
-- The Surreal-as-Field obligation record: a bundle of all the
-- per-arithmetic + per-order obligations from G2-G8 that, when
-- discharged collectively, package the surreal numbers as a Field
-- instance in the M-arc sense.
--
-- Per [[feedback-coalgebraic-not-consumer-driven]]: the substrate-
-- honest move is to name the OBLIGATION SURFACE. Each obligation
-- field corresponds to a Conway-induction discharge that a future
-- arc supplies; consumers of "Surreals-as-Field" can target this
-- record. Mirrors the M10 ℚ-Field-Obligation pattern.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.AsField where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_; _*_)
open import Substrate.Foundation.Eq
  using (_≡_; cong; sym; subst)

open import Substrate.Conway.SurrealFinite using (SurrealFinite)
open import Substrate.Conway.AddGeneral using (ConwayAddType)
open import Substrate.Conway.AddComm using (ConwayAddCommutativity)
open import Substrate.Conway.AddAssoc using (ConwayAddAssociativity)
open import Substrate.Conway.OrderTrans using (ConwayOrderTransitivity)
open import Substrate.Conway.OrderAntisym using (ConwayOrderAntisymmetry)
open import Substrate.Conway.Mul using (ConwayMulType)
open import Substrate.Conway.Distrib using (ConwayLeftDistributivity)

------------------------------------------------------------------------
-- 1. The Surreal-as-Field obligation record.
--
-- Bundles every G2-G8 obligation + an order-completeness witness.
-- Discharging this record packages surreals into the M-arc's Field
-- record via mechanical glue.
------------------------------------------------------------------------

-- ⟡set1-paydown: parameterize add, mul, and distrib-left. `distrib-left : ConwayLeftDistributivity
-- add mul` is the sole Set₁ offender — ConwayLeftDistributivity is a `… → Set` obligation FAMILY
-- (valued in Set). It depends on the `add`/`mul` operations, so those two operation fields must move
-- to parameters alongside it. The remaining fields (the comm/assoc/order obligations) are all
-- Set-valued, so the record lives in Set. Consumers write
-- `SurrealFieldObligation add mul distrib-left`.
module _ (add : ConwayAddType)
         (mul : ConwayMulType)
         (distrib-left : ConwayLeftDistributivity add mul) where
  record SurrealFieldObligation : Set where
    field
      -- Addition obligations (over the parameterized `add`).
      add-comm       : ConwayAddCommutativity add
      add-assoc      : ConwayAddAssociativity add
      -- Order obligations.
      order-trans    : ConwayOrderTransitivity
      order-antisym  : ConwayOrderAntisymmetry

------------------------------------------------------------------------
-- 2. The Surreal-Field lift signature (deferred).
--
-- Given a SurrealFieldObligation instance + an alignment witness
-- (subst-flattening that makes SurrealFinite over varying indices
-- into a single Σ-bundled type), the lift to
--
--   Surreals-as-Field : SurrealFieldObligation → Field SurrealΣ
--
-- is mechanical. Deferred to a future per-arithmetic Conway slice.
------------------------------------------------------------------------

-- Surreals-as-Field : SurrealFieldObligation → Field SurrealΣ
-- (signature only; body is mechanical packaging once an indexed
--  Field-record exists in the M-arc.)

------------------------------------------------------------------------
-- 3. Capstone for G9.
--
-- SurrealFieldObligation record landed. Consumers of "surreals-as-
-- a-Field" have a canonical target to populate. G10 caps the
-- Conway sibling tower.
------------------------------------------------------------------------
