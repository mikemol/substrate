------------------------------------------------------------------------
-- Substrate.Algebra.Q.AsLinearAlgebra
--
-- FLQ6 of the FreeLinearization-over-ℚ arc per [scratch/flq_arc_plan.md].
--
-- Packages Q-arc's ℚ-Vector + ℚ-Linear into a LinearAlgebra
-- instance (FLQ1). Sister to FLQ4's F₂-LinearAlgebra.
--
-- Note: ℚ does NOT yet have a FreeLinearBuilder analog (the
-- substrate doesn't yet supply linear-from-images-ℚ +
-- ℚ-extensionality). Those would be FLQ7 + future arc work.
-- This slice supplies the LinearAlgebra-level structure; the
-- Builder is left as a follow-up obligation per
-- [[feedback-coalgebraic-not-consumer-driven]].
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.AsLinearAlgebra where

open import Substrate.Algebra.Q using (ℚ; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Vector
  using (Vector; 𝟎ℚⱽ; _+ℚⱽ_; _*ℚₛ_; basis-ℚ)
open import Substrate.Algebra.Q.Linear using (Linearℚ; apply)
open import Substrate.Category.LinearAlgebra using (LinearAlgebra)

------------------------------------------------------------------------
-- 1. ℚ LinearAlgebra instance.
------------------------------------------------------------------------

ℚ-LinearAlgebra : LinearAlgebra
ℚ-LinearAlgebra = record
  { R      = ℚ
  ; Vector = Vector
  ; Linear = Linearℚ
  ; zeroR  = 0ℚ
  ; oneR   = 1ℚ
  ; zeroV  = 𝟎ℚⱽ
  ; _+V_   = _+ℚⱽ_
  ; _*S_   = _*ℚₛ_
  ; basis  = basis-ℚ
  ; apply  = apply
  }

------------------------------------------------------------------------
-- 2. Capstone for FLQ6.
--
-- ℚ at the LinearAlgebra layer. FLQ7 supplies the
-- linear-from-images-ℚ constructor as a Builder; FLQ8 worked
-- examples.
------------------------------------------------------------------------
