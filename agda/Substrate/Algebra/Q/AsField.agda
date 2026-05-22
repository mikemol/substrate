------------------------------------------------------------------------
-- Substrate.Algebra.Q.AsField
--
-- M10 of the Algebra Ladder arc per [scratch/m_mod_arc_plan.md].
--
-- Packages ℚ as a Field instance — STRUCTURAL SCAFFOLDING.
--
-- HONEST SCOPE: The Q-arc supplied ℚ's operations (Q5 Arithmetic,
-- Q6 Order, Q7 Embeddings) but DID NOT prove the ring-laws. Filling
-- the M8 Field record requires:
--   * +ℚ associativity, commutativity, identity, inverse
--   * *ℚ associativity, commutativity, identity
--   * Distributivity of *ℚ over +ℚ
--   * Zero-absorption
--   * Multiplicative inverse for non-zero
--
-- ALL of these hold (ℚ is a Field), but each requires substantial
-- per-arithmetic proof work that exceeds a 1-slice budget. This
-- slice lands:
--   * The ℚ-Magma structures (additive + multiplicative) — provable
--     trivially (just the operation, no laws).
--   * A `ℚ-Field-Obligation` record documenting precisely which
--     lemmas a future slice or arc must discharge to upgrade the
--     Magma scaffolding to a full Field instance.
--
-- Per the user's STRUCTURAL gap-closure discipline: the SHAPE
-- lands here; the per-law content is honestly named as remaining
-- work. ANY consumer needing a ℚ-Field instance has a
-- canonical NAMED TARGET to discharge.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.AsField where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.Q using (ℚ; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Arithmetic using (_+ℚ_; _*ℚ_; -ℚ_)
open import Substrate.Algebra.Magma using (Magma)

------------------------------------------------------------------------
-- 1. ℚ-Magma (additive).
------------------------------------------------------------------------

ℚ-+-Magma : Magma ℚ
ℚ-+-Magma = record { _·_ = _+ℚ_ }

------------------------------------------------------------------------
-- 2. ℚ-Magma (multiplicative).
------------------------------------------------------------------------

ℚ-·-Magma : Magma ℚ
ℚ-·-Magma = record { _·_ = _*ℚ_ }

------------------------------------------------------------------------
-- 3. ℚ-Field obligation record.
--
-- Names the exact lemmas needed to upgrade the Magma scaffolding
-- to a full Field instance. The Q-arc's deferred ring-laws ARE
-- these fields.
------------------------------------------------------------------------

record ℚ-Field-Obligation : Set where
  field
    -- Additive structure obligations.
    +ℚ-assoc      : (a b c : ℚ) → ((a +ℚ b) +ℚ c) ≡ (a +ℚ (b +ℚ c))
    +ℚ-comm       : (a b : ℚ) → (a +ℚ b) ≡ (b +ℚ a)
    +ℚ-identityˡ  : (a : ℚ) → (0ℚ +ℚ a) ≡ a
    +ℚ-identityʳ  : (a : ℚ) → (a +ℚ 0ℚ) ≡ a
    +ℚ-inverseˡ   : (a : ℚ) → ((-ℚ a) +ℚ a) ≡ 0ℚ
    +ℚ-inverseʳ   : (a : ℚ) → (a +ℚ (-ℚ a)) ≡ 0ℚ
    -- Multiplicative structure obligations.
    *ℚ-assoc      : (a b c : ℚ) → ((a *ℚ b) *ℚ c) ≡ (a *ℚ (b *ℚ c))
    *ℚ-comm       : (a b : ℚ) → (a *ℚ b) ≡ (b *ℚ a)
    *ℚ-identityˡ  : (a : ℚ) → (1ℚ *ℚ a) ≡ a
    *ℚ-identityʳ  : (a : ℚ) → (a *ℚ 1ℚ) ≡ a
    -- Ring / Field obligations.
    distribˡ      : (a b c : ℚ) → (a *ℚ (b +ℚ c)) ≡ ((a *ℚ b) +ℚ (a *ℚ c))
    distribʳ      : (a b c : ℚ) → ((b +ℚ c) *ℚ a) ≡ ((b *ℚ a) +ℚ (c *ℚ a))
    zero-absorbˡ  : (a : ℚ) → (0ℚ *ℚ a) ≡ 0ℚ
    zero-absorbʳ  : (a : ℚ) → (a *ℚ 0ℚ) ≡ 0ℚ

------------------------------------------------------------------------
-- 4. Once a ℚ-Field-Obligation instance is supplied, it lifts
-- (mechanically) to a full Field record via the M1-M8 ladder.
-- The lift is recorded as a future slice / arc obligation.
------------------------------------------------------------------------

-- ℚ-Field-from-obligation :
--   ℚ-Field-Obligation → Field ℚ
-- ℚ-Field-from-obligation o = ...
-- Body: mechanical packaging of obligation fields into the M1-M8
-- record stack. Deferred.

------------------------------------------------------------------------
-- 5. Capstone for M10 + M-arc.
--
-- M-arc lands the algebra ladder (Magma → Field) + F₂ instance
-- (M9) + ℚ-Magma scaffolding + ℚ-Field obligation (M10).
--
-- The STRUCTURAL gap-closure is real:
--   * Any consumer needing ℚ-ring-laws has a canonical named
--     record to point at.
--   * Future per-arithmetic slices discharge the obligation
--     fields one-by-one; each fills a Field-record slot directly.
--   * F₁ + F₂ as Field instances are complete TODAY (M3, M9).
--
-- The Mod-arc (slices 11-20) builds Module-over-Ring on top of
-- M7; F₂-Vector and ℚ-Vector retrofits land at Mod6-Mod7.
------------------------------------------------------------------------
