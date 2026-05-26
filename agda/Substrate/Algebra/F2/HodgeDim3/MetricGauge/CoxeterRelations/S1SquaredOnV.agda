------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnV
--
-- Pointwise s₁ ∘L s₁ agrees with id-L on every v via
-- linear-extensionality applied to the per-basis lemmas, with the
-- case-split on Fin 3 supplied by fin-cover (named-cover discipline
-- replacing the hand-written where-clause case match).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnV where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Fin.Cover using (fin-cover)
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (apply; id-L; _∘L_)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser using (s₁)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE0 using (s₁²-on-e₀)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE1 using (s₁²-on-e₁)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE2 using (s₁²-on-e₂)

s₁²-on-v : (v : Vector 3) → apply (s₁ ∘L s₁) v ≡ apply id-L v
s₁²-on-v = linear-extensionality (s₁ ∘L s₁) id-L
  (fin-cover _ (s₁²-on-e₀ , s₁²-on-e₁ , s₁²-on-e₂))
