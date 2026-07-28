------------------------------------------------------------------------
-- Substrate.Groups.S3
--
-- S₃ = ℤ/3 ⋊ ℤ/2, the dihedral / symmetric group on 3 elements.
-- Substrate-native (no stdlib).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S3 where
import Substrate.Groups.Capabilities.CoxeterGroup.Witness as CoxeterGroupW
import Substrate.Groups.Actions.Z2-on-Z3.Act as φ-Act
import Substrate.Groups.Actions.Z2-on-Z3.ActCong as φ-ActCong
import Substrate.Groups.Actions.Z2-on-Z3.ActEpsilonN.EpsilonN as φ-EpsilonN
import Substrate.Groups.Actions.Z2-on-Z3.ActHom.Hom as φ-Hom
import Substrate.Groups.Actions.Z2-on-Z3.ActDot.Dot as φ-Dot
import Substrate.Groups.Actions.Z2-on-Z3.ActEpsilon as φ-ActEpsilon
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)
cap-Z₃ = CoxeterGroupW.cap 2

import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₃ as Z₃G-GroupFromCapability
cap-Z₂ = CoxeterGroupW.cap 1



import Substrate.Groups.Coxeter.GroupFromCapability cap-Z₂ as Z₂G-GroupFromCapability

open import Substrate.Groups.Coxeter.SemidirectProductGroup
  _ _
  Z₃G-GroupFromCapability.Group-bundle  -- N (normal subgroup)
  _ _
  Z₂G-GroupFromCapability.Group-bundle  -- H (acting group)

open WithAction
  φ-Act.act
  (λ {h₁} {h₂} {n₁} {n₂} h-eq n-eq → φ-ActCong.act-cong {h₁} {h₂} {n₁} {n₂} h-eq n-eq)
  (λ n → φ-ActEpsilon.act-ε n)
  (λ h₁ h₂ n → φ-Dot.act-∙ h₁ h₂ n)
  (λ h n₁ n₂ → φ-Hom.act-hom h n₁ n₂)
  (λ h → φ-EpsilonN.act-ε-N h)
  public
------------------------------------------------------------------------
-- 1. Open the SemidirectProductGroup combinator with the two atoms.
------------------------------------------------------------------------


------------------------------------------------------------------------
-- 2. Plug in the action and re-export everything.
------------------------------------------------------------------------


------------------------------------------------------------------------
-- 3. Top-level alias for the SetoidGroup bundle.
------------------------------------------------------------------------

S₃-Group : SetoidGroup Carrier _≈_
S₃-Group = Group-bundle
