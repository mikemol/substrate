------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.HasOrderS2
--
-- s₂ is an involution: HasOrder s₂-endo 2.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.HasOrderS2 where

open import Substrate.Category.Coalgebra.FiniteOrder using (HasOrder)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2Endo using (s₂-endo)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2SquaredOnV using (s₂²-on-v)

HasOrder-s₂ : HasOrder s₂-endo 2
HasOrder-s₂ = s₂²-on-v
