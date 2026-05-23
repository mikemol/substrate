------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.TIdToMixed
--
-- Concrete invertible T : Linear 3 3 routing metric-id to
-- metric-mixed under the congruence action. Columns
-- (1,1,0), (1,0,1), (1,1,1); det = 𝟙. Provides T-id-to-mixed-images,
-- T-id-to-mixed, and per-basis evaluation lemmas T-on-e₀/₁/₂ that
-- rewrite `apply T (basis i)` to the explicit image vectors.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.TIdToMixed where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq  using (_≡_)
open import Substrate.Algebra.F2 using (𝟘; 𝟙)
open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)

T-id-to-mixed-images : Fin 3 → Vector 3
T-id-to-mixed-images zero          = 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ []
T-id-to-mixed-images (suc zero)    = 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ []
T-id-to-mixed-images ₂ = 𝟙 ∷ 𝟙 ∷ 𝟙 ∷ []

T-id-to-mixed : Linear 3 3
T-id-to-mixed = linear-from-images T-id-to-mixed-images

T-on-e₀ : apply T-id-to-mixed (basis zero) ≡ (𝟙 ∷ 𝟙 ∷ 𝟘 ∷ [])
T-on-e₀ = apply-linear-from-images-basis T-id-to-mixed-images zero

T-on-e₁ : apply T-id-to-mixed (basis (suc zero)) ≡ (𝟙 ∷ 𝟘 ∷ 𝟙 ∷ [])
T-on-e₁ = apply-linear-from-images-basis T-id-to-mixed-images (suc zero)

T-on-e₂ : apply T-id-to-mixed (basis ₂) ≡ (𝟙 ∷ 𝟙 ∷ 𝟙 ∷ [])
T-on-e₂ = apply-linear-from-images-basis T-id-to-mixed-images ₂
