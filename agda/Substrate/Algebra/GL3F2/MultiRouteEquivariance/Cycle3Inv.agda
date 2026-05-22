------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.MultiRouteEquivariance.Cycle3Inv
--
-- cycle3-Linear's inverse: cycle3 ∘L cycle3 (= cycle3²).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.MultiRouteEquivariance.Cycle3Inv where

open import Substrate.Algebra.F2.Linear using (Linear; _∘L_)
open import Substrate.Algebra.GL3F2.GaugeGenerators using (cycle3-Linear)

cycle3-inv : Linear 3 3
cycle3-inv = cycle3-Linear ∘L cycle3-Linear
