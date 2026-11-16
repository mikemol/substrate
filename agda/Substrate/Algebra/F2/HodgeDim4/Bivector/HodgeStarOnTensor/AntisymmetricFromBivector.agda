------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.AntisymmetricFromBivector
--
-- Defines: antisymmetric-from-bivector
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.AntisymmetricFromBivector where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals
open import Substrate.Foundation.Fin.Cover
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Product
open import Substrate.Groups.Coxeter.CanonicalCover
open import Substrate.Foundation.Eq
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
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.HodgeDim4.Bivector
open import Substrate.Algebra.F2.HodgeDim4.Bivector.TensorProductBridge
open import Substrate.Category.TensorProduct.AntisymmetricTensor
open import Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.BivectorToTensorSymmetric
open import Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.BivectorToTensorDiagZero



------------------------------------------------------------------------
-- N-2: antisymmetric-from-bivector — package the antisymmetry
-- witnesses into the subtype.
--
-- For any Bivector v, bivector-to-tensor v lives in the antisymmetric
-- subspace; this constructor surfaces that fact as an
-- AntisymmetricTensor 4.
------------------------------------------------------------------------

antisymmetric-from-bivector : Bivector → AntisymmetricTensor 4
antisymmetric-from-bivector v = record
  { tensor    = bivector-to-tensor v
  ; symmetric = bivector-to-tensor-symmetric v
  ; diag-zero = bivector-to-tensor-diag-zero v
  }
