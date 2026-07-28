------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Composition.Block00
--
-- act-∙ at h₁ = [] and h₂ = []: both inputs are pure rotations,
-- so no swap-induced twist appears. Both sides flatten to
-- `rot-pow n₁ (rot-pow n₂ v)` via Twist.act-equals-pow + Generators
-- composition lemmas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Composition.Block00 where

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
open import Substrate.Groups.Coxeter.Word using ([]; _∷_; _++_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)

open import Substrate.Groups.Actions.S3-on-V4.Composition.RotPowComposeChain using (rot-pow-compose-chain)

act-∙-canonical-00 : ∀ {n₁ n₂} →
                     Z₃E.Canonical-ex n₁ → Z₃E.Canonical-ex n₂ →
                     ∀ v →
                     act ((n₁ , []) S₃.∙ (n₂ , [])) v ≡
                     act-on-canonical n₁ [] (act-on-canonical n₂ [] v)
act-∙-canonical-00 {n₁} {n₂} c-n₁ c-n₂ v = trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , []) S₃.∙ (n₂ , [])) v ≡ rot-pow n₁ (rot-pow n₂ v)
    LHS-to-pow =
      trans (act-equals-pow (Z₃E.normalize-canonical (Z₃E.normalize (n₁ ++ Z₃E.normalize n₂))) (Z₂E.c-pos zero) v)
      (trans (rot-pow-compose-chain n₁ (Z₃E.normalize n₂) v)
             (sym (cong (rot-pow n₁) (rot-pow-normalize-eq n₂ v))))
    RHS-to-pow : act-on-canonical n₁ [] (act-on-canonical n₂ [] v) ≡ rot-pow n₁ (rot-pow n₂ v)
    RHS-to-pow =
      trans (act-equals-pow c-n₁ (Z₂E.c-pos zero) (act-on-canonical n₂ [] v))
            (cong (rot-pow n₁) (act-equals-pow c-n₂ (Z₂E.c-pos zero) v))
