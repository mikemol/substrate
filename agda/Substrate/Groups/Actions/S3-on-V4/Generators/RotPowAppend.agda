------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.RotPowAppend
--
-- `rot-pow` composes over word concatenation:
--   rot-pow (w₁ ++ w₂) v ≡ rot-pow w₁ (rot-pow w₂ v)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.RotPowAppend where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate using (rotate)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPow using (rot-pow)

rot-pow-append : (w₁ w₂ : Word Z₃.Gen) (v : V₄) →
                 rot-pow (w₁ ++ w₂) v ≡ rot-pow w₁ (rot-pow w₂ v)
rot-pow-append []          w₂ v = refl
rot-pow-append (Z₃.a ∷ w₁) w₂ v = cong rotate (rot-pow-append w₁ w₂ v)
