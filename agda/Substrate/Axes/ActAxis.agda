------------------------------------------------------------------------
-- Substrate.Axes.ActAxis
--
-- The V₄ action on axes, transported through the bijection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.ActAxis where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Groups.V4.Operations using (_·_)
open import Substrate.Axes.Axis using (Axis)
open import Substrate.Axes.VOfAxis using (v-of-axis)
open import Substrate.Axes.AxisOfV using (axis-of-v)

act-axis : V₄ → Axis → Axis
act-axis v x = axis-of-v (v · v-of-axis x)
