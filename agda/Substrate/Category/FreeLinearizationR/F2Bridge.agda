------------------------------------------------------------------------
-- Substrate.Category.FreeLinearizationR.F2Bridge
--
-- FLQ5 of the FreeLinearization-over-ℚ arc per [scratch/flq_arc_plan.md].
--
-- Bridge: the parametric FreeLinearizationR at the F₂-LinearAlgebra
-- instance reproduces (up to record shape) the existing F₂-specific
-- Substrate.Category.FreeLinearization.
--
-- The two records have IDENTICAL field types (since F₂-LinearAlgebra
-- supplies Vector = F₂-Vector and Linear = F₂-Linear). The lift
-- functions in both directions are essentially the identity at the
-- type level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeLinearizationR.F2Bridge where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Category.FreeLinearization
  using (FreeLinearization)
  renaming (extension to F₂-extension;
            images to F₂-images;
            extension-on-basis to F₂-extension-on-basis;
            uniqueness to F₂-uniqueness)
open import Substrate.Category.FreeLinearizationR
  using (FreeLinearizationR)
open import Substrate.Algebra.F2.AsLinearAlgebra
  using (F₂-LinearAlgebra)

------------------------------------------------------------------------
-- 1. Lift: F₂-FreeLinearization → FreeLinearizationR at F₂.
--
-- The two records have the same field types because
-- F₂-LinearAlgebra populates Vector / Linear identically.
------------------------------------------------------------------------

F₂-to-R :
  {n m : ℕ} →
  FreeLinearization n m →
  FreeLinearizationR F₂-LinearAlgebra n m
F₂-to-R fl = record
  { images             = F₂-images fl
  ; extension          = F₂-extension fl
  ; extension-on-basis = F₂-extension-on-basis fl
  ; uniqueness         = F₂-uniqueness fl
  }

------------------------------------------------------------------------
-- 2. Descent: FreeLinearizationR at F₂ → F₂-FreeLinearization.
--
-- The reverse direction; same shape, identity at type level.
------------------------------------------------------------------------

R-to-F₂ :
  {n m : ℕ} →
  FreeLinearizationR F₂-LinearAlgebra n m →
  FreeLinearization n m
R-to-F₂ flr = record
  { images             = FreeLinearizationR.images flr
  ; extension          = FreeLinearizationR.extension flr
  ; extension-on-basis = FreeLinearizationR.extension-on-basis flr
  ; uniqueness         = FreeLinearizationR.uniqueness flr
  }

------------------------------------------------------------------------
-- 3. Capstone for FLQ5.
--
-- F₂ bridge complete. The parametric FreeLinearizationR is a
-- strict generalisation: every existing F₂-FreeLinearization
-- lifts to the parametric version (and back). FLQ6 supplies
-- the ℚ instance; FLQ7 the ℚ free-linearize constructor.
------------------------------------------------------------------------
