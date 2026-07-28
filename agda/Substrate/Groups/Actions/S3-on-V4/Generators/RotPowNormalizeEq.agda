------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.RotPowNormalizeEq
--
-- `rot-pow` respects Z₃-normalization:
--   rot-pow w v ≡ rot-pow (Z₃-Existential.normalize w) v
-- Reduces via `rot-step` on a Z₃-canonical accumulator (3-way cover);
-- the (c-pos ₂) case is exactly where `rotate³ v ≡ v` is needed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.RotPowNormalizeEq where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection using (V₄)
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃-Existential
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃-Base
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄)
open import Substrate.Foundation.Fin.Fin

open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate       using (rotate)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPow       using (rot-pow)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotateCubeId using (rotate³-id)

rot-pow-normalize-eq : (w : Word Z₃-Base.Gen) (v : V₄) →
                       rot-pow w v ≡ rot-pow (Z₃-Existential.normalize w) v
rot-pow-normalize-eq []         v = refl
rot-pow-normalize-eq (Z₃-Base.a ∷ w) v =
  trans (cong rotate (rot-pow-normalize-eq w v))
        (rot-step (Z₃-Existential.normalize-canonical w) v)
  where
    rot-step : ∀ {x} → Z₃-Existential.Canonical-ex x → (v : V₄) →
               rotate (rot-pow x v) ≡ rot-pow (Z₃-Base.insert Z₃-Base.a x) v
    rot-step (Z₃-Existential.c-pos zero)  _ = refl
    rot-step (Z₃-Existential.c-pos ₁)  _ = refl
    rot-step (Z₃-Existential.c-pos ₂) v = rotate³-id v
