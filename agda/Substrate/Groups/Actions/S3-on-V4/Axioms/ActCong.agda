------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Axioms.ActCong
--
-- act-cong: act depends only on (canonical n, canonical h, v).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Axioms.ActCong where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection.V4
-- ⚑ `normalize` IS `ListPresentation`'s, not `Existential`'s (Ⓐ¹⁶″).
-- ⚑ AND THE `Cyclic.Base` IMPORTS ARE NEW: this file never imported Base, yet
-- the application needs `Gen`/`insert` from it.  `--lp-apply` reports exactly
-- that ("no `Cyclic.Base 1` binding in this file — the repair must ADD one"),
-- which is the judgement I had been making without noticing across ~28 hand
-- repairs, and the reason the transform stayed a census.
import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂-Base
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃-Base
import Substrate.Groups.Coxeter.Cyclic.Existential 1 as Z₂-Existential
import Substrate.Groups.Coxeter.Cyclic.Existential 2 as Z₃-Existential
import Substrate.Groups.Coxeter.ListPresentation
  Z₂-Base.Gen Z₂-Existential.Canonical-ex Z₂-Existential.c-ε
  Z₂-Base.insert Z₂-Existential.insert-canonical-ex as Z₂-LP
import Substrate.Groups.Coxeter.ListPresentation
  Z₃-Base.Gen Z₃-Existential.Canonical-ex Z₃-Existential.c-ε
  Z₃-Base.insert Z₃-Existential.insert-canonical-ex as Z₃-LP
import Substrate.Groups.S3 as S₃
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act using (act)
open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2

act-cong : ∀ {s₁ s₂ v₁ v₂} → s₁ S₃.≈ s₂ → v₁ ≡ v₂ →
           act s₁ v₁ ≡ act s₂ v₂
act-cong {n₁ , h₁} {n₂ , h₂} {v₁} {v₂} (n-eq , h-eq) v-eq =
  trans (cong₂ (λ x y → act-on-canonical x y v₁) n-eq h-eq)
        (cong (act-on-canonical (Z₃-LP.normalize n₂) (Z₂-LP.normalize h₂)) v-eq)
