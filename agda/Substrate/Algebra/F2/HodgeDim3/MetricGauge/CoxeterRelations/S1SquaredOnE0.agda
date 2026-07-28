------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE0
--
-- s₁ ∘L s₁ acts as identity on basis e₀ (s₁²-on-e₀).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE0 where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₁-on-e₀; s₁-on-e₁)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.SquaredOrbitWalk
  using (squared-orbit-walk)

s₁²-on-e₀ : apply (s₁ ∘L s₁) (basis zero) ≡ basis zero
s₁²-on-e₀ = squared-orbit-walk s₁ (basis zero) s₁-on-e₀ s₁-on-e₁
