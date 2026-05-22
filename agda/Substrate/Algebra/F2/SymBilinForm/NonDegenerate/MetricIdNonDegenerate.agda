------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.NonDegenerate.MetricIdNonDegenerate
--
-- The kernel-free witness for metric-id at any n:
--
--   metric-id-non-degenerate-generic : NonDegenerate (metric-id {n})
--
-- If v is in the radical of metric-id (= pairs to 𝟘 with every w),
-- specialise to w = basis i to extract `lookup v i ≡ 𝟘` for each i.
-- Conclude v ≡ 𝟎ⱽ by ≡-from-lookup.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.NonDegenerate.MetricIdNonDegenerate where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Eq using (_≡_; sym; trans)

open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ; basis; ≡-from-lookup; lookup-𝟎)
open import Substrate.Algebra.F2.SymBilinForm.MetricId using (metric-id)
open import Substrate.Algebra.F2.SymBilinForm.NonDegenerate using (NonDegenerate)
open import Substrate.Algebra.F2.SymBilinForm.NonDegenerate.PairMetricIdWithBasis
  using (pair-metric-id-with-basis-generic)

open import Substrate.Category.Equalizer using (equal)

metric-id-non-degenerate-generic :
  ∀ {n} → NonDegenerate (metric-id {n})
metric-id-non-degenerate-generic {n} v in-radical =
  ≡-from-lookup v 𝟎ⱽ goal
  where
    goal : (i : Fin n) → lookup v i ≡ lookup (𝟎ⱽ {n}) i
    goal i =
      trans (sym (pair-metric-id-with-basis-generic v i))
            (trans (equal (in-radical (basis i)))
                   (sym (lookup-𝟎 i)))
