------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.RotPowAppend
--
-- `rot-pow` composes over word concatenation:
--   rot-pow (w₁ ++ w₂) v ≡ rot-pow w₁ (rot-pow w₂ v)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.RotPowAppend where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection using (V₄)
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃-Base
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate using (rotate)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPow using (rot-pow)

rot-pow-append : (w₁ w₂ : Word Z₃-Base.Gen) (v : V₄) →
                 rot-pow (w₁ ++ w₂) v ≡ rot-pow w₁ (rot-pow w₂ v)
rot-pow-append []          w₂ v = refl
rot-pow-append (Z₃-Base.a ∷ w₁) w₂ v = cong rotate (rot-pow-append w₁ w₂ v)
