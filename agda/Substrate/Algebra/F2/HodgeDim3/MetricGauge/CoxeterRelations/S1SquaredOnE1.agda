------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE1
--
-- s₁ ∘L s₁ acts as identity on basis e₁.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE1 where

open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Eq  using (_≡_; trans; cong)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₁-on-e₀; s₁-on-e₁)

s₁²-on-e₁ : apply (s₁ ∘L s₁) (basis (suc zero)) ≡ basis (suc zero)
s₁²-on-e₁ = trans (cong (apply s₁) s₁-on-e₁) s₁-on-e₀
