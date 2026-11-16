------------------------------------------------------------------------
-- Substrate.Category.TensorProduct.BCInstances.BilinformEvalBCSquare
--
-- Defines: bilinform-eval-BCSquare
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.TensorProduct.BCInstances; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.TensorProduct.BCInstances.BilinformEvalBCSquare where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.F2.AbsorbL
open import Substrate.Algebra.F2.AbsorbR
open import Substrate.Algebra.F2.Assoc
open import Substrate.Algebra.F2.Comm
open import Substrate.Algebra.F2.Dec
open import Substrate.Algebra.F2.DistribLPlus
open import Substrate.Algebra.F2.DistribRPlus
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2Cases
open import Substrate.Algebra.F2.Idempotent
open import Substrate.Algebra.F2.IdentityL
open import Substrate.Algebra.F2.IdentityR
open import Substrate.Algebra.F2.InvOfOne
open import Substrate.Algebra.F2.OneNeqZero
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.Op2
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusComm
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityL
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.PlusInverseL
open import Substrate.Algebra.F2.PlusInverseR
open import Substrate.Algebra.F2.PlusSelfInverse
open import Substrate.Algebra.F2.ZeroNeqOne
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.SymBilinForm.BilinForm
open import Substrate.Algebra.F2.SymBilinForm.BilinearFormOf
open import Substrate.Algebra.F2.SymBilinForm.TensorProductView
open import Substrate.Category.TensorProduct
open import Substrate.Category.BeckChevalley
open import Substrate.Category.TensorProduct.BCInstances.VecPair
open import Substrate.Category.TensorProduct.BCInstances.PairVec
open import Substrate.Category.TensorProduct.BCInstances.EvalTensor
open import Substrate.Category.TensorProduct.BCInstances.EvalDirect



bilinform-eval-BCSquare :
  ∀ {n} (M : BilinForm n) →
  BCSquare {A = VecPair n}
           {B = TensorProduct n n}
           {C = VecPair n}
           {D = F₂}
           pair-vec
           (λ x → x)
           (eval-tensor M)
           (eval-direct M)
bilinform-eval-BCSquare M =
  factor-via-pair-BCSquare pair-vec (eval-tensor M) (eval-direct M)
    (λ { (v , w) → bilinear-form-of-via-tensor-agrees M v w })
