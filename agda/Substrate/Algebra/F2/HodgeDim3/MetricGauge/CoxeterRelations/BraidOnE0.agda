------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE0
--
-- Braid s₁ ∘L s₂ ∘L s₁ ≡ s₂ ∘L s₁ ∘L s₂ on basis e₀ (both map e₀ to e₂).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE0 where

open import Substrate.Foundation.Fin using (zero)
open import Substrate.Foundation.Eq  using (_≡_; sym; trans; cong)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₂; s₁-on-e₀; s₁-on-e₂; s₂-on-e₀; s₂-on-e₁)

braid-on-e₀ :
  apply (s₁ ∘L s₂ ∘L s₁) (basis zero)
    ≡ apply (s₂ ∘L s₁ ∘L s₂) (basis zero)
braid-on-e₀ =
  trans (cong (apply s₁) (cong (apply s₂) s₁-on-e₀))
  (trans (cong (apply s₁) s₂-on-e₁)
  (trans s₁-on-e₂
  (trans (sym s₂-on-e₁)
  (trans (cong (apply s₂) (sym s₁-on-e₀))
         (cong (apply s₂) (cong (apply s₁) (sym s₂-on-e₀)))))))
