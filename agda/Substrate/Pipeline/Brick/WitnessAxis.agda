------------------------------------------------------------------------
-- Substrate.Pipeline.Brick.WitnessAxis
--
-- witness-axis : Witnessing → Axis. Maps each oriented morphism to
-- its third-axis witness label.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Brick.WitnessAxis where

open import Substrate.Pipeline.Brick.Witnessing using (Witnessing; D⇒S; S⇒D; D⇒C; C⇒D; S⇒C; C⇒S)
open import Substrate.Pipeline.Brick.Axis using (BrickAxis; 𝔻; 𝕊; ℂ)

witness-axis : Witnessing → BrickAxis
witness-axis D⇒S = ℂ
witness-axis S⇒D = ℂ
witness-axis D⇒C = 𝕊
witness-axis C⇒D = 𝕊
witness-axis S⇒C = 𝔻
witness-axis C⇒S = 𝔻
