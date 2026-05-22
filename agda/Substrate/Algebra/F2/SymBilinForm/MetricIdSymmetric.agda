------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.MetricIdSymmetric
--
-- is-symmetric-metric-id : metric-id is symmetric. Recursive proof
-- mirroring metric-id's definition; no decidable equality needed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.MetricIdSymmetric where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (refl)
open import Substrate.Algebra.F2.SymBilinForm.IsSymmetric using (IsSymmetric)
open import Substrate.Algebra.F2.SymBilinForm.MetricId using (metric-id)

is-symmetric-metric-id : ∀ {n} → IsSymmetric (metric-id {n})
is-symmetric-metric-id zero    zero    = refl
is-symmetric-metric-id zero    (suc _) = refl
is-symmetric-metric-id (suc _) zero    = refl
is-symmetric-metric-id (suc i) (suc j) = is-symmetric-metric-id i j
