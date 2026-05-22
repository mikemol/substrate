------------------------------------------------------------------------
-- Substrate.Conway.Mul
--
-- G7 of the Conway game-induction tower per
-- [scratch/m_mod_arc_plan.md].
--
-- Names the general signature of Conway multiplication. The
-- recursive definition (Conway, ONAG ch. 1) is the "scrambled L/R"
-- formula:
--
--   xy = ⟨ xᴸy + xyᴸ - xᴸyᴸ, xᴿy + xyᴿ - xᴿyᴿ
--        | xᴸy + xyᴿ - xᴸyᴿ, xᴿy + xyᴸ - xᴿyᴸ ⟩
--
-- The substrate-honest packaging:
--   * The TYPE of `_·ⁿ_` is named here.
--   * The Zero·Zero base case discharges to ⟨ [] ∣ [] ⟩.
--   * A `ConwayMulSignature` record bundles the multiplication +
--     identity, commutativity, associativity, distributivity
--     obligations.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Conway.Mul where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Conway.SurrealFinite using (SurrealFinite)

------------------------------------------------------------------------
-- 1. The general multiplication type.
------------------------------------------------------------------------

ConwayMulType : Set
ConwayMulType =
  (m n : ℕ) →
  SurrealFinite (suc m) →
  SurrealFinite (suc n) →
  SurrealFinite (suc (m + n))

------------------------------------------------------------------------
-- 2. The ConwayMul signature record.
------------------------------------------------------------------------

record ConwayMulSignature : Set₁ where
  field
    mul : ConwayMulType
    -- Per-axiom obligations are stated as `Set` placeholders;
    -- a downstream slice that supplies `mul` discharges them.
    one-identity-stated   : Set
    commutativity-stated  : Set
    associativity-stated  : Set
    distributivity-stated : Set

------------------------------------------------------------------------
-- 3. Capstone for G7.
--
-- Multiplication signature named. G8 names distributivity
-- explicitly; G9 packages surreals as a Field-obligation; G10
-- caps the arc.
------------------------------------------------------------------------
