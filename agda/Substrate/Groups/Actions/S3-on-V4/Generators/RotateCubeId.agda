------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.RotateCubeId
--
-- Order-3 identity for `rotate`: applying it three times is identity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.RotateCubeId where

import Substrate.Groups.V4.Bijection as V4
open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate using (rotate)

rotate³-id : (v : V₄) → rotate (rotate (rotate v)) ≡ v
rotate³-id V4.e = refl
rotate³-id V4.α = refl
rotate³-id V4.β = refl
rotate³-id V4.γ = refl
