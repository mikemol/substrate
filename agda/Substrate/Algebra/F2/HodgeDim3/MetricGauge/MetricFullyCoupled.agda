------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricFullyCoupled
--
-- Exemplar fully-coupled metric: a=1, b=c=0, d=e=f=1. Det = 1.
-- Structural exemplar of the fully-coupled shape-class.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricFullyCoupled where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq  using (refl)
open import Substrate.Algebra.F2     using (𝟘; 𝟙)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Type          using (SymBilinForm-3)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.NonDegenerate using (NonDegenerate)

metric-fully-coupled : SymBilinForm-3
metric-fully-coupled = 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []

metric-fully-coupled-non-degenerate : NonDegenerate metric-fully-coupled
metric-fully-coupled-non-degenerate = refl
