------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE0
--
-- s₂ ∘L s₂ acts as identity on basis e₀.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE0 where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear.CompL
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₂; s₂-on-e₀)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.SquaredOrbitWalk
  using (squared-orbit-walk)
open import Substrate.Foundation.Eq

s₂²-on-e₀ : apply (s₂ ∘L s₂) (basis zero) ≡ basis zero
s₂²-on-e₀ = squared-orbit-walk s₂ (basis zero) s₂-on-e₀ s₂-on-e₀
