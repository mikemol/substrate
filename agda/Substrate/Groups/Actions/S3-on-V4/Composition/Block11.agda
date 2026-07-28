------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Composition.Block11
--
-- act-∙ at h₁ = [a] and h₂ = [a]: both factors swap. The LEFT factor's
-- swap twist inverts n₂; the H-component swaps collapse via swap-αβ²-id.
-- Both sides flatten to `rot-pow n₁ (swap-αβ (rot-pow n₂ (swap-αβ v)))`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Composition.Block11 where

import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂B
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂E
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃E
import Substrate.Groups.Coxeter.Cyclic.Inverse 2 as Z₃I
import Substrate.Groups.Coxeter.Cyclic.Core 2 as Z₃C
import Substrate.Groups.S3 as S₃
open import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act using (act)
open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)
open import Substrate.Groups.Actions.S3-on-V4.Twist.ActEqualsPow using (act-equals-pow)
open import Substrate.Groups.Actions.S3-on-V4.Twist.RotPowSwapTwist using (rot-pow-swap-twist)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPow using (rot-pow)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapAB using (swap-αβ)
open import Substrate.Groups.Actions.S3-on-V4.Generators.SwapSquareId using (swap-αβ²-id)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotPowNormalizeEq using (rot-pow-normalize-eq)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄)
open import Substrate.Groups.Coxeter.Word using ([]; _∷_; _++_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)

open import Substrate.Groups.Actions.S3-on-V4.Composition.RotPowComposeChain using (rot-pow-compose-chain)

act-∙-canonical-11 : ∀ {n₁ n₂} →
                     Z₃E.Canonical-ex n₁ → Z₃E.Canonical-ex n₂ →
                     ∀ v →
                     act ((n₁ , Z₂B.a ∷ []) S₃.∙ (n₂ , Z₂B.a ∷ [])) v ≡
                     act-on-canonical n₁ (Z₂B.a ∷ []) (act-on-canonical n₂ (Z₂B.a ∷ []) v)
act-∙-canonical-11 {n₁} {n₂} c-n₁ c-n₂ v = trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , Z₂B.a ∷ []) S₃.∙ (n₂ , Z₂B.a ∷ [])) v ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ (swap-αβ v)))
    LHS-to-pow =
      trans (act-equals-pow (Z₃E.normalize-canonical (Z₃E.normalize (n₁ ++ Z₃I.inv (Z₃E.normalize n₂)))) (Z₂E.c-pos zero) v)
      (trans (rot-pow-compose-chain n₁ (Z₃I.inv (Z₃E.normalize n₂)) v)
      (trans (cong (λ w → rot-pow n₁ (rot-pow (Z₃I.inv w) v)) (Z₃C.canonical-is-fixed c-n₂))
      (trans (cong (λ x → rot-pow n₁ (rot-pow (Z₃I.inv n₂) x)) (sym (swap-αβ²-id v)))
             (cong (rot-pow n₁) (sym (rot-pow-swap-twist c-n₂ (swap-αβ v)))))))
    RHS-to-pow : act-on-canonical n₁ (Z₂B.a ∷ []) (act-on-canonical n₂ (Z₂B.a ∷ []) v) ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ (swap-αβ v)))
    RHS-to-pow =
      trans (act-equals-pow c-n₁ (Z₂E.c-pos ₁) (act-on-canonical n₂ (Z₂B.a ∷ []) v))
            (cong (λ x → rot-pow n₁ (swap-αβ x)) (act-equals-pow c-n₂ (Z₂E.c-pos ₁) v))
