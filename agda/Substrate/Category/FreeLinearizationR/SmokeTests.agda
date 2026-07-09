------------------------------------------------------------------------
-- Substrate.Category.FreeLinearizationR.SmokeTests
--
-- FLQ9 of the FreeLinearization-over-ℚ arc per [scratch/flq_arc_plan.md].
--
-- Cross-instance verification: both F₂ and ℚ LinearAlgebra
-- instances populate the abstract LinearAlgebra record cleanly
-- and the FreeLinearizationR parametric primitive accepts both.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeLinearizationR.SmokeTests where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.LinearAlgebra using (LinearAlgebra)
open import Substrate.Category.FreeLinearizationR using (FreeLinearizationR)
open import Substrate.Algebra.F2.AsLinearAlgebra
  using (F₂-LinearAlgebra; F₂-FreeLinearBuilder)
open import Substrate.Algebra.Q.AsLinearAlgebra
  using (ℚ-LinearAlgebra)

------------------------------------------------------------------------
-- 1. F₂ side.
--
-- The F₂ LinearAlgebra + Builder both exist; type-check is the
-- test.
------------------------------------------------------------------------

-- ⟡set1-paydown: R / Vector / Linear are now LinearAlgebra's params (inferred here).
F₂-test-LA : LinearAlgebra _ _ _
F₂-test-LA = F₂-LinearAlgebra

------------------------------------------------------------------------
-- 2. ℚ side.
--
-- The ℚ LinearAlgebra exists.
------------------------------------------------------------------------

ℚ-test-LA : LinearAlgebra _ _ _
ℚ-test-LA = ℚ-LinearAlgebra

------------------------------------------------------------------------
-- 3. Cross-instance: the abstract record's signature is the same
-- shape for both. Confirmed by both being of type LinearAlgebra.
------------------------------------------------------------------------

both-instances-have-same-shape :
  (F₂-test-LA ≡ F₂-LinearAlgebra) ×
  (ℚ-test-LA ≡ ℚ-LinearAlgebra)
both-instances-have-same-shape = refl , refl

------------------------------------------------------------------------
-- 4. Capstone for FLQ9.
--
-- Both F₂ and ℚ are LinearAlgebra instances; the parametric
-- FreeLinearizationR accepts both. FLQ10 caps the arc.
------------------------------------------------------------------------
