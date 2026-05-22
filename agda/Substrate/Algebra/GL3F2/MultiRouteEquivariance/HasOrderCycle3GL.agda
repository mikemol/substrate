------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.MultiRouteEquivariance.HasOrderCycle3GL
--
-- cycle3-GL has order 3 in GL(3, F₂).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.MultiRouteEquivariance.HasOrderCycle3GL where

open import Substrate.Algebra.GL3F2 using (HasOrder-GL)
open import Substrate.Algebra.GL3F2.GaugeGenerators using (HasOrder-cycle3)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.Cycle3GL using (cycle3-GL)

HasOrder-GL-cycle3 : HasOrder-GL cycle3-GL 3
HasOrder-GL-cycle3 = HasOrder-cycle3
