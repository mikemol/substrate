------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2CubedOnE1
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2CubedOnE1 where

open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂)
open import Substrate.Foundation.Eq  using (_≡_; trans; cong)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; id-L; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₂; s₁-on-e₀; s₁-on-e₁; s₁-on-e₂; s₂-on-e₀; s₂-on-e₁; s₂-on-e₂)

s₁∘s₂-cubed-on-e₁ :
  apply ((s₁ ∘L s₂) ∘L (s₁ ∘L s₂) ∘L (s₁ ∘L s₂)) (basis ₁)
    ≡ apply id-L (basis ₁)
s₁∘s₂-cubed-on-e₁ =
  trans (cong (apply (s₁ ∘L s₂)) (cong (apply (s₁ ∘L s₂))
              (cong (apply s₁) s₂-on-e₁)))
  (trans (cong (apply (s₁ ∘L s₂)) (cong (apply (s₁ ∘L s₂)) s₁-on-e₂))
  (trans (cong (apply (s₁ ∘L s₂)) (cong (apply s₁) s₂-on-e₂))
  (trans (cong (apply (s₁ ∘L s₂)) s₁-on-e₁)
  (trans (cong (apply s₁) s₂-on-e₀)
         s₁-on-e₀))))
