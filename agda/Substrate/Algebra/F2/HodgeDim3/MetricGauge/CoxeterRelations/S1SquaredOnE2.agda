------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE2
--
-- s₁ ∘L s₁ acts as identity on basis e₂.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE2 where

open import Substrate.Foundation.Fin.Literals using (₂)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear.CompL
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₁-on-e₂)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.SquaredOrbitWalk
  using (squared-orbit-walk)
open import Substrate.Foundation.Eq

s₁²-on-e₂ : apply (s₁ ∘L s₁) (basis ₂) ≡ basis ₂
s₁²-on-e₂ = squared-orbit-walk s₁ (basis ₂) s₁-on-e₂ s₁-on-e₂
