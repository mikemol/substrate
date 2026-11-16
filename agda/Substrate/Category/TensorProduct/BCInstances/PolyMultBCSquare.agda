------------------------------------------------------------------------
-- Substrate.Category.TensorProduct.BCInstances.PolyMultBCSquare
--
-- Defines: poly-mult-BCSquare
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.TensorProduct.BCInstances; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.TensorProduct.BCInstances.PolyMultBCSquare where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
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
open import Substrate.Algebra.F2.Polynomial
open import Substrate.Algebra.F2.Polynomial.TensorProductView
open import Substrate.Category.TensorProduct
open import Substrate.Category.BeckChevalley
open import Substrate.Category.TensorProduct.BCInstances.PolyPair
open import Substrate.Category.TensorProduct.BCInstances.PairPoly
open import Substrate.Category.TensorProduct.BCInstances.AntiDiagPoly
open import Substrate.Category.TensorProduct.BCInstances.MultPoly



poly-mult-BCSquare :
  ∀ {n m} →
  BCSquare {A = PolyPair n m}
           {B = TensorProduct n m}
           {C = PolyPair n m}
           {D = Polynomial (n ℕ+ m)}
           pair-poly
           (λ x → x)
           anti-diag-poly
           mult-poly
poly-mult-BCSquare =
  factor-via-pair-BCSquare pair-poly anti-diag-poly mult-poly
    (λ { (v , w) → *P-via-tensor-eq v w })
