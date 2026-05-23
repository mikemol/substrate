------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Composition.Block11
--
-- act-∙ at h₁ = [a] and h₂ = [a]: both factors swap. The LEFT factor's
-- swap twist inverts n₂; the H-component swaps collapse via swap-αβ²-id.
-- Both sides flatten to `rot-pow n₁ (swap-αβ (rot-pow n₂ (swap-αβ v)))`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Composition.Block11 where

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
open import Substrate.Groups.Actions.S3-on-V4.Composition.RotPowComposeChain
  using (rot-pow-compose-chain)

act-∙-canonical-11 : ∀ {n₁ n₂} →
                     Z₃.Canonical n₁ → Z₃.Canonical n₂ →
                     ∀ v →
                     act ((n₁ , Z₂.a ∷ []) S₃.∙ (n₂ , Z₂.a ∷ [])) v ≡
                     act-on-canonical n₁ (Z₂.a ∷ []) (act-on-canonical n₂ (Z₂.a ∷ []) v)
act-∙-canonical-11 {n₁} {n₂} c-n₁ c-n₂ v = trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , Z₂.a ∷ []) S₃.∙ (n₂ , Z₂.a ∷ [])) v ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ (swap-αβ v)))
    LHS-to-pow =
      trans (act-equals-pow (Z₃.normalize-canonical (Z₃.normalize (n₁ ++ Z₃.inv (Z₃.normalize n₂)))) Z₂.c-ε v)
      (trans (rot-pow-compose-chain n₁ (Z₃.inv (Z₃.normalize n₂)) v)
      (trans (cong (λ w → rot-pow n₁ (rot-pow (Z₃.inv w) v)) (Z₃.canonical-is-fixed c-n₂))
      (trans (cong (λ x → rot-pow n₁ (rot-pow (Z₃.inv n₂) x)) (sym (swap-αβ²-id v)))
             (cong (rot-pow n₁) (sym (rot-pow-swap-twist c-n₂ (swap-αβ v)))))))
    RHS-to-pow : act-on-canonical n₁ (Z₂.a ∷ []) (act-on-canonical n₂ (Z₂.a ∷ []) v) ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ (swap-αβ v)))
    RHS-to-pow =
      trans (act-equals-pow c-n₁ Z₂.c-a (act-on-canonical n₂ (Z₂.a ∷ []) v))
            (cong (λ x → rot-pow n₁ (swap-αβ x)) (act-equals-pow c-n₂ Z₂.c-a v))
