------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.HasOrderS1
--
-- s₁ is an involution: HasOrder s₁-endo 2.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.HasOrderS1 where

open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1Endo using (s₁-endo)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1SquaredOnV using (s₁²-on-v)

HasOrder-s₁ : HasOrder s₁-endo 2
HasOrder-s₁ = s₁²-on-v
