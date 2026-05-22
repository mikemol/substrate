------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.MultiRouteEquivariance.Swap01GL
--
-- Sylow-2 generator as a GL3F2 value. swap01-Linear is its own
-- inverse (HasOrder 2); the L-left / L-right witnesses are both
-- HasOrder-swap01.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.MultiRouteEquivariance.Swap01GL where

open import Substrate.Algebra.GL3F2 using (GL3F2; mkGL3F2)
open import Substrate.Algebra.GL3F2.GaugeGenerators
  using (swap01-Linear; HasOrder-swap01)

swap01-GL : GL3F2
swap01-GL = mkGL3F2 swap01-Linear swap01-Linear HasOrder-swap01 HasOrder-swap01
