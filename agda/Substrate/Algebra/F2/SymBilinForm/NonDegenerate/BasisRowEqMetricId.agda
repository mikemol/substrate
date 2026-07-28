------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.NonDegenerate.BasisRowEqMetricId
--
-- The basis vector's lookup at j is exactly metric-id i j.
--
-- Both `lookup (basis i) j` and `metric-id i j` are 𝟙 iff i=j, else 𝟘.
-- Proof by simultaneous induction on (i, j).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.NonDegenerate.BasisRowEqMetricId where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.F2.Vector using (basis; lookup-𝟎)
open import Substrate.Algebra.F2.SymBilinForm.MetricId using (metric-id)
open import Substrate.Foundation.Vec using (lookup)

basis-row-eq-metric-id :
  ∀ {n} (i j : Fin n) → lookup (basis i) j ≡ metric-id i j
basis-row-eq-metric-id zero    zero    = refl
basis-row-eq-metric-id zero    (suc j) = lookup-𝟎 j
basis-row-eq-metric-id (suc i) zero    = refl
basis-row-eq-metric-id (suc i) (suc j) = basis-row-eq-metric-id i j
