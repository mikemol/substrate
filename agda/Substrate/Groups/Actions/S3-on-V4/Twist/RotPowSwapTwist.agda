------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Twist.RotPowSwapTwist
--
-- The generator-level twist lifted to canonical n : Z₃ inputs:
--   swap-αβ ∘ rot-pow n ≡ rot-pow (Z₃.inv n) ∘ swap-αβ
-- (3 cases × 4 V₄ refls = 12 refls via v4-cover).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Twist.RotPowSwapTwist where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Axes using (v4-cover)

open import Substrate.Groups.Actions.S3-on-V4.Generators using (rot-pow; swap-αβ)

rot-pow-swap-twist : ∀ {n} → Z₃.Canonical n → (v : V₄) →
                     swap-αβ (rot-pow n v) ≡ rot-pow (Z₃.inv n) (swap-αβ v)
rot-pow-swap-twist (Z₃.c-pos zero)  = v4-cover _ (refl , refl , refl , refl)
rot-pow-swap-twist (Z₃.c-pos (suc zero))  = v4-cover _ (refl , refl , refl , refl)
rot-pow-swap-twist (Z₃.c-pos (suc (suc zero))) = v4-cover _ (refl , refl , refl , refl)
