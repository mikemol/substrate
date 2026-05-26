------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE2
--
-- Braid on basis e₂ (both map e₂ to e₀).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE2 where

open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Fin.Literals using (₂)
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₂; s₁-on-e₁; s₁-on-e₂; s₂-on-e₀; s₂-on-e₂)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidWalk
  using (braid-walk)

braid-on-e₂ :
  apply (s₁ ∘L s₂ ∘L s₁) (basis ₂)
    ≡ apply (s₂ ∘L s₁ ∘L s₂) (basis ₂)
braid-on-e₂ = braid-walk s₁ s₂ (basis ₂)
  s₁-on-e₂ s₂-on-e₂ s₁-on-e₁ s₂-on-e₀ s₁-on-e₁ s₂-on-e₂
