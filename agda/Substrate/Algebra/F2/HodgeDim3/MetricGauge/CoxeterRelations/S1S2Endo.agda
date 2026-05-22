------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2Endo
--
-- s₁ ∘L s₂ as an endomap (3-cycle in S₃).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.S1S2Endo where

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (apply; _∘L_)
open import Substrate.Category.Coalgebra using (Endomap)
open import Substrate.Algebra.F2.HodgeDim3.MetricGauge.Stabiliser using (s₁; s₂)

s₁∘s₂-endo : Endomap (Vector 3)
s₁∘s₂-endo = apply (s₁ ∘L s₂)
