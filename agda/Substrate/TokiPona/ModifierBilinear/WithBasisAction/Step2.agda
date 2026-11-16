------------------------------------------------------------------------
-- Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step2
--
-- Defines: step2
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.TokiPona.ModifierBilinear.WithBasisAction; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step2 where

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



------------------------------------------------------------------------
-- 2. Step 2: extend over j by FreeLinearization again.
--
-- For fixed v : SemVec n, the function `j → apply (step1 b j) v`
-- is in Fin n → SemVec m; lift it through linear-from-images to
-- obtain a Linear n m. Apply to w to complete the bilinear map.
------------------------------------------------------------------------

step2 :
  (b : Fin n → Fin n → SemVec m) →
  SemVec n →
  Linear n m
step2 b v = linear-from-images (λ j → apply (step1 b j) v)
