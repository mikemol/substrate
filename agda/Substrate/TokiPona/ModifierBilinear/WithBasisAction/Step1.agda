------------------------------------------------------------------------
-- Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step1
--
-- Defines: step1
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.TokiPona.ModifierBilinear.WithBasisAction; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step1 where

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



------------------------------------------------------------------------
-- 1. Step 1: fix-j linear extension.
--
-- For each column j : Fin n, the slice `b · j` lifts to a Linear
-- n m via the substrate's existing free-linear universal property.
-- Result: apply (step1 b j) (basis i) ≡ b i j.
------------------------------------------------------------------------

step1 :
  (b : Fin n → Fin n → SemVec m) →
  Fin n →
  Linear n m
step1 b j = linear-from-images (λ i → b i j)
