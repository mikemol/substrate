------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB
--
-- The V₄-automorphism generator `swap-αβ` (order 2, fixes γ).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ)

swap-αβ : V₄ → V₄
swap-αβ e = e
swap-αβ α = β
swap-αβ β = α
swap-αβ γ = γ
