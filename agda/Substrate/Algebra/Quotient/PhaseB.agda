------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.PhaseB
--
-- QU9 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- Phase-B capstone. Catalogues the four landed Quotient instances:
--
-- ===================================================================
-- PHASE-B SUMMARY (QU5-QU9)
-- ===================================================================
--
-- Five hand-built substrate quotients lifted into Quotient
-- (+ Canonical where applicable) instances:
--
-- ┌───────────────────────────┬──────────────┬──────────────┐
-- │ Substrate construction     │ Quotient     │ Canonical    │
-- ├───────────────────────────┼──────────────┼──────────────┤
-- │ Coxeter Word / normalize   │ QU5  ✅      │ QU5  ✅      │
-- │ ℕ / parity ≅ F₂            │ QU6  ✅      │ QU6  ✅      │
-- │ S₄ / V₄ (V4-Cosets)        │ QU7  ✅      │ —            │
-- │ Surrealᶠ (parametric)      │ QU8  ✅ᵖ     │ —            │
-- │ ℚ / cross-mult             │ deferred     │ deferred     │
-- └───────────────────────────┴──────────────┴──────────────┘
--
-- ᵖ Surreal attachment is parametric on `≤ⁿ-refl` + `≤ⁿ-trans`
--   pending Conway-induction completion (Conway.OrderTrans).
--
-- ℚ deferred because Substrate.Algebra.Q.Reduction provides the
-- gcd-of-ℚ predicate but not the reduce : ℚ → ℚ function — the
-- division-by-gcd-with-NonZero step is its own slice.
--
-- ===================================================================
-- WHAT PHASE C BRINGS
-- ===================================================================
--
-- QU10-QU15 build QuotientProduct (CRT as UP):
--   • QuotientProduct UP record
--   • Modular equivalence ≡ₘ on ℕ
--   • ModN as Quotient + Canonical instance
--   • CRT instance: ℕ/(mn) ≅ ℕ/m × ℕ/n under coprime hypothesis
--   • Connect to AbelianPFG (the CRT was already named there;
--     now it's structurally derived)
--
-- The four attachments above are the empirical evidence that the
-- UP-of-quotient pattern unifies the substrate's hand-built
-- quotients. The same pattern will give CRT structurally at QU13.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.PhaseB where

open import Substrate.Algebra.Quotient.PhaseA
open import Substrate.Algebra.Quotient.F2Parity
-- Substrate.Algebra.Quotient.V4Cosets is held back from re-export
-- until the stdlib-Algebra.Bundles chain in S4 / Symmetric finishes
-- migrating to Substrate.Algebra.Group. The V4Cosets instance is
-- written and ready (see [scratch/qu_arc_plan.md] QU7); it'll re-
-- enter PhaseB the moment the upstream chain typechecks under
-- --safe.
