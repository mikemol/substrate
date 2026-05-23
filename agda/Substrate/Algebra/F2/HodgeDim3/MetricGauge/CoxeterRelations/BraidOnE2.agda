------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE2
--
-- Braid on basis e₂ (both map e₂ to e₀).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.BraidOnE2 where

open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂)
open import Substrate.Foundation.Eq  using (_≡_; sym; trans; cong)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Linear using (apply; _∘L_)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser
  using (s₁; s₂; s₁-on-e₁; s₁-on-e₂; s₂-on-e₀; s₂-on-e₂)

braid-on-e₂ :
  apply (s₁ ∘L s₂ ∘L s₁) (basis ₂)
    ≡ apply (s₂ ∘L s₁ ∘L s₂) (basis ₂)
braid-on-e₂ =
  trans (cong (apply s₁) (cong (apply s₂) s₁-on-e₂))
  (trans (cong (apply s₁) s₂-on-e₂)
  (trans s₁-on-e₁
  (trans (sym s₂-on-e₀)
  (trans (cong (apply s₂) (sym s₁-on-e₁))
         (cong (apply s₂) (cong (apply s₁) (sym s₂-on-e₂)))))))
