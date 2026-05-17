------------------------------------------------------------------------
-- Substrate.Groups.S4-Composed
--
-- S₄ = V₄ ⋊ S₃, the symmetric group on 4 elements constructed
-- compositionally from atoms via the Coxeter framework:
--
--   Atoms:        Z/2 (Z2-Coxeter)            -- involution
--                 Z/3 (Z3-Coxeter)            -- 3-cycle
--   Combinators:  SemidirectProductGroup       -- N ⋊_φ H
--   Actions:      Z/2 → Aut(Z/3)              -- inversion (S₃)
--                 S₃ → Aut(V₄)                -- AGL/dihedral (S₄)
--   Adapters:     CoxeterGroupAdapter          -- Coxeter → stdlib Group
--
-- This file: instantiate SemidirectProductGroup with G_N = V₄-Group
-- and G_H = S₃-Group (where S₃ is itself a SP composition). The
-- resulting carrier is V₄ × (Word Z₃.Gen × Word Z₂.Gen). Algebra is
-- inherited from the SP combinator.
--
-- Naming: S4-Composed (not S4) to coexist with the existing
-- Substrate.Groups.S4 (= Symmetric Axis). A subsequent slice will
-- prove the iso S4-Composed ≅ Substrate.Groups.S4 and migrate
-- consumers.
--
-- Per [[feedback-v4-typeclass-architecture]]: V₄ ⊳ S₄ is now
-- STRUCTURAL — V₄ is the N in N ⋊ H, so its normality in S₄ is by
-- construction. The previously-postulated V₄-normal theorem becomes
-- a projection of the SP combinator's data, replacing the postulate
-- in Substrate.Groups.V4-Embedding.Normality once consumers are
-- migrated.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Composed where

import Substrate.Groups.V4 as V4
import Substrate.Groups.S3 as S₃
import Substrate.Groups.Actions.S3-on-V4 as φ
open import Algebra.Bundles using (Group)
open import Level using (0ℓ)

------------------------------------------------------------------------
-- 1. Open the SemidirectProductGroup combinator with V₄ as N and S₃ as H.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.SemidirectProductGroup
  V4.V₄-Group   -- N (normal subgroup)
  S₃.S₃-Group   -- H (acting group)

------------------------------------------------------------------------
-- 2. Plug in the AGL action and re-export everything.
--
-- Explicit-implicit binding (per S3.agda lesson) to avoid the
-- normalize-unification block in Agda's metavariable resolution.
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
-- 3. Top-level alias for the Group bundle.
------------------------------------------------------------------------

S₄-Group : Group 0ℓ 0ℓ
S₄-Group = Group-bundle
