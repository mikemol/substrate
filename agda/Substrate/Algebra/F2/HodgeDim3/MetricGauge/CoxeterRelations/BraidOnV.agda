------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnV
--
-- Pointwise s₁ ∘L s₂ ∘L s₁ ≡ s₂ ∘L s₁ ∘L s₂ via linear-extensionality
-- + fin-cover (named-cover discipline).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnV where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Fin.Cover using (fin-cover)
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (apply; _∘L_)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser using (s₁; s₂)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE0 using (braid-on-e₀)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE1 using (braid-on-e₁)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE2 using (braid-on-e₂)

braid-on-v :
  (v : Vector 3) →
  apply (s₁ ∘L s₂ ∘L s₁) v ≡ apply (s₂ ∘L s₁ ∘L s₂) v
braid-on-v = linear-extensionality (s₁ ∘L s₂ ∘L s₁) (s₂ ∘L s₁ ∘L s₂)
  (fin-cover _ (braid-on-e₀ , braid-on-e₁ , braid-on-e₂))
