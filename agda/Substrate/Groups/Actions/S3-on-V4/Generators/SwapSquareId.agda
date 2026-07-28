------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.SwapSquareId
--
-- Order-2 identity for `swap-αβ`: applying it twice is identity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.SwapSquareId where

import Substrate.Groups.V4.Bijection as V4
open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB using (swap-αβ)

swap-αβ²-id : (v : V₄) → swap-αβ (swap-αβ v) ≡ v
swap-αβ²-id V4.e = refl
swap-αβ²-id V4.α = refl
swap-αβ²-id V4.β = refl
swap-αβ²-id V4.γ = refl
