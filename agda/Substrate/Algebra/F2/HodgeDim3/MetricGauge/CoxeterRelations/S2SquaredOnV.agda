------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnV
--
-- Pointwise s₂ ∘L s₂ agrees with id-L on every v.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnV where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂)
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Linear using (apply; id-L; _∘L_)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser using (s₂)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE0 using (s₂²-on-e₀)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE1 using (s₂²-on-e₁)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnE2 using (s₂²-on-e₂)

s₂²-on-v : (v : Vector 3) → apply (s₂ ∘L s₂) v ≡ apply id-L v
s₂²-on-v = linear-extensionality (s₂ ∘L s₂) id-L agree-on-basis
  where
    agree-on-basis : (i : Fin 3) →
                     apply (s₂ ∘L s₂) (basis i) ≡ apply id-L (basis i)
    agree-on-basis zero             = s₂²-on-e₀
    agree-on-basis ₁       = s₂²-on-e₁
    agree-on-basis ₂ = s₂²-on-e₂
