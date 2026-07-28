------------------------------------------------------------------------
-- Substrate.Axes.AxisOfV
--
-- V₄ → Axis.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.AxisOfV where

open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ)
open import Substrate.Axes.Axis using (Axis; D; C; S; W)

axis-of-v : V₄ → Axis
axis-of-v e = D
axis-of-v α = C
axis-of-v β = S
axis-of-v γ = W
