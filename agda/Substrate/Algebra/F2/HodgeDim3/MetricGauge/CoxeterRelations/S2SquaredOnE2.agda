------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE2
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE2 where

open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₂; s₂-on-e₁; s₂-on-e₂)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.SquaredOrbitWalk
  using (squared-orbit-walk)

s₂²-on-e₂ : apply (s₂ ∘L s₂) (basis ₂) ≡ basis ₂
s₂²-on-e₂ = squared-orbit-walk s₂ (basis ₂) s₂-on-e₂ s₂-on-e₁
