------------------------------------------------------------------------
-- Substrate.Axes.V4Roundtrip
--
-- v-of-axis ∘ axis-of-v ≡ id.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.V4Roundtrip where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Groups.V4.Operations using (v4-cover)
open import Substrate.Axes.VOfAxis using (v-of-axis)
open import Substrate.Axes.AxisOfV using (axis-of-v)

v-of-axis-axis-of-v : (v : V₄) → v-of-axis (axis-of-v v) ≡ v
v-of-axis-axis-of-v = v4-cover _ (refl , refl , refl , refl)
