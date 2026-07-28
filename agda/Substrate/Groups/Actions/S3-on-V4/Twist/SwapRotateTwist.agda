------------------------------------------------------------------------
-- …Twist.SwapRotateTwist — the swap/rotate braid twist on V₄.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Twist.SwapRotateTwist where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (v4-cover)

open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate using (rotate)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB using (swap-αβ)

swap-rotate-twist : (v : V₄) → swap-αβ (rotate v) ≡ rotate (rotate (swap-αβ v))
swap-rotate-twist = v4-cover _ (refl , refl , refl , refl)
