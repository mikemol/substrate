------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.SwapPowAppend
--
-- `swap-pow` composes over word concatenation:
--   swap-pow (w₁ ++ w₂) v ≡ swap-pow w₁ (swap-pow w₂ v)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.SwapPowAppend where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z2-Coxeter as Z₂
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB  using (swap-αβ)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapPow using (swap-pow)

swap-pow-append : (w₁ w₂ : Word Z₂.Gen) (v : V₄) →
                  swap-pow (w₁ ++ w₂) v ≡ swap-pow w₁ (swap-pow w₂ v)
swap-pow-append []          w₂ v = refl
swap-pow-append (Z₂.a ∷ w₁) w₂ v = cong swap-αβ (swap-pow-append w₁ w₂ v)
