------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2.MultiRouteEquivariance.SingerInv
--
-- singer-Linear's inverse: L-iterate 6 singer-Linear (= singer⁶).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2.MultiRouteEquivariance.SingerInv where

open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Order using (L-iterate)
open import Substrate.Algebra.GL3F2.GaugeGenerators using (singer-Linear)
open import Substrate.Algebra.F2.FanoPlane

singer-inv : Linear 3 3
singer-inv = L-iterate 6 singer-Linear
