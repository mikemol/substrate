------------------------------------------------------------------------
-- Substrate.Axes.VOfAxis
--
-- Axis → V₄.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.VOfAxis where

open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Axes.Axis using (Axis; D; C; S; W)

v-of-axis : Axis → V₄
v-of-axis D = e
v-of-axis C = α
v-of-axis S = β
v-of-axis W = γ
