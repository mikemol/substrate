------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE0
--
-- Braid s₁ ∘L s₂ ∘L s₁ ≡ s₂ ∘L s₁ ∘L s₂ on basis e₀ (both map e₀ to e₂).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE0 where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₂; s₁-on-e₀; s₁-on-e₂; s₂-on-e₀; s₂-on-e₁)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidWalk
  using (braid-walk)

braid-on-e₀ :
  apply (s₁ ∘L s₂ ∘L s₁) (basis zero)
    ≡ apply (s₂ ∘L s₁ ∘L s₂) (basis zero)
braid-on-e₀ = braid-walk s₁ s₂ (basis zero)
  s₁-on-e₀ s₂-on-e₁ s₁-on-e₂ s₂-on-e₁ s₁-on-e₀ s₂-on-e₀
