------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Composition.ActDot
--
-- act-∙: full action composition via act-cong + S₃.∙-cong over
-- normalize-idem, dispatching to act-∙-canonical on the canonical
-- normalize-canonical witnesses.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Composition.ActDot where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act)
open import Substrate.Groups.Actions.S3-on-V4.Axioms.ActCong using (act-cong)
open import Substrate.Groups.Actions.S3-on-V4.Composition.ActDotCanonical using (act-∙-canonical)

act-∙ : ∀ s₁ s₂ v → act (s₁ S₃.∙ s₂) v ≡ act s₁ (act s₂ v)
act-∙ (n₁ , h₁) (n₂ , h₂) v =
  trans
    (act-cong {s₁ = (n₁ , h₁) S₃.∙ (n₂ , h₂)}
              {s₂ = (Z₃.normalize n₁ , Z₂.normalize h₁) S₃.∙ (Z₃.normalize n₂ , Z₂.normalize h₂)}
              {v₁ = v} {v₂ = v}
      (S₃.∙-cong {a₁ = n₁ , h₁} {a₂ = Z₃.normalize n₁ , Z₂.normalize h₁}
                  {b₁ = n₂ , h₂} {b₂ = Z₃.normalize n₂ , Z₂.normalize h₂}
                  (sym (Z₃.normalize-idem n₁) , sym (Z₂.normalize-idem h₁))
                  (sym (Z₃.normalize-idem n₂) , sym (Z₂.normalize-idem h₂)))
      refl)
    (act-∙-canonical (Z₃.normalize-canonical n₁) (Z₂.normalize-canonical h₁)
                     (Z₃.normalize-canonical n₂) (Z₂.normalize-canonical h₂) v)
