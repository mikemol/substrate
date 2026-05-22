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

act-∙-canonical-00 : ∀ {n₁ n₂} →
                     Z₃.Canonical n₁ → Z₃.Canonical n₂ →
                     ∀ v →
                     act ((n₁ , []) S₃.∙ (n₂ , [])) v ≡
                     act-on-canonical n₁ [] (act-on-canonical n₂ [] v)
act-∙-canonical-00 {n₁} {n₂} c-n₁ c-n₂ v = trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , []) S₃.∙ (n₂ , [])) v ≡ rot-pow n₁ (rot-pow n₂ v)
    LHS-to-pow =
      trans (act-equals-pow (Z₃.normalize-canonical (Z₃.normalize (n₁ ++ Z₃.normalize n₂))) Z₂.c-ε v)
      (trans (cong (λ w → rot-pow w v) (Z₃.normalize-idem (n₁ ++ Z₃.normalize n₂)))
      (trans (sym (rot-pow-normalize-eq (n₁ ++ Z₃.normalize n₂) v))
      (trans (rot-pow-append n₁ (Z₃.normalize n₂) v)
             (sym (cong (rot-pow n₁) (rot-pow-normalize-eq n₂ v))))))
    RHS-to-pow : act-on-canonical n₁ [] (act-on-canonical n₂ [] v) ≡ rot-pow n₁ (rot-pow n₂ v)
    RHS-to-pow =
      trans (act-equals-pow c-n₁ Z₂.c-ε (act-on-canonical n₂ [] v))
            (cong (rot-pow n₁) (act-equals-pow c-n₂ Z₂.c-ε v))
