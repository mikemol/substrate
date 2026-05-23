------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Composition.ActDotCanonical
--
-- act-∙-canonical: per-block dispatch over the four (h₁, h₂)
-- canonical-element combinations. Each block proof lives in its own
-- Block00..Block11 file; this file just routes the cases.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Composition.ActDotCanonical where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄)
open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act; act-on-canonical)
open import Substrate.Groups.Actions.S3-on-V4.Composition.Block00 using (act-∙-canonical-00)
open import Substrate.Groups.Actions.S3-on-V4.Composition.Block01 using (act-∙-canonical-01)
open import Substrate.Groups.Actions.S3-on-V4.Composition.Block10 using (act-∙-canonical-10)
open import Substrate.Groups.Actions.S3-on-V4.Composition.Block11 using (act-∙-canonical-11)

act-∙-canonical : ∀ {n₁ h₁ n₂ h₂} →
                  Z₃.Canonical n₁ → Z₂.Canonical h₁ →
                  Z₃.Canonical n₂ → Z₂.Canonical h₂ →
                  ∀ v →
                  act ((n₁ , h₁) S₃.∙ (n₂ , h₂)) v ≡
                  act-on-canonical n₁ h₁ (act-on-canonical n₂ h₂ v)
act-∙-canonical c-n₁ (Z₂.c-pos zero) c-n₂ (Z₂.c-pos zero) v = act-∙-canonical-00 c-n₁ c-n₂ v
act-∙-canonical c-n₁ (Z₂.c-pos zero) c-n₂ (Z₂.c-pos ₁) v = act-∙-canonical-01 c-n₁ c-n₂ v
act-∙-canonical c-n₁ (Z₂.c-pos ₁) c-n₂ (Z₂.c-pos zero) v = act-∙-canonical-10 c-n₁ c-n₂ v
act-∙-canonical c-n₁ (Z₂.c-pos ₁) c-n₂ (Z₂.c-pos ₁) v = act-∙-canonical-11 c-n₁ c-n₂ v
