------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Composition.Block10
--
-- act-∙ at h₁ = [a] and h₂ = []: the LEFT factor's swap twist
-- inverts n₂. Both sides flatten to `rot-pow n₁ (swap-αβ (rot-pow n₂ v))`
-- via rot-pow-swap-twist (the dihedral twist).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Composition.Block10 where

import Substrate.Groups.V4 as V4
open V4 using (V₄)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄)
open import Substrate.Groups.Coxeter.Word using ([]; _∷_; _++_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act; act-on-canonical)
open import Substrate.Groups.Actions.S3-on-V4.Twist
open import Substrate.Groups.Actions.S3-on-V4.Composition.RotPowComposeChain
  using (rot-pow-compose-chain)

act-∙-canonical-10 : ∀ {n₁ n₂} →
                     Z₃.Canonical n₁ → Z₃.Canonical n₂ →
                     ∀ v →
                     act ((n₁ , Z₂.a ∷ []) S₃.∙ (n₂ , [])) v ≡
                     act-on-canonical n₁ (Z₂.a ∷ []) (act-on-canonical n₂ [] v)
act-∙-canonical-10 {n₁} {n₂} c-n₁ c-n₂ v = trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , Z₂.a ∷ []) S₃.∙ (n₂ , [])) v ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ v))
    LHS-to-pow =
      trans (act-equals-pow (Z₃.normalize-canonical (Z₃.normalize (n₁ ++ Z₃.inv (Z₃.normalize n₂)))) (Z₂.c-pos ₁) v)
      (trans (rot-pow-compose-chain n₁ (Z₃.inv (Z₃.normalize n₂)) (swap-αβ v))
      (trans (cong (λ w → rot-pow n₁ (rot-pow (Z₃.inv w) (swap-αβ v))) (Z₃.canonical-is-fixed c-n₂))
             (cong (rot-pow n₁) (sym (rot-pow-swap-twist c-n₂ v)))))
    RHS-to-pow : act-on-canonical n₁ (Z₂.a ∷ []) (act-on-canonical n₂ [] v) ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ v))
    RHS-to-pow =
      trans (act-equals-pow c-n₁ (Z₂.c-pos ₁) (act-on-canonical n₂ [] v))
            (cong (λ x → rot-pow n₁ (swap-αβ x)) (act-equals-pow c-n₂ (Z₂.c-pos zero) v))
