------------------------------------------------------------------------
-- Substrate.Category.FreeLinearizationR.QExamples
--
-- FLQ8 of the FreeLinearization-over-ℚ arc per [scratch/flq_arc_plan.md].
--
-- Worked examples demonstrating the parametric FreeLinearizationR
-- + ℚ-LinearAlgebra used together. Mostly type-level smoke tests:
-- ℚ-Vector, ℚ-Linear, basis-ℚ all accessible through the abstract
-- LinearAlgebra interface.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeLinearizationR.QExamples where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.Q using (ℚ; 0ℚ; 1ℚ; mkℚ)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Q.Vector using (Vector; basis-ℚ)
open import Substrate.Algebra.Q.Linear using (Linear; id-LQ; apply)
open import Substrate.Algebra.Q.AsLinearAlgebra using (ℚ-LinearAlgebra)
open import Substrate.Category.LinearAlgebra using (LinearAlgebra)
open import Substrate.Category.FreeLinearizationR using (FreeLinearizationR)

------------------------------------------------------------------------
-- 1. ℚ-Vector at dimension 3 with rational entries.
------------------------------------------------------------------------

half : ℚ
half = mkℚ (+ 1) 1   -- 1/2

third : ℚ
third = mkℚ (+ 1) 2  -- 1/3

example-rational-vector : Vector 3
example-rational-vector = half ∷ third ∷ 1ℚ ∷ []
  where open import Substrate.Foundation.Vec using (_∷_; [])

------------------------------------------------------------------------
-- 2. Accessing ℚ-LinearAlgebra through the abstract interface.
--
-- Demonstrates that the LinearAlgebra record successfully exposes
-- the ℚ-side operations at the abstract level. Type-checking
-- alone is the test (no proof obligation).
------------------------------------------------------------------------

-- Pull the abstract fields out via the record.
abstract-zeroR : LinearAlgebra.R ℚ-LinearAlgebra
abstract-zeroR = LinearAlgebra.zeroR ℚ-LinearAlgebra

abstract-oneR : LinearAlgebra.R ℚ-LinearAlgebra
abstract-oneR = LinearAlgebra.oneR ℚ-LinearAlgebra

-- Confirm: abstract-zeroR ≡ 0ℚ via reduction.
abstract-zeroR-is-0ℚ : abstract-zeroR ≡ 0ℚ
abstract-zeroR-is-0ℚ = refl

abstract-oneR-is-1ℚ : abstract-oneR ≡ 1ℚ
abstract-oneR-is-1ℚ = refl

------------------------------------------------------------------------
-- 3. The basis vectors at ℚ via the abstract interface.
------------------------------------------------------------------------

abstract-basis-3-0 : Vector 3
abstract-basis-3-0 = LinearAlgebra.basis ℚ-LinearAlgebra {3} zero

------------------------------------------------------------------------
-- 4. Identity Linear via the abstract interface.
--
-- LinearAlgebra.apply ℚ-LinearAlgebra id-LQ v ≡ v (for any v).
------------------------------------------------------------------------

abstract-apply-id :
  {n : ℕ} (v : Vector n) →
  LinearAlgebra.apply ℚ-LinearAlgebra id-LQ v ≡ v
abstract-apply-id _ = refl

------------------------------------------------------------------------
-- 5. Capstone for FLQ8.
--
-- Worked examples demonstrate the parametric FreeLinearizationR +
-- LinearAlgebra interface working at ℚ. FLQ9 cross-instance
-- smoke tests; FLQ10 capstone.
------------------------------------------------------------------------
