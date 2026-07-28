------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.PhaseA
--
-- QU4 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- Phase-A capstone. Re-exports the QU1-QU3 surface:
--   * QU1: Quotient + Canonical records (+ derived characterisations)
--   * QU2: QuotientUP record + trivial-QuotientUP + UPArrow registration
--   * QU3: canonical / trivial projection forms with the three laws
--
-- ===================================================================
-- PHASE-A SUMMARY (QU1-QU4)
-- ===================================================================
--
-- Quotient algebra LANDED as a substrate-native UP.
--
-- Carrier surface:
--   • Quotient A _≈_       — equivalence (refl/sym/trans)
--   • Canonical Q          — canonical-form extension
--
-- UP surface:
--   • QuotientUP A _≈_ Q   — factor / factor-≡-f / factor-respects /
--                            factor-unique
--   • trivial-QuotientUP   — discharges UP for any Quotient (HIT-free)
--   • Quotient-UPArrow     — UP-topos catalogue entry
--
-- Projection:
--   • trivial-projection    — id, always available
--   • canonical-projection  — canonical-form, requires Canonical
--   • q-respects-≈, q-idempotent, q-≈  — the three projection laws
--
-- Surreals integrate at Phase B without requiring a Canonical
-- extension, closing the loop with the term-algebra spine
-- per [[project-surreals-term-algebra-alignment]].
--
-- ===================================================================
-- WHAT PHASE B BRINGS
-- ===================================================================
--
-- QU5-QU10 attach the five substrate instances:
--   • Coxeter Word + normalize (Quotient + Canonical)
--   • ℚ via gcd reduction (Quotient + Canonical)
--   • Surreals via ≈ⁿ (Quotient only)
--   • V4-Cosets / S₄ / V₄ (Quotient + Canonical)
--   • F₂ (Bool) parity (Quotient + Canonical)
--
-- Each attaches via a single record-construction, demonstrating
-- that the UP pattern unifies the five hand-built instances.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.PhaseA where

open import Substrate.Algebra.Quotient
open import Substrate.Algebra.Quotient.Projection
open import Substrate.Category.UniversalProperty.Quotient