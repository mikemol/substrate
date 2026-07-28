------------------------------------------------------------------------
-- Substrate.Groups.S4-Composed
--
-- S₄ = V₄ ⋊ S₃, the symmetric group on 4 elements constructed
-- compositionally. Substrate-native (no stdlib).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Composed where

open import Substrate.Groups.V4.Bundle using (V₄-Group)
import Substrate.Groups.S3 as S₃
import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act as φ-Act
import Substrate.Groups.Actions.S3-on-V4.Axioms.ActCong as φ-ActCong
import Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilon as φ-ActEpsilon
import Substrate.Groups.Actions.S3-on-V4.Composition.ActDot as φ-ActDot
import Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHom as φ-ActHom
import Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilonN.EpsilonN as φ-EpsilonN
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
  (to-setoid V₄-Group)  -- N (normal subgroup)
  _ _
  S₃.S₃-Group              -- H (acting group)

------------------------------------------------------------------------
-- 2. Plug in the action and re-export everything.
------------------------------------------------------------------------

open WithAction
  φ-Act.act
  (λ {h₁} {h₂} {n₁} {n₂} h-eq n-eq → φ-ActCong.act-cong {h₁} {h₂} {n₁} {n₂} h-eq n-eq)
  (λ n → φ-ActEpsilon.act-ε n)
  (λ h₁ h₂ n → φ-ActDot.act-∙ h₁ h₂ n)
  (λ h n₁ n₂ → φ-ActHom.act-hom h n₁ n₂)
  (λ h → φ-EpsilonN.act-ε-N h)
  public

------------------------------------------------------------------------
-- 3. Top-level alias for the SetoidGroup bundle.
------------------------------------------------------------------------

S₄-Group : SetoidGroup Carrier _≈_
S₄-Group = Group-bundle
