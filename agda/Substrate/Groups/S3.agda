------------------------------------------------------------------------
-- Substrate.Groups.S3
--
-- S₃ = ℤ/3 ⋊ ℤ/2, the dihedral / symmetric group on 3 elements.
-- Substrate-native (no stdlib).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S3 where

import Substrate.Groups.Z2-Coxeter-Group as Z₂G
import Substrate.Groups.Z3-Coxeter-Group as Z₃G
import Substrate.Groups.Actions.Z2-on-Z3 as φ
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)

------------------------------------------------------------------------
-- 1. Open the SemidirectProductGroup combinator with the two atoms.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.SemidirectProductGroup
  _ _
  Z₃G.Group-bundle  -- N (normal subgroup)
  _ _
  Z₂G.Group-bundle  -- H (acting group)

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

S₃-Group : SetoidGroup Carrier _≈_
S₃-Group = Group-bundle
