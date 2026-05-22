------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricId
--
-- The diagonal identity metric: a=b=c=1, d=e=f=0. Structural
-- exemplar of the orthogonal shape-class under the S₃ axis-permutation
-- subgroup of GL(3, F₂).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricId where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq  using (refl)
open import Substrate.Algebra.F2     using (𝟘; 𝟙)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Type          using (SymBilinForm-3)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.NonDegenerate using (NonDegenerate)

metric-id : SymBilinForm-3
metric-id = 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []

metric-id-non-degenerate : NonDegenerate metric-id
metric-id-non-degenerate = refl
