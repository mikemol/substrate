------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Generators.SwapPowNormalizeEq
--
-- `swap-pow` respects Z₂-normalization:
--   swap-pow w v ≡ swap-pow (Z₂.normalize w) v
-- Reduces via `swap-step` on a Z₂-canonical accumulator (2-way cover);
-- the c-a case is exactly where `swap-αβ² v ≡ v` is needed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Generators.SwapPowNormalizeEq where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z2-Coxeter as Z₂
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)

open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB       using (swap-αβ)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapPow      using (swap-pow)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapSquareId using (swap-αβ²-id)

swap-pow-normalize-eq : (w : Word Z₂.Gen) (v : V₄) →
                        swap-pow w v ≡ swap-pow (Z₂.normalize w) v
swap-pow-normalize-eq []         v = refl
swap-pow-normalize-eq (Z₂.a ∷ w) v =
  trans (cong swap-αβ (swap-pow-normalize-eq w v))
        (swap-step (Z₂.normalize-canonical w) v)
  where
    swap-step : ∀ {x} → Z₂.Canonical x → (v : V₄) →
                swap-αβ (swap-pow x v) ≡ swap-pow (Z₂.insert Z₂.a x) v
    swap-step Z₂.c-ε _ = refl
    swap-step Z₂.c-a v = swap-αβ²-id v
