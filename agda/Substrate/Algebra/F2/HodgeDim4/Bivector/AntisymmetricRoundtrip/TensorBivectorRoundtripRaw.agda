------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip.TensorBivectorRoundtripRaw
--
-- Defines: tensor-bivector-roundtrip-raw
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip.TensorBivectorRoundtripRaw where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals
open import Substrate.Foundation.Vec
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
open import Substrate.Algebra.F2.HodgeDim4.Bivector.TensorProductBridge
open import Substrate.Category.TensorProduct
open import Substrate.Category.TensorProduct.AntisymmetricTensor
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip.EqFromLookupA



------------------------------------------------------------------------
-- N-1: tensor-bivector-roundtrip-raw — reverse round-trip with the
-- antisymmetry hypotheses as explicit arguments.
--
-- For any T : TensorProduct 4 4 satisfying symmetric +F diagonal-zero,
--   bivector-to-tensor (tensor-to-bivector T) ≡ T
--
-- Proof via double ≡-from-lookup at each (i, j) ∈ Fin 4 × Fin 4. The
-- 16 positions split into:
--   * 4 diagonal positions: LHS = 𝟘, RHS = T(i,i); use sym (dz i).
--   * 6 upper-triangular: LHS = T(i,j) by definition of tensor-to-
--     bivector and bivector-to-tensor; use refl.
--   * 6 lower-triangular: LHS = T(j,i) (the upper-triangular partner);
--     use symmetric T j i to bridge.
------------------------------------------------------------------------

tensor-bivector-roundtrip-raw :
  (T : TensorProduct 4 4) →
  ((i j : Fin 4) → lookup (lookup T i) j ≡ lookup (lookup T j) i) →
  ((i : Fin 4) → lookup (lookup T i) i ≡ 𝟘) →
  bivector-to-tensor (tensor-to-bivector T) ≡ T
tensor-bivector-roundtrip-raw T sym dz =
  ≡-from-lookup-A _ T (λ i →
    ≡-from-lookup-A _ (lookup T i) (λ j → entry-eq i j))
  where
    entry-eq : (i j : Fin 4) →
      lookup (lookup (bivector-to-tensor (tensor-to-bivector T)) i) j
        ≡ lookup (lookup T i) j
    -- Row 0: (𝟘 ∷ a ∷ b ∷ c ∷ [])  where a=T(0,1), b=T(0,2), c=T(0,3)
    entry-eq zero                            zero                            = sym (dz zero)
    entry-eq zero                            ₁                      = refl
    entry-eq zero                            ₂                = refl
    entry-eq zero                            ₃          = refl
    -- Row 1: (a ∷ 𝟘 ∷ d ∷ e ∷ [])  where d=T(1,2), e=T(1,3)
    entry-eq ₁                      zero                            = sym zero ₁
    entry-eq ₁                      ₁                      = sym (dz ₁)
    entry-eq ₁                      ₂                = refl
    entry-eq ₁                      ₃          = refl
    -- Row 2: (b ∷ d ∷ 𝟘 ∷ f ∷ [])  where f=T(2,3)
    entry-eq ₂                zero                            = sym zero ₂
    entry-eq ₂                ₁                      = sym ₁ ₂
    entry-eq ₂                ₂                = sym (dz ₂)
    entry-eq ₂                ₃          = refl
    -- Row 3: (c ∷ e ∷ f ∷ 𝟘 ∷ [])
    entry-eq ₃          zero                            = sym zero ₃
    entry-eq ₃          ₁                      = sym ₁ ₃
    entry-eq ₃          ₂                = sym ₂ ₃
    entry-eq ₃          ₃          = sym (dz ₃)
