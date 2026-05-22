------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Composition.Block01
--
-- act-∙ at h₁ = [] and h₂ = [a]: only the right factor swaps.
-- Both sides flatten to `rot-pow n₁ (rot-pow n₂ (swap-αβ v))`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Composition.Block01 where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.S3 as S₃
open import Substrate.Groups.Coxeter.Word using ([]; _∷_; _++_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act; act-on-canonical)
open import Substrate.Groups.Actions.S3-on-V4.Twist

act-∙-canonical-01 : ∀ {n₁ n₂} →
                     Z₃.Canonical n₁ → Z₃.Canonical n₂ →
                     ∀ v →
                     act ((n₁ , []) S₃.∙ (n₂ , Z₂.a ∷ [])) v ≡
                     act-on-canonical n₁ [] (act-on-canonical n₂ (Z₂.a ∷ []) v)
act-∙-canonical-01 {n₁} {n₂} c-n₁ c-n₂ v = trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , []) S₃.∙ (n₂ , Z₂.a ∷ [])) v ≡
                 rot-pow n₁ (rot-pow n₂ (swap-αβ v))
    LHS-to-pow =
      trans (act-equals-pow (Z₃.normalize-canonical (Z₃.normalize (n₁ ++ Z₃.normalize n₂))) Z₂.c-a v)
      (trans (cong (λ w → rot-pow w (swap-αβ v)) (Z₃.normalize-idem (n₁ ++ Z₃.normalize n₂)))
      (trans (sym (rot-pow-normalize-eq (n₁ ++ Z₃.normalize n₂) (swap-αβ v)))
      (trans (rot-pow-append n₁ (Z₃.normalize n₂) (swap-αβ v))
             (sym (cong (rot-pow n₁) (rot-pow-normalize-eq n₂ (swap-αβ v)))))))
    RHS-to-pow : act-on-canonical n₁ [] (act-on-canonical n₂ (Z₂.a ∷ []) v) ≡
                 rot-pow n₁ (rot-pow n₂ (swap-αβ v))
    RHS-to-pow =
      trans (act-equals-pow c-n₁ Z₂.c-ε (act-on-canonical n₂ (Z₂.a ∷ []) v))
            (cong (rot-pow n₁) (act-equals-pow c-n₂ Z₂.c-a v))
