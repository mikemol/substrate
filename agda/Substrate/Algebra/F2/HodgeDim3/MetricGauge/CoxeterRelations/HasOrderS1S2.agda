------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.HasOrderS1S2
--
-- (s₁s₂)³ = e: HasOrder s₁∘s₂-endo 3, via linear-extensionality on
-- the three per-basis cubed lemmas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.HasOrderS1S2 where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; id-L; _∘L_)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser using (s₁; s₂)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2Endo using (s₁∘s₂-endo)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2CubedOnE0 using (s₁∘s₂-cubed-on-e₀)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2CubedOnE1 using (s₁∘s₂-cubed-on-e₁)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2CubedOnE2 using (s₁∘s₂-cubed-on-e₂)

HasOrder-s₁∘s₂ : HasOrder s₁∘s₂-endo 3
HasOrder-s₁∘s₂ v =
  linear-extensionality
    ((s₁ ∘L s₂) ∘L (s₁ ∘L s₂) ∘L (s₁ ∘L s₂))
    id-L
    agree-on-basis
    v
  where
    agree-on-basis : (i : Fin 3) →
                     apply ((s₁ ∘L s₂) ∘L (s₁ ∘L s₂) ∘L (s₁ ∘L s₂)) (basis i)
                       ≡ apply id-L (basis i)
    agree-on-basis zero             = s₁∘s₂-cubed-on-e₀
    agree-on-basis (suc zero)       = s₁∘s₂-cubed-on-e₁
    agree-on-basis (suc (suc zero)) = s₁∘s₂-cubed-on-e₂
