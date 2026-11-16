------------------------------------------------------------------------
-- Substrate.TokiPona.ModifierBilinear.WithBasisAction.BilinearModifyOnBasis
--
-- Defines: bilinear-modify-on-basis
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.TokiPona.ModifierBilinear.WithBasisAction; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.ModifierBilinear.WithBasisAction.BilinearModifyOnBasis where

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
open import Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step1OnBasis
open import Substrate.TokiPona.ModifierBilinear.WithBasisAction.Step2
open import Substrate.TokiPona.ModifierBilinear.WithBasisAction.BilinearModify



------------------------------------------------------------------------
-- 4. Universal-property witness: bilinear-modify on basis pairs.
--
-- bilinear-modify b (basis i) (basis j) ≡ b i j
--
-- This is the defining property: the bilinear map agrees with the
-- basis-pair action on basis pairs. Discharged by applying the
-- universal property of linear-from-images at the OUTER step (step2)
-- and then at the INNER step (step1).
------------------------------------------------------------------------

bilinear-modify-on-basis :
  (b : Fin n → Fin n → SemVec m) (i j : Fin n) →
  bilinear-modify b (basis i) (basis j) ≡ b i j
bilinear-modify-on-basis b i j =
  -- bilinear-modify b (basis i) (basis j)
  --   = apply (step2 b (basis i)) (basis j)
  --   = apply (linear-from-images (λ k → apply (step1 b k) (basis i))) (basis j)
  -- By apply-linear-from-images-basis (outer):
  --   = (λ k → apply (step1 b k) (basis i)) j
  --   = apply (step1 b j) (basis i)
  -- By apply-linear-from-images-basis (inner) i.e. step1-on-basis:
  --   = b i j
  trans-step
  where
    open import Substrate.Foundation.Eq.Trans
    outer :
      apply (linear-from-images (λ k → apply (step1 b k) (basis i)))
            (basis j)
        ≡ apply (step1 b j) (basis i)
    outer = apply-linear-from-images-basis
              (λ k → apply (step1 b k) (basis i)) j
    inner : apply (step1 b j) (basis i) ≡ b i j
    inner = step1-on-basis b i j
    trans-step : bilinear-modify b (basis i) (basis j) ≡ b i j
    trans-step = trans outer inner
