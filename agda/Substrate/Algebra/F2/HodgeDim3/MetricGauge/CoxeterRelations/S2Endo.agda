------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2Endo
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S2Endo where

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (apply)
open import Substrate.Category.Coalgebra using (Endomap)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser using (s₂)

s₂-endo : Endomap (Vector 3)
s₂-endo = apply s₂
