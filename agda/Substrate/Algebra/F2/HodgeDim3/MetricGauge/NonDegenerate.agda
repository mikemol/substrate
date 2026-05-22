------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.NonDegenerate
--
-- The NonDegenerate predicate: det-sym3 m ≡ 𝟙. The "inference rule"
-- presentation of the 28-element non-degenerate metric space.
-- Decidability inherits from F₂'s decidable equality.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.NonDegenerate where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.F2    using (𝟙)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Type using (SymBilinForm-3)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Det  using (det-sym3)

NonDegenerate : SymBilinForm-3 → Set
NonDegenerate m = det-sym3 m ≡ 𝟙
