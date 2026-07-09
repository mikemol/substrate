------------------------------------------------------------------------
-- Substrate.Algebra.F2.AsLinearAlgebra
--
-- FLQ4 of the FreeLinearization-over-ℚ arc per [scratch/flq_arc_plan.md].
--
-- Packages the existing F₂-Vector + F₂-Linear infrastructure as
-- a LinearAlgebra instance (FLQ1) + a FreeLinearBuilder (FLQ3).
-- Witnesses that the substrate's F₂ ecosystem fits the parametric
-- abstraction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.AsLinearAlgebra where

open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ; _+ⱽ_; _*ₛ_; basis)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)
open import Substrate.Algebra.F2.Linear.Universal
  using (linear-extensionality)
open import Substrate.Category.LinearAlgebra using (LinearAlgebra)
open import Substrate.Category.FreeLinearizationR.FromImages
  using (FreeLinearBuilder)

------------------------------------------------------------------------
-- 1. F₂ LinearAlgebra instance.
------------------------------------------------------------------------

-- ⟡set1-paydown: R / Vector / Linear are now LinearAlgebra's params (F₂, Vector, Linear).
F₂-LinearAlgebra : LinearAlgebra F₂ Vector Linear
F₂-LinearAlgebra = record
  { zeroR  = 𝟘
  ; oneR   = 𝟙
  ; zeroV  = 𝟎ⱽ
  ; _+V_   = _+ⱽ_
  ; _*S_   = _*ₛ_
  ; basis  = basis
  ; apply  = apply
  }

------------------------------------------------------------------------
-- 2. F₂ FreeLinearBuilder instance.
--
-- Uses the substrate's existing linear-from-images +
-- apply-linear-from-images-basis + linear-extensionality lemmas.
------------------------------------------------------------------------

-- ⟡set1-paydown: FreeLinearBuilder now takes LinearAlgebra's R/Vector/Linear params.
F₂-FreeLinearBuilder : FreeLinearBuilder F₂ Vector Linear F₂-LinearAlgebra
F₂-FreeLinearBuilder = record
  { linear-from-images-LA    = linear-from-images
  ; apply-on-basis-LA        = apply-linear-from-images-basis
  ; linear-extensionality-LA = linear-extensionality
  }

------------------------------------------------------------------------
-- 3. Capstone for FLQ4.
--
-- F₂ as a LinearAlgebra + FreeLinearBuilder. FLQ5 bridges to
-- the existing Substrate.Category.FreeLinearization to show the
-- parametric primitive subsumes the F₂-specific original.
------------------------------------------------------------------------
