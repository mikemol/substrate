------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnV
--
-- Pointwise s₂ ∘L s₂ agrees with id-L on every v, via
-- linear-extensionality + fin-cover (named-cover discipline).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnV where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Fin.Cover using (fin-cover)
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (apply; id-L; _∘L_)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser using (s₂)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE0 using (s₂²-on-e₀)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE1 using (s₂²-on-e₁)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE2 using (s₂²-on-e₂)

s₂²-on-v : (v : Vector 3) → apply (s₂ ∘L s₂) v ≡ apply id-L v
s₂²-on-v = linear-extensionality (s₂ ∘L s₂) id-L
  (fin-cover _ (s₂²-on-e₀ , s₂²-on-e₁ , s₂²-on-e₂))
