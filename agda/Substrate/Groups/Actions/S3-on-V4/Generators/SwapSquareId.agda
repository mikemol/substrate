------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.SwapSquareId
--
-- Order-2 identity for `swap-αβ`: applying it twice is identity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.SwapSquareId where

open import Substrate.Groups.V4.Bijection.V4

open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB using (swap-αβ)
open import Substrate.Foundation.Eq

swap-αβ²-id : (v : V₄) → swap-αβ (swap-αβ v) ≡ v
swap-αβ²-id e = refl
swap-αβ²-id α = refl
swap-αβ²-id β = refl
swap-αβ²-id γ = refl
