------------------------------------------------------------------------
-- Substrate.Axes.AxisRoundtrip
--
-- axis-of-v ∘ v-of-axis ≡ id.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.AxisRoundtrip where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Axes.Axis using (Axis)
open import Substrate.Axes.VOfAxis using (v-of-axis)
open import Substrate.Axes.AxisOfV using (axis-of-v)
open import Substrate.Axes.Cover using (axis-cover)

axis-of-v-v-of-axis : (a : Axis) → axis-of-v (v-of-axis a) ≡ a
axis-of-v-v-of-axis = axis-cover _ (refl , refl , refl , refl)
