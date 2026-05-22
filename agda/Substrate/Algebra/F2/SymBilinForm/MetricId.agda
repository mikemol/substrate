------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.MetricId
--
-- metric-id : the n-parametric diagonal identity. Defined recursively
-- on the simultaneous Fin patterns — no decidable equality needed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.MetricId where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Algebra.F2 using (𝟘; 𝟙)
open import Substrate.Algebra.F2.SymBilinForm.BilinForm using (BilinForm)

metric-id : ∀ {n} → BilinForm n
metric-id zero    zero    = 𝟙
metric-id zero    (suc _) = 𝟘
metric-id (suc _) zero    = 𝟘
metric-id (suc i) (suc j) = metric-id i j
