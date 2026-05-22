------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.MetricIdSym
--
-- metric-id-Sym : metric-id packaged as a SymBilinForm n.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.MetricIdSym where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.F2.SymBilinForm.Type using (SymBilinForm)
open import Substrate.Algebra.F2.SymBilinForm.MetricId using (metric-id)
open import Substrate.Algebra.F2.SymBilinForm.MetricIdSymmetric using (is-symmetric-metric-id)

metric-id-Sym : ∀ {n} → SymBilinForm n
metric-id-Sym = metric-id , is-symmetric-metric-id
