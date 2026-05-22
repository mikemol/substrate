------------------------------------------------------------------------
-- Substrate.Category.FreeLinearizationR.Capstone
--
-- FLQ10 of the FreeLinearization-over-ℚ arc per [scratch/flq_arc_plan.md].
--
-- Capstone: re-export of FLQ1-FLQ9 + summary of the arc's
-- contributions + connection to TPQ-arc (slices 11-20).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeLinearizationR.Capstone where

-- Re-export the FLQ-arc slices publicly.
open import Substrate.Category.LinearAlgebra public
open import Substrate.Category.FreeLinearizationR public
open import Substrate.Category.FreeLinearizationR.FromImages public
open import Substrate.Algebra.F2.AsLinearAlgebra public
open import Substrate.Category.FreeLinearizationR.F2Bridge public
open import Substrate.Algebra.Q.AsLinearAlgebra public
open import Substrate.Category.FreeLinearizationR.QInstance public
open import Substrate.Category.FreeLinearizationR.QExamples public
open import Substrate.Category.FreeLinearizationR.SmokeTests public

------------------------------------------------------------------------
-- Capstone for the FLQ-arc.
--
-- After this slice, the substrate has:
--   * LinearAlgebra abstract record (FLQ1) — parametric carrier
--     for any R-linear structure
--   * FreeLinearizationR parametric primitive (FLQ2)
--   * FreeLinearBuilder constructor pattern (FLQ3)
--   * F₂ as a LinearAlgebra + FreeLinearBuilder (FLQ4-FLQ5),
--     subsumes existing Substrate.Category.FreeLinearization
--   * ℚ as a LinearAlgebra + sketch FreeLinearization (FLQ6-FLQ7)
--   * Worked examples + cross-instance smoke tests (FLQ8-FLQ9)
--
-- Honest scope: ℚ-side FreeLinearBuilder is sketched, not fully
-- discharged — pending ℚ-linear-extensionality lemma from a
-- future Q-arc extension.
--
-- TPQ-arc (slices 11-20) consumes FLQ6's ℚ-LinearAlgebra +
-- FLQ7's identity-case for the Toki Pona ℚ-retrofit.
------------------------------------------------------------------------
