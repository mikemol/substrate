------------------------------------------------------------------------
-- Substrate.Axes.Axis.Compose
--
-- The induced binary operation on axes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.Axis.Compose where

open import Substrate.Axes.Axis using (Axis)
open import Substrate.Axes.VOfAxis using (v-of-axis)
open import Substrate.Axes.ActAxis using (act-axis)

_∙ᴬ_ : Axis → Axis → Axis
x ∙ᴬ y = act-axis (v-of-axis x) y
