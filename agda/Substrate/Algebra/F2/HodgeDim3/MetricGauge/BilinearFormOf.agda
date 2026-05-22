------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.BilinearFormOf
--
-- bilinear-form-of M v w = v^T M w over F₂. For symmetric
-- M = (a, b, c, d, e, f) and v = (v₀, v₁, v₂), w = (w₀, w₁, w₂):
--
--   v₀ · (a·w₀ + d·w₁ + e·w₂)
-- + v₁ · (d·w₀ + b·w₁ + f·w₂)
-- + v₂ · (e·w₀ + f·w₁ + c·w₂).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.BilinearFormOf where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Algebra.F2     using (F₂; _·_; _+_)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Type using (SymBilinForm-3)

bilinear-form-of : SymBilinForm-3 → Vector 3 → Vector 3 → F₂
bilinear-form-of (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ [])
                 (v₀ ∷ v₁ ∷ v₂ ∷ [])
                 (w₀ ∷ w₁ ∷ w₂ ∷ []) =
  v₀ · (a · w₀ + d · w₁ + e · w₂) +
  v₁ · (d · w₀ + b · w₁ + f · w₂) +
  v₂ · (e · w₀ + f · w₁ + c · w₂)
