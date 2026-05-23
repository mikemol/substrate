------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Twist.ActEqualsPow
--
-- act-equals-pow: bridge act-on-canonical ↔ rot-pow ∘ swap-pow on
-- canonical inputs (24 refls covering the 6 S₃-canonical-pair cases
-- across the 4 V₄ elements).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Twist.ActEqualsPow where

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Axes using (v4-cover)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act-on-canonical)
open import Substrate.Groups.Actions.S3-on-V4.Generators using (rot-pow; swap-pow)

act-equals-pow : ∀ {n h} → Z₃.Canonical n → Z₂.Canonical h → ∀ v →
                 act-on-canonical n h v ≡ rot-pow n (swap-pow h v)
act-equals-pow (Z₃.c-pos zero)  (Z₂.c-pos zero) = v4-cover _ (refl , refl , refl , refl)
act-equals-pow (Z₃.c-pos (suc zero))  (Z₂.c-pos zero) = v4-cover _ (refl , refl , refl , refl)
act-equals-pow (Z₃.c-pos (suc (suc zero))) (Z₂.c-pos zero) = v4-cover _ (refl , refl , refl , refl)
act-equals-pow (Z₃.c-pos zero)  (Z₂.c-pos (suc zero)) = v4-cover _ (refl , refl , refl , refl)
act-equals-pow (Z₃.c-pos (suc zero))  (Z₂.c-pos (suc zero)) = v4-cover _ (refl , refl , refl , refl)
act-equals-pow (Z₃.c-pos (suc (suc zero))) (Z₂.c-pos (suc zero)) = v4-cover _ (refl , refl , refl , refl)
