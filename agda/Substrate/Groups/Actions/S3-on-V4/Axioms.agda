------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Axioms
--
-- Easy action axioms: act-cong, act-ε, act-ε-N.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Axioms where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong; cong₂)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch public

------------------------------------------------------------------------
-- act-cong: depends only on (canonical n, canonical h, v).
------------------------------------------------------------------------

act-cong : ∀ {s₁ s₂ v₁ v₂} → s₁ S₃.≈ s₂ → v₁ ≡ v₂ →
           act s₁ v₁ ≡ act s₂ v₂
act-cong {n₁ , h₁} {n₂ , h₂} {v₁} {v₂} (n-eq , h-eq) v-eq =
  trans (cong₂ (λ x y → act-on-canonical x y v₁) n-eq h-eq)
        (cong (act-on-canonical (Z₃.normalize n₂) (Z₂.normalize h₂)) v-eq)

------------------------------------------------------------------------
-- act-ε: act S₃.ε v ≡ v.
------------------------------------------------------------------------

act-ε : ∀ v → act S₃.ε v ≡ v
act-ε v = refl

------------------------------------------------------------------------
-- act-ε-N: act g e ≡ e (every action preserves V₄'s identity).
------------------------------------------------------------------------

act-ε-N-on-canonical : ∀ {n h} → Z₃.Canonical n → Z₂.Canonical h →
                       act-on-canonical n h e ≡ e
act-ε-N-on-canonical Z₃.c-ε  Z₂.c-ε = refl
act-ε-N-on-canonical Z₃.c-a  Z₂.c-ε = refl
act-ε-N-on-canonical Z₃.c-aa Z₂.c-ε = refl
act-ε-N-on-canonical Z₃.c-ε  Z₂.c-a = refl
act-ε-N-on-canonical Z₃.c-a  Z₂.c-a = refl
act-ε-N-on-canonical Z₃.c-aa Z₂.c-a = refl

act-ε-N : ∀ s → act s e ≡ e
act-ε-N (n , h) = act-ε-N-on-canonical (Z₃.normalize-canonical n) (Z₂.normalize-canonical h)
