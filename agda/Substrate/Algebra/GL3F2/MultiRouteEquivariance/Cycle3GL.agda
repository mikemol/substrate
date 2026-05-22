------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.MultiRouteEquivariance.Cycle3GL
--
-- Sylow-3 generator as a GL3F2 value. Left/right inverse witnesses
-- both close by HasOrder-cycle3 (since cycle3² is the inverse).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.MultiRouteEquivariance.Cycle3GL where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (apply)
open import Substrate.Algebra.GL3F2 using (GL3F2; mkGL3F2)
open import Substrate.Algebra.GL3F2.GaugeGenerators
  using (cycle3-Linear; HasOrder-cycle3)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.Cycle3Inv using (cycle3-inv)

cycle3-GL : GL3F2
cycle3-GL = mkGL3F2 cycle3-Linear cycle3-inv left-witness right-witness
  where
    left-witness :
      (v : Vector 3) →
      apply cycle3-inv (apply cycle3-Linear v) ≡ v
    left-witness v = HasOrder-cycle3 v

    right-witness :
      (v : Vector 3) →
      apply cycle3-Linear (apply cycle3-inv v) ≡ v
    right-witness v = HasOrder-cycle3 v
