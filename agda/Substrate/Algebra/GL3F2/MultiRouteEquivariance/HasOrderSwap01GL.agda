------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.MultiRouteEquivariance.HasOrderSwap01GL
--
-- swap01-GL has order 2 in GL(3, F₂).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.MultiRouteEquivariance.HasOrderSwap01GL where

open import Substrate.Algebra.GL3F2 using (HasOrder-GL)
open import Substrate.Algebra.GL3F2.GaugeGenerators using (HasOrder-swap01)
open import Substrate.Algebra.GL3F2.MultiRouteEquivariance.Swap01GL using (swap01-GL)

HasOrder-GL-swap01 : HasOrder-GL swap01-GL 2
HasOrder-GL-swap01 = HasOrder-swap01
