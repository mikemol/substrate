------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.RotateCubeId
--
-- Order-3 identity for `rotate`: applying it three times is identity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.RotateCubeId where

open import Substrate.Groups.V4.Bijection.V4

open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate using (rotate)
open import Substrate.Foundation.Eq

rotate³-id : (v : V₄) → rotate (rotate (rotate v)) ≡ v
rotate³-id e = refl
rotate³-id α = refl
rotate³-id β = refl
rotate³-id γ = refl
