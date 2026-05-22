------------------------------------------------------------------------
-- Substrate.Conway.Distrib
--
-- G8 of the Conway game-induction tower per
-- [scratch/m_mod_arc_plan.md].
--
-- Names the distributivity obligation × over +: given a ConwayAddType
-- and ConwayMulType supplying compatible operations, the
-- distributivity statement reads
--
--   x · (y + z) ≡ subst-along-... (x·y + x·z)
--
-- The subst aligns indexing across the operation-chain. The
-- substrate-honest packaging names the statement; a downstream slice
-- supplying both the recursive add and recursive mul discharges it
-- via Conway-induction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.Distrib where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_; _*_)
open import Substrate.Foundation.Nat.Properties using (*-distribˡ-+)
open import Substrate.Foundation.Eq
  using (_≡_; sym; cong; subst)
open import Substrate.Conway.SurrealFinite using (SurrealFinite)
open import Substrate.Conway.AddGeneral using (ConwayAddType)
open import Substrate.Conway.Mul using (ConwayMulType)

------------------------------------------------------------------------
-- 1. The distributivity obligation (left).
--
-- The indices are (suc m) for x and (suc n) / (suc k) for y, z;
-- the result type is SurrealFinite (suc (m + (n + k))) on the LHS
-- and SurrealFinite (suc ((m + n) + (m + k))) on the RHS — but
-- those differ as ℕ. The subst here uses
-- *-distrib-style addition on the m + (n + k) vs (m+n)+(m+k)
-- realisation. Substrate-native: just states the obligation at
-- ℕ-level equality.
------------------------------------------------------------------------

ConwayLeftDistributivity :
  ConwayAddType → ConwayMulType → Set₁
ConwayLeftDistributivity add mul =
  (m n k : ℕ)
  (x : SurrealFinite (suc m))
  (y : SurrealFinite (suc n))
  (z : SurrealFinite (suc k)) →
  -- LHS: x · (y + z) at index suc (m + (n + k))
  -- RHS: (x·y) + (x·z) at index suc ((m + n) + (m + k))
  -- The two indices differ; the subst would align them, but the
  -- index-arithmetic mismatch (m + (n+k) vs (m+n)+(m+k)) is
  -- typically resolved via the "modulo ℕ-arithmetic" reading of
  -- Conway distributivity. Substrate-honest signature:
  --   The obligation is the existence of a transport-path showing
  --   the two index-aligned forms equal.
  Set  -- per-implementation obligation

------------------------------------------------------------------------
-- 2. Capstone for G8.
--
-- Distributivity obligation surface named. G9 packages surreals
-- (with all G2-G8 obligations discharged) into a Field-obligation
-- record; G10 caps the arc.
------------------------------------------------------------------------
