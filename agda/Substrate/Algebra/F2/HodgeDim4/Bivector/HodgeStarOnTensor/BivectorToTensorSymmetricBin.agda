------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.BivectorToTensorSymmetricBin
--
-- Defines: bivector-to-tensor-symmetric-bin
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.BivectorToTensorSymmetricBin where

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
open import Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.ToFin4




------------------------------------------------------------------------
-- N-1: bivector-to-tensor produces antisymmetric tensors.
--
-- Two structural witnesses: symmetric (T(i,j) = T(j,i)) and
-- diag-zero (T(i,i) = 𝟘). Both hold by construction of
-- bivector-to-tensor (the 4×4 matrix is hardcoded to be symmetric
-- with zero diagonal).
--
-- Proofs are case-by-case on (i, j): 16 refl positions for symmetric
-- (the symmetric matrix structure makes every lookup pair equal); 4
-- refl positions for diag-zero.
------------------------------------------------------------------------

-- Cayley enumeration collapsed via compositional cover from
-- Substrate.Foundation.Fin.Cover: the 16-case Fin 4 × Fin 4 table
-- IS the orbit of two fin4-cover applications composed via the
-- product structure (the atlas-of-charts view, per the user's
-- observation: the 4 blocks of 4 lines in any 4×4-cover are
-- screaming for the tensor decomposition). Refl tokens are nested
-- into 4-tuples-of-4-tuples matching the row structure; each refl's
-- {x} unifies independently with its position's predicate.
-- Binary fan-out dispatch: Fin 4 × Fin 4 = (Fin 2 × Fin 2) × (Fin 2 ×
-- Fin 2) = F₂⁴. The 16-cell Cayley reads as four nested binary
-- decisions via `fin-cover-2⁴`. Each `refl` literal carries its own
-- implicit {x} (heterogeneous cells per (i₁, i₂, j₁, j₂) bit pattern).
bivector-to-tensor-symmetric-bin :
  (v : Bivector) →
  (i₁ i₂ j₁ j₂ : Fin 2) →
  lookup (lookup (bivector-to-tensor v) (to-fin4 i₁ i₂)) (to-fin4 j₁ j₂)
    ≡ lookup (lookup (bivector-to-tensor v) (to-fin4 j₁ j₂)) (to-fin4 i₁ i₂)
bivector-to-tensor-symmetric-bin (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) =
  fin-cover-2⁴ _
    ((((refl , refl) , (refl , refl)) , ((refl , refl) , (refl , refl))) ,
     (((refl , refl) , (refl , refl)) , ((refl , refl) , (refl , refl))))
