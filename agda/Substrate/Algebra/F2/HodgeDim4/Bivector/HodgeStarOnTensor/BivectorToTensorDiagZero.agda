------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.BivectorToTensorDiagZero
--
-- Defines: bivector-to-tensor-diag-zero
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.BivectorToTensorDiagZero where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Cover
open import Substrate.Foundation.Vec
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



-- diag-zero is the UNIFORM case (every cell reduces to 𝟘 ≡ 𝟘), so
-- the polymorphic `4-refls` from CanonicalCover applies directly:
-- one polymorphic {x = 𝟘} unifies across all 4 positions.
bivector-to-tensor-diag-zero :
  (v : Bivector) →
  (i : Fin 4) →
  lookup (lookup (bivector-to-tensor v) i) i ≡ 𝟘
bivector-to-tensor-diag-zero (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) =
  fin-cover _ (n-refls 4)
