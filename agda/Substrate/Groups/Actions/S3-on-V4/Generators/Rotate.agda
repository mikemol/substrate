------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.Rotate
--
-- The V₄-automorphism generator `rotate` (order 3, αβγ-cycle).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.Rotate where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e; α; β; γ)

rotate : V₄ → V₄
rotate e = e
rotate α = β
rotate β = γ
rotate γ = α
