------------------------------------------------------------------------
-- Substrate.TokiPona.ModifierBilinear.WithBasisAction.BilinearModify
--
-- Defines: --, bilinear-modify
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.TokiPona.ModifierBilinear.WithBasisAction; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.ModifierBilinear.WithBasisAction.BilinearModify where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.Linear.CompL
open import Substrate.Algebra.F2.Linear.CompLAssoc
open import Substrate.Algebra.F2.Linear.CompLIdentityL
open import Substrate.Algebra.F2.Linear.CompLIdentityR
open import Substrate.Algebra.F2.Linear.IdL
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.Preserves
open import Substrate.Algebra.F2.Linear.FromImages
open import Substrate.TokiPona.SemanticSpace
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open Linear
open import Substrate.TokiPona.ModifierBilinear.WithBasisAction.Private
open import Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step1
open import Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step2



------------------------------------------------------------------------
-- 3. The bilinear map itself.
--
-- bilinear-modify v w = apply (step2 b v) w
-- = Σⱼ wⱼ · apply (step1 b j) v
-- = Σⱼ wⱼ · Σᵢ vᵢ · b(i, j)
-- = Σᵢⱼ vᵢ wⱼ b(i, j)
------------------------------------------------------------------------

bilinear-modify :
  (b : Fin n → Fin n → SemVec m) →
  SemVec n → SemVec n → SemVec m
bilinear-modify b v w = apply (step2 b v) w
