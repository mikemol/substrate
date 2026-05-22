------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnV
--
-- Pointwise s₁ ∘L s₁ agrees with id-L on every v via
-- linear-extensionality applied to the per-basis lemmas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnV where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Linear using (apply; id-L; _∘L_)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser using (s₁)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE0 using (s₁²-on-e₀)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE1 using (s₁²-on-e₁)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnE2 using (s₁²-on-e₂)

s₁²-on-v : (v : Vector 3) → apply (s₁ ∘L s₁) v ≡ apply id-L v
s₁²-on-v = linear-extensionality (s₁ ∘L s₁) id-L agree-on-basis
  where
    agree-on-basis : (i : Fin 3) →
                     apply (s₁ ∘L s₁) (basis i) ≡ apply id-L (basis i)
    agree-on-basis zero             = s₁²-on-e₀
    agree-on-basis (suc zero)       = s₁²-on-e₁
    agree-on-basis (suc (suc zero)) = s₁²-on-e₂
