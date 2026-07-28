------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2CubedOnE0
--
-- (s₁ ∘L s₂)³ = id on basis e₀.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2CubedOnE0 where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; id-L; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₂; s₁-on-e₀; s₁-on-e₁; s₁-on-e₂; s₂-on-e₀; s₂-on-e₁; s₂-on-e₂)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.CubedOrbitWalk
  using (cubed-orbit-walk)

s₁∘s₂-cubed-on-e₀ :
  apply ((s₁ ∘L s₂) ∘L (s₁ ∘L s₂) ∘L (s₁ ∘L s₂)) (basis zero)
    ≡ apply id-L (basis zero)
s₁∘s₂-cubed-on-e₀ =
  cubed-orbit-walk s₁ s₂ (basis zero) s₂-on-e₀ s₁-on-e₀ s₂-on-e₁ s₁-on-e₂ s₂-on-e₂ s₁-on-e₁
