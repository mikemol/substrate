------------------------------------------------------------------------
-- Substrate.Groups.S4-Composed
--
-- S₄ = V₄ ⋊ S₃, the symmetric group on 4 elements constructed
-- compositionally. Substrate-native (no stdlib).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Composed where

import Substrate.Groups.V4 as V4
import Substrate.Groups.S3 as S₃
import Substrate.Groups.Actions.S3-on-V4 as φ
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)
open import Substrate.Algebra.Group.ToSetoid using (to-setoid)

------------------------------------------------------------------------
-- 1. Open the SemidirectProductGroup combinator with V₄ as N and S₃ as H.
--
-- V₄ is `Substrate.Algebra.Group V₄`; coerce to SetoidGroup via
-- `to-setoid`. S₃ already exports `S₃-Group : SetoidGroup`.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.SemidirectProductGroup
  _ _
  (to-setoid V4.V₄-Group)  -- N (normal subgroup)
  _ _
  S₃.S₃-Group              -- H (acting group)

------------------------------------------------------------------------
-- 2. Plug in the action and re-export everything.
------------------------------------------------------------------------

open WithAction
  φ.act
  (λ {h₁} {h₂} {n₁} {n₂} h-eq n-eq → φ.act-cong {h₁} {h₂} {n₁} {n₂} h-eq n-eq)
  (λ n → φ.act-ε n)
  (λ h₁ h₂ n → φ.act-∙ h₁ h₂ n)
  (λ h n₁ n₂ → φ.act-hom h n₁ n₂)
  (λ h → φ.act-ε-N h)
  public

------------------------------------------------------------------------
-- 3. Top-level alias for the SetoidGroup bundle.
------------------------------------------------------------------------

S₄-Group : SetoidGroup Carrier _≈_
S₄-Group = Group-bundle
