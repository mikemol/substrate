------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Axioms.ActCong
--
-- act-cong: act depends only on (canonical n, canonical h, v).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Axioms.ActCong where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection using (V₄)
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂-Existential
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃-Existential
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; trans; cong; cong₂)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act using (act)
open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)

act-cong : ∀ {s₁ s₂ v₁ v₂} → s₁ S₃.≈ s₂ → v₁ ≡ v₂ →
           act s₁ v₁ ≡ act s₂ v₂
act-cong {n₁ , h₁} {n₂ , h₂} {v₁} {v₂} (n-eq , h-eq) v-eq =
  trans (cong₂ (λ x y → act-on-canonical x y v₁) n-eq h-eq)
        (cong (act-on-canonical (Z₃-Existential.normalize n₂) (Z₂-Existential.normalize h₂)) v-eq)
