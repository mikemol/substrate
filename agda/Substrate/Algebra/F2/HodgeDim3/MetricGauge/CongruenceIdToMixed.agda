------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CongruenceIdToMixed
--
-- ONE concrete transitivity witness for the GL(3, F₂) congruence
-- orbit: congruence-act T-id-to-mixed metric-id ≡ metric-mixed.
--
-- Closes by ≡-from-lookup at the Vector 6 level; each of the 6
-- entries reduces via the T-on-eᵢ rewrites then F₂ arithmetic.
--
-- Full structural transitivity (every non-degenerate form reduces
-- to metric-id via some T) is the coalgebraic-unfolding follow-on
-- (M-11.metric-gauge.orbit-characterisation).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CongruenceIdToMixed where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂; ₃; ₄; ₅)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq  using (_≡_; trans; cong)
open import Substrate.Algebra.F2 using (𝟘; 𝟙)
open import Substrate.Algebra.F2.Vector using (basis; ≡-from-lookup)
open import Substrate.Algebra.F2.Linear using (apply)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.BilinearFormOf
  using (bilinear-form-of)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CongruenceAct
  using (congruence-act)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricId    using (metric-id)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.MetricMixed using (metric-mixed)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.TIdToMixed
  using (T-id-to-mixed; T-on-e₀; T-on-e₁; T-on-e₂)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.BilinearFormSteps
  using (diag-bf-step; off-diag-bf-step)

congruence-id-to-mixed :
  congruence-act T-id-to-mixed metric-id ≡ metric-mixed
congruence-id-to-mixed = ≡-from-lookup _ _ goal
  where
    goal : (i : Fin 6) →
           lookup (congruence-act T-id-to-mixed metric-id) i ≡
           lookup metric-mixed i
    goal zero       = diag-bf-step metric-id T-id-to-mixed (basis zero) T-on-e₀
    goal ₁          = diag-bf-step metric-id T-id-to-mixed (basis ₁)    T-on-e₁
    goal ₂          = diag-bf-step metric-id T-id-to-mixed (basis ₂)    T-on-e₂
    goal ₃          = off-diag-bf-step metric-id T-id-to-mixed (basis zero) (basis ₁) (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []) (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []) T-on-e₀ T-on-e₁
    goal ₄          = off-diag-bf-step metric-id T-id-to-mixed (basis zero) (basis ₂) (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []) (𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []) T-on-e₀ T-on-e₂
    goal ₅          = off-diag-bf-step metric-id T-id-to-mixed (basis ₁)    (basis ₂) (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []) (𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []) T-on-e₁ T-on-e₂
