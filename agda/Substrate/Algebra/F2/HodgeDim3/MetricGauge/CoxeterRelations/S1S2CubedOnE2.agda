------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2CubedOnE2
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2CubedOnE2 where

open import Substrate.Foundation.Fin.Literals using (₂)
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; id-L; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₂; s₁-on-e₀; s₁-on-e₁; s₁-on-e₂; s₂-on-e₀; s₂-on-e₁; s₂-on-e₂)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.CubedOrbitWalk
  using (cubed-orbit-walk)

s₁∘s₂-cubed-on-e₂ :
  apply ((s₁ ∘L s₂) ∘L (s₁ ∘L s₂) ∘L (s₁ ∘L s₂)) (basis ₂)
    ≡ apply id-L (basis ₂)
s₁∘s₂-cubed-on-e₂ =
  cubed-orbit-walk s₁ s₂ (basis ₂) s₂-on-e₂ s₁-on-e₁ s₂-on-e₀ s₁-on-e₀ s₂-on-e₁ s₁-on-e₂
