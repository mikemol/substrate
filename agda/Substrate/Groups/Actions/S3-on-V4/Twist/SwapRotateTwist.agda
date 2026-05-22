------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Twist.SwapRotateTwist
--
-- The dihedral generator-level relation:
--   swap-αβ ∘ rotate ≡ rotate² ∘ swap-αβ
-- (encoded as a single 4-way v4-cover refl tuple).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Twist.SwapRotateTwist where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Axes using (v4-cover)

open import Substrate.Groups.Actions.S3-on-V4.Generators using (rotate; swap-αβ)

swap-rotate-twist : (v : V₄) → swap-αβ (rotate v) ≡ rotate (rotate (swap-αβ v))
swap-rotate-twist = v4-cover _ (refl , refl , refl , refl)
