------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE1
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE1 where

open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear.CompL
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₂; s₂-on-e₁; s₂-on-e₂)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.SquaredOrbitWalk
  using (squared-orbit-walk)
open import Substrate.Foundation.Eq

s₂²-on-e₁ : apply (s₂ ∘L s₂) (basis ₁) ≡ basis ₁
s₂²-on-e₁ = squared-orbit-walk s₂ (basis ₁) s₂-on-e₁ s₂-on-e₂
