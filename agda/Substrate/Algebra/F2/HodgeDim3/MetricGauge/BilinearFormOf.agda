------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.BilinearFormOf
--
-- bilinear-form-of M v w = v^T M w over F₂. For symmetric
-- M = (a, b, c, d, e, f) and v = (v₀, v₁, v₂), w = (w₀, w₁, w₂):
--
--   v₀ · (a·w₀ +F d·w₁ +F e·w₂)
-- +F v₁ · (d·w₀ +F b·w₁ +F f·w₂)
-- +F v₂ · (e·w₀ +F f·w₁ +F c·w₂).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.BilinearFormOf where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Type using (SymBilinForm-3)

bilinear-form-of : SymBilinForm-3 → Vector 3 → Vector 3 → F₂
bilinear-form-of (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ [])
                 (v₀ ∷ v₁ ∷ v₂ ∷ [])
                 (w₀ ∷ w₁ ∷ w₂ ∷ []) =
  v₀ · (a · w₀ +F d · w₁ +F e · w₂) +F
  v₁ · (d · w₀ +F b · w₁ +F f · w₂) +F
  v₂ · (e · w₀ +F f · w₁ +F c · w₂)
