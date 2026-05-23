------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.RotPowNormalizeEq
--
-- `rot-pow` respects Z₃-normalization:
--   rot-pow w v ≡ rot-pow (Z₃.normalize w) v
-- Reduces via `rot-step` on a Z₃-canonical accumulator (3-way cover);
-- the (c-pos (suc (suc zero))) case is exactly where `rotate³ v ≡ v` is needed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.RotPowNormalizeEq where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.Foundation.Fin using (zero; suc)

open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate       using (rotate)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPow       using (rot-pow)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotateCubeId using (rotate³-id)

rot-pow-normalize-eq : (w : Word Z₃.Gen) (v : V₄) →
                       rot-pow w v ≡ rot-pow (Z₃.normalize w) v
rot-pow-normalize-eq []         v = refl
rot-pow-normalize-eq (Z₃.a ∷ w) v =
  trans (cong rotate (rot-pow-normalize-eq w v))
        (rot-step (Z₃.normalize-canonical w) v)
  where
    rot-step : ∀ {x} → Z₃.Canonical x → (v : V₄) →
               rotate (rot-pow x v) ≡ rot-pow (Z₃.insert Z₃.a x) v
    rot-step (Z₃.c-pos zero)  _ = refl
    rot-step (Z₃.c-pos (suc zero))  _ = refl
    rot-step (Z₃.c-pos (suc (suc zero))) v = rotate³-id v
