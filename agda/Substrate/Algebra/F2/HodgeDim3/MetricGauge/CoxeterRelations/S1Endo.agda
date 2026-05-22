------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1Endo
--
-- s₁ as an endomap of Vector 3 (interface for HasOrder retrofit).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1Endo where

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (apply)
open import Substrate.Category.Coalgebra using (Endomap)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser using (s₁)

s₁-endo : Endomap (Vector 3)
s₁-endo = apply s₁
