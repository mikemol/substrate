------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.NonDegenerate.PairMetricIdWithBasis
--
-- The universal extraction lemma:
--
--   bilinear-form-of metric-id v (basis i) ≡ lookup v i
--
-- — metric-id IS the Kronecker delta as a bilinear form; pairing
-- against the i-th basis vector extracts the i-th component.
--
-- Path:
--   bf metric-id v (basis i)
--     = sum-F₂ (λ k → lookup v k · sum-F₂ (λ j → metric-id k j · lookup (basis i) j))
--     = sum-F₂ (λ k → lookup v k · lookup (basis i) k)       [inner δ-collapse]
--     = sum-F₂ (λ k → lookup v k · metric-id i k)            [basis-row-eq]
--     = sum-F₂ (λ k → metric-id i k · lookup v k)            [·-comm]
--     = lookup v i                                            [outer δ-collapse]
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.NonDegenerate.PairMetricIdWithBasis where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Eq using (_≡_; trans; cong)

open import Substrate.Algebra.F2 using (·-comm)
open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Vector.Universal using (sum-F₂; sum-F₂-cong)
open import Substrate.Algebra.F2.SymBilinForm.MetricId using (metric-id)
open import Substrate.Algebra.F2.SymBilinForm.BilinearFormOf using (bilinear-form-of)
open import Substrate.Algebra.F2.SymBilinForm.HodgeRecast using (metric-id-collapse)
open import Substrate.Algebra.F2.SymBilinForm.NonDegenerate.BasisRowEqMetricId
  using (basis-row-eq-metric-id)

pair-metric-id-with-basis-generic :
  ∀ {n} (v : Vector n) (i : Fin n) →
  bilinear-form-of metric-id v (basis i) ≡ lookup v i
pair-metric-id-with-basis-generic {n} v i =
  trans
    -- Inner δ-collapse on each k.
    (sum-F₂-cong {n} (λ k →
      cong (lookup v k ·_) (metric-id-collapse k (basis i))))
  (trans
    -- Replace lookup (basis i) k with metric-id i k.
    (sum-F₂-cong {n} (λ k →
      cong (lookup v k ·_) (basis-row-eq-metric-id i k)))
  (trans
    -- Swap factor order so metric-id is on the left.
    (sum-F₂-cong {n} (λ k →
      ·-comm (lookup v k) (metric-id i k)))
    -- Outer δ-collapse.
    (metric-id-collapse i v)))
  where open import Substrate.Algebra.F2 using (_·_)
