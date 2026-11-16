------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.BivectorToTensorSymmetric
--
-- Defines: bivector-to-tensor-symmetric
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.BivectorToTensorSymmetric where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals
open import Substrate.Foundation.Fin.Cover
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Product
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
open import Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.BivectorToTensorSymmetricBin



-- Original Fin 4 × Fin 4 surface, derived by composing the binary
-- dispatch with the bit-decomposition of each Fin 4 index.
bivector-to-tensor-symmetric :
  (v : Bivector) →
  (i j : Fin 4) →
  lookup (lookup (bivector-to-tensor v) i) j
    ≡ lookup (lookup (bivector-to-tensor v) j) i
bivector-to-tensor-symmetric v i j =
  fin4-fin4-route i j
  where
    -- Bit-decompose i, j ∈ Fin 4 to (Fin 2 × Fin 2) × (Fin 2 × Fin 2)
    -- and dispatch via the binary cover.
    fin4-fin4-route : (i j : Fin 4) →
      lookup (lookup (bivector-to-tensor v) i) j
        ≡ lookup (lookup (bivector-to-tensor v) j) i
    fin4-fin4-route zero                     zero                     = bivector-to-tensor-symmetric-bin v zero zero zero zero
    fin4-fin4-route zero                     ₁               = bivector-to-tensor-symmetric-bin v zero zero zero ₁
    fin4-fin4-route zero                     ₂         = bivector-to-tensor-symmetric-bin v zero zero ₁ zero
    fin4-fin4-route zero                     ₃   = bivector-to-tensor-symmetric-bin v zero zero ₁ ₁
    fin4-fin4-route ₁               zero                     = bivector-to-tensor-symmetric-bin v zero ₁ zero zero
    fin4-fin4-route ₁               ₁               = bivector-to-tensor-symmetric-bin v zero ₁ zero ₁
    fin4-fin4-route ₁               ₂         = bivector-to-tensor-symmetric-bin v zero ₁ ₁ zero
    fin4-fin4-route ₁               ₃   = bivector-to-tensor-symmetric-bin v zero ₁ ₁ ₁
    fin4-fin4-route ₂         zero                     = bivector-to-tensor-symmetric-bin v ₁ zero zero zero
    fin4-fin4-route ₂         ₁               = bivector-to-tensor-symmetric-bin v ₁ zero zero ₁
    fin4-fin4-route ₂         ₂         = bivector-to-tensor-symmetric-bin v ₁ zero ₁ zero
    fin4-fin4-route ₂         ₃   = bivector-to-tensor-symmetric-bin v ₁ zero ₁ ₁
    fin4-fin4-route ₃   zero                     = bivector-to-tensor-symmetric-bin v ₁ ₁ zero zero
    fin4-fin4-route ₃   ₁               = bivector-to-tensor-symmetric-bin v ₁ ₁ zero ₁
    fin4-fin4-route ₃   ₂         = bivector-to-tensor-symmetric-bin v ₁ ₁ ₁ zero
    fin4-fin4-route ₃   ₃   = bivector-to-tensor-symmetric-bin v ₁ ₁ ₁ ₁
