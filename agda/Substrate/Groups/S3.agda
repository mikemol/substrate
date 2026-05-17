------------------------------------------------------------------------
-- Substrate.Groups.S3
--
-- S₃ = ℤ/3 ⋊ ℤ/2, the dihedral / symmetric group on 3 elements,
-- constructed compositionally from atoms via the Coxeter framework.
--
-- Composition:
--   Z₃G.Group-bundle  (normal subgroup, from Substrate.Groups.Z3-Coxeter-Group)
--   Z₂G.Group-bundle  (acting group, from Substrate.Groups.Z2-Coxeter-Group)
--   act               (Z/2 → Aut(Z/3) by inversion, from
--                      Substrate.Groups.Actions.Z2-on-Z3)
--
-- Output: a stdlib Group bundle (Algebra.Bundles.Group 0ℓ 0ℓ) with
-- Carrier = Word Z₃.Gen × Word Z₂.Gen, twisted ∙ via the action.
--
-- Per [[feedback-composable-primitives-over-flat-enumeration]]: this
-- file is intentionally minimal — composition IS the construction.
-- The "compositional" S₃ has no enumeration of its 6 elements.
-- Theorems about S₃ either come for free from the SemidirectProductGroup
-- combinator, or are added downstream.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S3 where

import Substrate.Groups.Z2-Coxeter-Group as Z₂G
import Substrate.Groups.Z3-Coxeter-Group as Z₃G
import Substrate.Groups.Actions.Z2-on-Z3 as φ
open import Algebra.Bundles using (Group)
open import Level using (0ℓ)

------------------------------------------------------------------------
-- 1. Open the SemidirectProductGroup combinator with the two atoms.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.SemidirectProductGroup
  Z₃G.Group-bundle  -- N (normal subgroup)
  Z₂G.Group-bundle  -- H (acting group)

------------------------------------------------------------------------
-- 2. Plug in the action and re-export everything.
------------------------------------------------------------------------

-- Pass each implicit explicitly via λ-binding so Agda doesn't need
-- to invert Z₂.normalize / Z₃.normalize when checking the action
-- axioms against SP's expected types.
open WithAction
  φ.act
  (λ {h₁} {h₂} {n₁} {n₂} h-eq n-eq → φ.act-cong {h₁} {h₂} {n₁} {n₂} h-eq n-eq)
  (λ n → φ.act-ε n)
  (λ h₁ h₂ n → φ.act-∙ h₁ h₂ n)
  (λ h n₁ n₂ → φ.act-hom h n₁ n₂)
  (λ h → φ.act-ε-N h)
  public

------------------------------------------------------------------------
-- 3. Top-level alias for the Group bundle.
------------------------------------------------------------------------

S₃-Group : Group 0ℓ 0ℓ
S₃-Group = Group-bundle
