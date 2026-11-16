------------------------------------------------------------------------
-- Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step1OnBasis
--
-- Defines: step1-on-basis
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.TokiPona.ModifierBilinear.WithBasisAction; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step1OnBasis where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.Vector
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



step1-on-basis :
  (b : Fin n → Fin n → SemVec m) (i j : Fin n) →
  apply (step1 b j) (basis i) ≡ b i j
step1-on-basis b i j = apply-linear-from-images-basis (λ k → b k j) i
