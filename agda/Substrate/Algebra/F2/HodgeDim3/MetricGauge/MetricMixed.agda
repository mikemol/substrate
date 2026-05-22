------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricMixed
--
-- Exemplar mixed (one-coupling) metric. Matrix
--   [[0, 1, 0], [1, 0, 0], [0, 0, 1]]
-- with det = 1. Structural exemplar of the mixed shape-class.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricMixed where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq  using (refl)
open import Substrate.Algebra.F2     using (𝟘; 𝟙)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Type          using (SymBilinForm-3)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.NonDegenerate using (NonDegenerate)

metric-mixed : SymBilinForm-3
metric-mixed = 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ []

metric-mixed-non-degenerate : NonDegenerate metric-mixed
metric-mixed-non-degenerate = refl
