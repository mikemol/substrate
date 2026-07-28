------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE1
--
-- Braid on basis e₁ (both map e₁ to e₁).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE1 where

open import Substrate.Foundation.Fin.Literals using (₁)
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₂; s₁-on-e₀; s₁-on-e₁; s₁-on-e₂; s₂-on-e₀; s₂-on-e₁; s₂-on-e₂)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidWalk
  using (braid-walk)

braid-on-e₁ :
  apply (s₁ ∘L s₂ ∘L s₁) (basis ₁)
    ≡ apply (s₂ ∘L s₁ ∘L s₂) (basis ₁)
braid-on-e₁ = braid-walk s₁ s₂ (basis ₁)
  s₁-on-e₁ s₂-on-e₀ s₁-on-e₀ s₂-on-e₂ s₁-on-e₂ s₂-on-e₁
