------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CongruenceAct
--
-- congruence-act T M: the standard T^T M T congruence action expressed
-- via the bilinear-form interpretation. Produces the new symmetric
-- form whose (i, j) entry is bilinear-form-of M (T e_i) (T e_j).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CongruenceAct where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Type           using (SymBilinForm-3)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.BilinearFormOf using (bilinear-form-of)

congruence-act : Linear 3 3 → SymBilinForm-3 → SymBilinForm-3
congruence-act T M =
  bilinear-form-of M Te₀ Te₀ ∷
  bilinear-form-of M Te₁ Te₁ ∷
  bilinear-form-of M Te₂ Te₂ ∷
  bilinear-form-of M Te₀ Te₁ ∷
  bilinear-form-of M Te₀ Te₂ ∷
  bilinear-form-of M Te₁ Te₂ ∷ []
  where
    Te₀ = apply T (basis zero)
    Te₁ = apply T (basis ₁)
    Te₂ = apply T (basis ₂)
