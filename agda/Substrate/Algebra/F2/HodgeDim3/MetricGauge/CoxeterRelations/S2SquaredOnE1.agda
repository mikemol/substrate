------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE1
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE1 where

open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Eq  using (_≡_; trans; cong)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₂; s₂-on-e₁; s₂-on-e₂)

s₂²-on-e₁ : apply (s₂ ∘L s₂) (basis (suc zero)) ≡ basis (suc zero)
s₂²-on-e₁ = trans (cong (apply s₂) s₂-on-e₁) s₂-on-e₂
