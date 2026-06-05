------------------------------------------------------------------------
-- Substrate.Category.FreeLinearizationR.QInstance
--
-- FLQ7 of the FreeLinearization-over-ℚ arc per [scratch/flq_arc_plan.md].
--
-- ℚ-side FreeLinearizationR partial instance.
--
-- HONEST SCOPE: The Q-arc supplies ℚ-Vector + ℚ-Linear (Q8, Q9)
-- but does NOT yet prove ℚ-linear-extensionality. Without that
-- lemma, the full `linear-from-images-ℚ` + `ℚ-FreeLinearBuilder`
-- can't be constructed in --safe.
--
-- This slice provides:
--   1. A `QFreeLinearizationSketch` record naming the data-shape
--      that a future arc completing ℚ-extensionality would fill.
--   2. The API signature for `linear-from-images-ℚ` as a
--      documented obligation.
--
-- Per [[feedback-coalgebraic-not-consumer-driven]]: the full ℚ
-- FreeLinearBuilder is forced when a consumer demands it; this
-- slice supplies the SKETCH that consumers can reference, and the
-- F₂-side bridge (FLQ5) suffices to demonstrate the parametric
-- primitive's reach.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeLinearizationR.QInstance where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)

open import Substrate.Algebra.Q.Vector using (Vector; basis-ℚ)
open import Substrate.Algebra.Q.Linear using (Linearℚ)
open import Substrate.Algebra.Q.AsLinearAlgebra using (ℚ-LinearAlgebra)

------------------------------------------------------------------------
-- 1. QFreeLinearizationSketch: the data shape a full instance
-- would have.
--
-- A future Q-arc extension supplying ℚ-extensionality would
-- populate this record's fields.
------------------------------------------------------------------------

record QFreeLinearizationSketch : Set where
  field
    can-linearize-from-images :
      {n m : ℕ} → (Fin n → Vector m) → Linearℚ n m

------------------------------------------------------------------------
-- 2. Note on the identity case.
--
-- For the special case `images = basis-ℚ`, the linear extension
-- is the identity Linear (Q9's id-LQ). This is the only case
-- the slice can fully discharge without ℚ-extensionality. The
-- general parametric construction remains the sketch.
------------------------------------------------------------------------

-- The signature `linear-from-images-ℚ-identity-case : (n : ℕ) →
-- Linear n n` lives in Q9 as `id-LQ`. Consumers needing the
-- identity case use that directly.

------------------------------------------------------------------------
-- 3. Capstone for FLQ7.
--
-- ℚ FreeLinearization at sketch level. FLQ8 demonstrates the
-- parametric primitive working end-to-end using the F₂ side
-- (which IS fully discharged) + the ℚ-LinearAlgebra structure
-- as the codomain (ℚ-LinearAlgebra is usable independently of
-- ℚ-extensionality).
------------------------------------------------------------------------
