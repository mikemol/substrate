------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE0
--
-- s₁ ∘L s₁ acts as identity on basis e₀ (s₁²-on-e₀).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE0 where

open import Substrate.Foundation.Fin using (zero)
open import Substrate.Foundation.Eq  using (_≡_; trans; cong)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₁-on-e₀; s₁-on-e₁)

s₁²-on-e₀ : apply (s₁ ∘L s₁) (basis zero) ≡ basis zero
s₁²-on-e₀ = trans (cong (apply s₁) s₁-on-e₀) s₁-on-e₁
