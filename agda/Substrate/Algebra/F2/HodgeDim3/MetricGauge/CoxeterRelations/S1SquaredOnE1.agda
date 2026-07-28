------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE1
--
-- s₁ ∘L s₁ acts as identity on basis e₁.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE1 where

open import Substrate.Foundation.Fin.Literals using (₁)
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₁-on-e₀; s₁-on-e₁)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.SquaredOrbitWalk
  using (squared-orbit-walk)

s₁²-on-e₁ : apply (s₁ ∘L s₁) (basis ₁) ≡ basis ₁
s₁²-on-e₁ = squared-orbit-walk s₁ (basis ₁) s₁-on-e₁ s₁-on-e₀
